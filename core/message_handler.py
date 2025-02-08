from typing import Dict, Optional
import os
from loguru import logger
from .generation import GenerationManager
from .marketing_manager import MarketingManager

# Get environment configurations
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'
ENABLE_REPLIES = os.getenv('ENABLE_REPLIES', 'true').lower() == 'true'

class MessageHandler:
    def __init__(self, character: Dict, generation_manager: GenerationManager):
        self.character = character
        self.generation_manager = generation_manager
        self.marketing_manager = MarketingManager(character, generation_manager)
        logger.info(f"Initialized MessageHandler for character '{character.get('name', 'unknown')}'")
        
    def _should_reply(self, message: str) -> bool:
        """Determine if we should reply to this message based on character rules"""
        if not ENABLE_REPLIES:
            return False
            
        try:
            # Get rules from character config
            rules = self.character.get("rules", {}).get("message", {})
            blocked_terms = self.character.get("rules", {}).get("blocked_terms", [])
            
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Checking message rules for: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")
            
            # Check blocked terms
            if blocked_terms:
                for term in blocked_terms:
                    if term.lower() in message.lower():
                        if ENABLE_DEBUG_LOGS:
                            logger.debug(f"Message contains blocked term '{term}', skipping")
                        return False
                
            # Check message length limits
            min_length = rules.get("min_length", 0)
            max_length = rules.get("max_length", float('inf'))
            if not (min_length <= len(message) <= max_length):
                if ENABLE_DEBUG_LOGS:
                    logger.debug(f"Message length ({len(message)} chars) outside bounds [{min_length}, {max_length}], skipping")
                return False
            
            if ENABLE_DEBUG_LOGS:
                logger.debug("Message passed all rules")
            return True
            
        except Exception as e:
            logger.error(f"Error in should_reply: {e}")
            return False
            
    async def _generate_reply(self, message: str) -> Optional[str]:
        """Generate a reply using the LLM based on character template"""
        if not ENABLE_REPLIES:
            return None
            
        try:
            character_name = self.character.get("name", "unknown")
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Generating reply for message: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")
            
            # Get reply template and personality
            template = self.character.get("templates", {}).get("reply", "")
            personality = self.character.get("personality", {})
            
            if not template:
                if ENABLE_DEBUG_LOGS:
                    logger.error(f"No reply template found for character {character_name}")
                return None
                
            # Replace placeholders in template
            context = template.replace("{message}", message)
            context = context.replace("{traits}", personality.get("traits", ""))
            context = context.replace("{interests}", personality.get("interests", ""))
            
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Generated context of {len(context)} chars for LLM")
            
            # Generate response
            response = await self.generation_manager.generate_text(context)
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
        """Main message handling logic"""
        try:
            character_name = self.character.get("name", "unknown")
            if ENABLE_DEBUG_LOGS:
                logger.info(f"[{character_name}] Processing message: '{message[:50]}{'...' if len(message) > 50 else ''}' ({len(message)} chars)")
            
            # Record message for marketing manager
            self.marketing_manager.record_message()
            
            # First check if we should send a marketing message
            marketing_message = await self.marketing_manager.generate_marketing_message()
            if marketing_message:
                if ENABLE_DEBUG_LOGS:
                    logger.info(f"[{character_name}] Sending marketing message ({len(marketing_message)} chars)")
                return marketing_message
                
            # If not sending marketing, check if we should reply to this message
            if not self._should_reply(message):
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
