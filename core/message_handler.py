from typing import Dict, Optional
from loguru import logger
from .generation import GenerationManager
from .marketing_manager import MarketingManager

class MessageHandler:
    def __init__(self, character: Dict, generation_manager: GenerationManager):
        self.character = character
        self.generation_manager = generation_manager
        self.marketing_manager = MarketingManager(character, generation_manager)
        
    def _should_reply(self, message: str) -> bool:
        """Determine if we should reply to this message based on character rules"""
        try:
            # Get reply rules from character config
            rules = self.character.get("reply_rules", {})
            
            # Check keywords to ignore
            ignore_keywords = rules.get("ignore_keywords", [])
            if any(keyword.lower() in message.lower() for keyword in ignore_keywords):
                logger.debug(f"Message contains ignore keyword, skipping")
                return False
                
            # Check required keywords (if any must be present)
            required_keywords = rules.get("required_keywords", [])
            if required_keywords and not any(keyword.lower() in message.lower() for keyword in required_keywords):
                logger.debug(f"Message doesn't contain any required keywords, skipping")
                return False
                
            # Check message length limits
            min_length = rules.get("min_length", 0)
            max_length = rules.get("max_length", float('inf'))
            if not (min_length <= len(message) <= max_length):
                logger.debug(f"Message length ({len(message)}) outside bounds [{min_length}, {max_length}], skipping")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in should_reply: {e}")
            return False
            
    async def _generate_reply(self, message: str) -> Optional[str]:
        """Generate a reply using the LLM based on character template"""
        try:
            # Get reply template from character config
            template = self.character.get("reply_template", "")
            if not template:
                logger.error("No reply template found in character config")
                return None
                
            # Replace placeholders in template
            context = template.replace("{message}", message)
            context = context.replace("{character_name}", self.character.get("name", ""))
            context = context.replace("{personality}", self.character.get("personality", ""))
            
            # Generate response
            response = await self.generation_manager.generate_text(context)
            if response and not response.startswith("Error:"):
                return response
                
            logger.error(f"Failed to generate response: {response}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None
            
    async def handle_message(self, message: str) -> Optional[str]:
        """Main message handling logic"""
        try:
            # Record message for marketing manager
            self.marketing_manager.record_message()
            
            # First check if we should send a marketing message
            marketing_message = await self.marketing_manager.generate_marketing_message()
            if marketing_message:
                logger.info("Sending marketing message")
                return marketing_message
                
            # If not sending marketing, check if we should reply to this message
            if not self._should_reply(message):
                logger.debug("Message doesn't meet reply criteria")
                return None
                
            # Generate and return reply
            return await self._generate_reply(message)
            
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            return None
