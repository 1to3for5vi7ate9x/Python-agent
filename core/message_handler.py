from typing import Dict, Optional
import os
from loguru import logger
from .generation import GenerationManager
from .marketing_manager import MarketingManager

# Get environment configurations
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'
ENABLE_REPLIES = os.getenv('ENABLE_REPLIES', 'true').lower() == 'true'

class MessageHandler:
    def __init__(self, prompt_file: str, character: Dict):
        self.prompt_file = prompt_file
        self.prompt_content = self.load_prompt()
        self.character = character
        model_provider = character.get("modelProvider", "ollama")
        base_url = character.get("baseUrl")  # Optional, only for Ollama
        default_model = character.get("model")
        api_key = os.getenv("GEMINI_API_KEY") if model_provider == "gemini" else None

        self.generation_manager = GenerationManager(
            model_provider=model_provider,
            base_url=base_url,
            default_model=default_model,
            api_key=api_key,
        )
        self.marketing_manager = MarketingManager(self.prompt_content, character, self.generation_manager)
        logger.info(f"Initialized MessageHandler using prompt file: {self.prompt_file}")

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
            prompt = f"""
{self.prompt_content}

Message: '{message}'

Based on the provided context, is this message relevant and should receive a reply? Answer with 'yes' or 'no'.
"""
            response = await self.generation_manager.generate_text(prompt, personality="")
            if response.startswith("[INTERNAL]"):
                logger.error(f"Error checking relevance: {response}")
                return False

            normalized_response = response.strip().lower()
            logger.info(f"The message '{message}' relevance is {normalized_response}")
            return "yes" in normalized_response

        except Exception as e:
            logger.error(f"Error in _is_relevant: {e}")
            return False

    async def _should_reply(self, message: str) -> bool:
        """Determine if we should reply to this message."""
        if not ENABLE_REPLIES:
            return False

        try:
            if not await self._is_relevant(message):
                if ENABLE_DEBUG_LOGS:
                    logger.debug(f"Message is not relevant, skipping")
                return False

            if ENABLE_DEBUG_LOGS:
                logger.debug("Message is relevant")
            return True

        except Exception as e:
            logger.error(f"Error in _should_reply: {e}")
            return False

    async def _generate_reply(self, message: str) -> Optional[str]:
        """Generate a reply using the LLM based on the prompt."""
        if not ENABLE_REPLIES:
            return None

        try:
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Generating reply for message: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")

            prompt = f"""
{self.prompt_content}

Message: '{message}'

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

    async def handle_message(self, message: str) -> Optional[str]:
        """Main message handling logic."""
        try:
            character_name = self.character.get("name", "unknown")
            if ENABLE_DEBUG_LOGS:
                logger.info(f"[{character_name}] Processing message: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")

            # Record message for marketing manager
            self.marketing_manager.record_message()

            # Model selection logic
            model_provider = self.character.get("modelProvider", "ollama")  # Default
            if message.startswith("!ollama"):
                model_provider = "ollama"
                message = message[len("!ollama"):].strip()  # Remove the command
            elif message.startswith("!gemini"):
                model_provider = "gemini"
                message = message[len("!gemini"):].strip()  # Remove the command

            # Re-initialize GenerationManager if model provider changed
            if model_provider != self.generation_manager.model_provider:
                base_url = self.character.get("baseUrl")  # Optional, only for Ollama
                default_model = self.character.get("model")
                api_key = os.getenv("GEMINI_API_KEY") if model_provider == "gemini" else None

                self.generation_manager = GenerationManager(
                    model_provider=model_provider,
                    base_url=base_url,
                    default_model=default_model,
                    api_key=api_key,
                )
                logger.info(f"Switched to model provider: {model_provider}")

            # First check if we should send a marketing message
            marketing_message = await self.marketing_manager.generate_marketing_message()
            if marketing_message:
                if ENABLE_DEBUG_LOGS:
                    logger.info(f"[{character_name}] Sending marketing message ({len(marketing_message)} chars)")
                return marketing_message

            # If not sending marketing, check if we should reply to this message
            if not await self._should_reply(message):
                if ENABLE_DEBUG_LOGS:
                    logger.debug(f"[{character_name}] Message doesn't meet reply criteria")
                return None

            # Generate and return reply
            reply = await self._generate_reply(message)
            if reply and ENABLE_DEBUG_LOGS:
                logger.info(f"[{character_name}] Sending reply ({len(reply)} chars)")
            return reply

        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            return None
