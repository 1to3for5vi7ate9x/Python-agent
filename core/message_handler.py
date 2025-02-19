from typing import Dict, Optional
import os
from loguru import logger
from .generation import GenerationManager
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Get environment configurations
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'
load_dotenv(override=True)
MIN_MESSAGES = int(os.getenv('MIN_MESSAGES'))
MIN_TIME = int(os.getenv('MIN_TIME'))

class MessageHandler:
    def __init__(self, prompt_file: str, character: Dict):
        self.prompt_file = prompt_file
        self.min_messages = MIN_MESSAGES
        self.min_time = MIN_TIME
        self.minus_time = int(os.getenv('MINUS_TIME', '0'))  # Default to 0 if not set
        self.prompt_content = self.load_prompt()
        self.character = character
        ollama_model = os.getenv("OLLAMA_MODEL")
        model_provider = os.getenv("MODEL_PROVIDER", "ollama")
        base_url = character.get("baseUrl")  # Optional, only for Ollama
        default_model = ollama_model

        self.generation_manager = GenerationManager(
            model_provider=model_provider,
            base_url=base_url,
            default_model=default_model,
        )
        logger.info(f"Initialized MessageHandler using prompt file: {self.prompt_file}")

        # Channel-specific state: {channel_id: {last_message_time: timestamp, message_count: int}}
        self.channel_state = {}

    def load_prompt(self) -> str:
        """Load the content of the prompt file."""
        try:
            with open(self.prompt_file, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt file: {e}")
            return ""

    async def _is_relevant(self, message: str) -> bool:
        """Determine if the message is relevant based on the prompt."""
        try:
            # Use the entire conversation history for context
            prompt = f"""
{self.prompt_content}

Conversation History:
{message}

Based on the conversation history, is the latest message relevant and should the bot respond? Answer with 'yes' or 'no'.
"""
            response = await self.generation_manager.generate_text(prompt, personality="")
            if response.startswith("[INTERNAL]"):
                logger.error(f"Error checking relevance: {response}")
                return False

            normalized_response = response.strip().lower()
            try:
                # Attempt to extract the last message, handling potential errors
                last_message = message.split('\\n')[-1].split('User: ')[-1]
            except (IndexError, ValueError):
                last_message = message  # Fallback to the entire history if extraction fails
            logger.info(f"The message '{last_message}' relevance is {normalized_response}")
            return "yes" in normalized_response

        except Exception as e:
            logger.error(f"Error in _is_relevant: {e}")
            return False

    async def _should_reply(self, channel_id: str, message: str) -> bool:
        """Determine if we should reply to this message."""

        channel_id = str(channel_id)

        # Initialize channel state if not present
        if channel_id not in self.channel_state:
            self.channel_state[channel_id] = {"last_message_time": None, "message_count": 0}

        state = self.channel_state[channel_id]

        # Check message count
        if state["message_count"] < self.min_messages:
            remaining_messages = max(0, self.min_messages - state["message_count"])  # Ensure non-negative
            logger.info(f"Message count ({state['message_count']}) below threshold ({self.min_messages}) for channel {channel_id}. Remaining messages: {remaining_messages}")
            state["message_count"] += 1
            return False

        # Check time elapsed
        if state["last_message_time"]:
            time_elapsed = datetime.utcnow() - state["last_message_time"]
            time_threshold = timedelta(minutes=self.min_time)
            if time_elapsed < time_threshold:
                logger.info(f"Time elapsed ({time_elapsed}) below threshold ({time_threshold}) for channel {channel_id}")
                # Reduce remaining waiting time
                state["last_message_time"] -= timedelta(seconds=self.minus_time)
                logger.info(f"Reduced remaining waiting time by {self.minus_time} seconds for channel {channel_id}")
                state["message_count"] += 1
                return False

        if not await self._is_relevant(message):
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Message is not relevant, skipping")
            return False

        if ENABLE_DEBUG_LOGS:
            logger.debug("Message is relevant")

        return True

    async def _generate_reply(self, message: str) -> Optional[str]:
        """Generate a reply using the LLM based on the prompt."""

        try:
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Generating reply for message: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")

            prompt = f"""
{self.prompt_content}

{message}

Reply:"""

            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Generated context of {len(prompt)} chars for LLM")

            response = await self.generation_manager.generate_text(prompt, personality="")
            if response and not response.startswith("[INTERNAL]"):
                if ENABLE_DEBUG_LOGS:
                    logger.info(f"Generated reply of {len(response)} chars")
                return response

            if ENABLE_DEBUG_LOGS:
                logger.error(f"Failed to generate response: {response}")
            return None

        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None

    async def handle_message(self, message_object, history: str) -> Optional[str]:
        """Main message handling logic."""
        try:
            load_dotenv(override=True)  # Reload environment variables
            character_name = self.character.get("name", "unknown")
            if ENABLE_DEBUG_LOGS:
                logger.info(f"[{character_name}] Processing message: '{history[:50]}{'...' if len(history) > 50 else ''}' ({len(history)} chars)")

            # Handle different message object types (Discord and Telegram)
            if hasattr(message_object, 'channel') and hasattr(message_object.channel, 'id'):
                channel_id = str(message_object.channel.id)  # Discord
            elif hasattr(message_object, 'chat_id'):
                channel_id = str(message_object.chat_id)  # Telegram
            else:
                logger.error("Unsupported message object type")
                return None

            message = history

            # Model selection logic (This part might need adjustments depending on how commands are handled)
            model_provider = os.getenv("MODEL_PROVIDER", "ollama")
            if message.startswith("!ollama"):  # Check if this logic is still needed
                model_provider = "ollama"
                message = message[len("!ollama"):].strip()  # Remove the command

            # Re-initialize GenerationManager if model provider changed
            if model_provider != self.generation_manager.model_provider:
                base_url = self.character.get("baseUrl")  # Optional, only for Ollama
                default_model = os.getenv("OLLAMA_MODEL")
                self.generation_manager = GenerationManager(
                    model_provider=model_provider,
                    base_url=base_url,
                    default_model=default_model,
                )
                logger.info(f"Switched to model provider: {model_provider}")


            # Check if we should reply to this message
            if not await self._should_reply(channel_id, message):
                if ENABLE_DEBUG_LOGS:
                    logger.debug(f"[{character_name}] Message doesn't meet reply criteria")
                return None

            # Generate reply
            reply = await self._generate_reply(message)
            if reply:
                logger.info(f"[{character_name}] Sending reply ({len(reply)} chars)")
                # Reset message count and update last message time
                self.channel_state[channel_id] = {"last_message_time": datetime.utcnow(), "message_count": 0}
                return reply

            return None  # No reply generated

        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            return None
