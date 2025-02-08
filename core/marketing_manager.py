from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from loguru import logger
from .generation import GenerationManager

# Get environment configurations
ENABLE_MARKETING = os.getenv('ENABLE_MARKETING', 'true').lower() == 'true'
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'

class MarketingManager:
    def __init__(self, character: Dict, generation_manager: GenerationManager):
        self.character = character
        self.generation_manager = generation_manager
        self.message_count = 0
        self.last_marketing_time: Optional[datetime] = None
        self.marketing_cooldown = timedelta(hours=6)
        self.message_threshold = 5  # Send marketing message after this many messages
        self.time_threshold = timedelta(hours=6)  # Or after this much time
        self.start_time = datetime.now()
        
        logger.info(f"Initialized MarketingManager for character '{character.get('name', 'unknown')}'")
        logger.info(f"Settings: message_threshold={self.message_threshold}, time_threshold={self.time_threshold.total_seconds()/3600}h, cooldown={self.marketing_cooldown.total_seconds()/3600}h")
        
    def record_message(self) -> None:
        """Record a new message in the group"""
        if not ENABLE_MARKETING:
            return
            
        self.message_count += 1
        
        if ENABLE_DEBUG_LOGS:
            time_since_start = datetime.now() - self.start_time
            time_since_last = datetime.now() - (self.last_marketing_time or self.start_time)
            logger.debug(f"Message recorded: count={self.message_count}, time_since_start={time_since_start.total_seconds()/3600:.1f}h, time_since_last_marketing={time_since_last.total_seconds()/3600:.1f}h")
        
    async def should_send_marketing(self) -> bool:
        """Check if we should send a marketing message based on conditions"""
        if not ENABLE_MARKETING:
            return False
            
        current_time = datetime.now()
        
        # If we sent a marketing message recently, don't send another
        if self.last_marketing_time:
            time_since_last = current_time - self.last_marketing_time
            if time_since_last < self.marketing_cooldown:
                if ENABLE_DEBUG_LOGS:
                    logger.debug(f"Marketing on cooldown: {(self.marketing_cooldown - time_since_last).total_seconds()/3600:.1f}h remaining")
                return False
            
        # Check message count condition
        if self.message_count >= self.message_threshold:
            if ENABLE_DEBUG_LOGS:
                logger.info(f"Marketing trigger: message threshold reached ({self.message_count}/{self.message_threshold} messages)")
            return True
            
        # Check time elapsed condition
        time_elapsed = current_time - self.start_time
        if time_elapsed >= self.time_threshold:
            if ENABLE_DEBUG_LOGS:
                logger.info(f"Marketing trigger: time threshold reached ({time_elapsed.total_seconds()/3600:.1f}/{self.time_threshold.total_seconds()/3600:.1f} hours)")
            return True
            
        # Log current status if not triggering
        if ENABLE_DEBUG_LOGS:
            logger.debug(f"Marketing status: messages={self.message_count}/{self.message_threshold}, time={time_elapsed.total_seconds()/3600:.1f}/{self.time_threshold.total_seconds()/3600:.1f}h")
        return False
        
    async def generate_marketing_message(self) -> Optional[str]:
        """Generate and return a marketing message"""
        if not ENABLE_MARKETING:
            return None
            
        try:
            character_name = self.character.get("name", "unknown")
            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Checking marketing conditions for {character_name}")
            
            if not await self.should_send_marketing():
                return None
                
            # Get marketing template from character config
            template = self.character.get("marketing_template", "")
            if not template:
                logger.error(f"No marketing template found for character {character_name}")
                return None
                
            if ENABLE_DEBUG_LOGS:
                logger.info(f"Generating marketing message for {character_name}")
                
            # Generate message using LLM
            message = await self.generation_manager.generate_marketing_message(
                template=template,
                character_name=character_name
            )
            
            if message and not message.startswith("[INTERNAL]"):
                current_time = datetime.now()
                self.last_marketing_time = current_time
                prev_count = self.message_count
                prev_time = self.start_time
                
                self.message_count = 0  # Reset message count
                self.start_time = current_time  # Reset timer
                
                if ENABLE_DEBUG_LOGS:
                    logger.info(f"Marketing message generated ({len(message)} chars)")
                    logger.info(f"Stats reset - Messages: {prev_count}→0, Timer: {(current_time - prev_time).total_seconds()/3600:.1f}h→0h")
                return message
            
            if ENABLE_DEBUG_LOGS:
                logger.error(f"Failed to generate marketing message: {message}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating marketing message: {e}")
            return None
