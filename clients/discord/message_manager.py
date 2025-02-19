import discord
from loguru import logger
from core.message_handler import MessageHandler
import asyncio
import os
from dotenv import load_dotenv
from core.generation import GenerationManager
import time
from datetime import datetime, timedelta
from typing import Optional, Dict


class DiscordMessageManager:
    def __init__(self, runtime: dict):
        self.client = None
        self.conversations = {}  # Store conversation history: {user_id: [messages]}
        self.prompt_file = runtime["prompt_file"]
        self.min_messages = int(os.getenv('MIN_MESSAGES'))
        self.min_time = int(os.getenv('MIN_TIME'))
        self.minus_time = int(os.getenv('MINUS_TIME', '0'))  # Default to 0 if not set
        self.prompt_content = self.load_prompt()
        ollama_model = os.getenv("OLLAMA_MODEL")
        model_provider = os.getenv("MODEL_PROVIDER", "ollama")
        base_url = os.getenv("OLLAMA_BASE_URL")  # Optional, only for Ollama
        default_model = ollama_model

        self.generation_manager = GenerationManager(
            model_provider=model_provider,
            base_url=base_url,
            default_model=default_model,
        )
        logger.info(f"Initialized DiscordMessageManager using prompt file: {self.prompt_file}")

        # Channel-specific state: {channel_id: {last_message_time: timestamp, message_count: int, lock: asyncio.Lock}}
        self.channel_state = {}
        self.locks: Dict[str, asyncio.Lock] = {}  # Add a dictionary for locks

        # Set log level based on environment variable
        logger.remove()  # Remove default handler
        if os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true':
            logger.add(lambda msg: print(msg), level="DEBUG") # Add this to see all logs in console
        else:
            logger.add(lambda msg: print(msg), level="INFO")  # Add a handler with INFO level


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

        # Initialize channel state and lock if not present
        if channel_id not in self.channel_state:
            self.channel_state[channel_id] = {"last_message_time": None, "message_count": 0}
            self.locks[channel_id] = asyncio.Lock()  # Create a lock for the channel

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

        ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'
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
            ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'
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

    async def handle_message(self, message: discord.Message) -> None:
        try:
            # Check if the message is from an allowed channel
            # allowed_channel_ids = "1301754237411262485,1128867684130508875".split(",")  # From .env
            # Reload environment variables
            load_dotenv(override=True)

            # Check if the message is from an allowed channel
            allowed_channel_ids = os.getenv("DISCORD_ALLOWED_CHANNELS", "").split(",")
            if str(message.channel.id) not in allowed_channel_ids:
                return

            if message.author.bot:
                return

            # Get the user ID
            user_id = str(message.author.id)

            # Get the message content
            content = message.content
            if not content:
                return

            # Update conversation history
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            self.conversations[user_id].append(f"User: {content}")

            # Get conversation history
            conversation_history = "\\n".join(self.conversations[user_id])
            
            channel_id = str(message.channel.id)
            ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'

            # Acquire the lock for the channel
            if channel_id not in self.locks:
                self.locks[channel_id] = asyncio.Lock()
            logger.debug(f"[Discord] Attempting to acquire lock for channel {channel_id}")  # Added logging
            async with self.locks[channel_id]:
                logger.debug(f"[Discord] Acquired lock for channel {channel_id}")  # Added logging
                # Check if we should reply to this message
                if not await self._should_reply(channel_id, conversation_history):
                    return

                # Generate reply
                response = await self._generate_reply(conversation_history)
                if response and not response.startswith("Error:"):
                    self.conversations[user_id].append(f"Bot: {response}")  # Add bot response to history
                    await self._send_with_typing(message, response)
                    # Reset message count and update last message time
                    self.channel_state[channel_id] = {"last_message_time": datetime.utcnow(), "message_count": 0}
            logger.debug(f"[Discord] Releasing lock for channel {channel_id}")  # Added logging

        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")

    async def _send_with_typing(self, message: discord.Message, response: str) -> None:
        """Simulate typing and send a message."""
        async with message.channel.typing():
            await asyncio.sleep(len(response) * 0.05)  # Simulate typing speed
            await message.channel.send(response)
