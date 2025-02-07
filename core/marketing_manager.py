from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from .generation import GenerationManager

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
        
    def record_message(self) -> None:
        """Record a new message in the group"""
        self.message_count += 1
        
    async def should_send_marketing(self) -> bool:
        """Check if we should send a marketing message based on conditions"""
        # If we sent a marketing message recently, don't send another
        if self.last_marketing_time and datetime.now() - self.last_marketing_time < self.marketing_cooldown:
            return False
            
        # Check message count condition
        if self.message_count >= self.message_threshold:
            logger.info(f"Marketing trigger: message threshold reached ({self.message_count} messages)")
            return True
            
        # Check time elapsed condition
        time_elapsed = datetime.now() - self.start_time
        if time_elapsed >= self.time_threshold:
            logger.info(f"Marketing trigger: time threshold reached ({time_elapsed.total_seconds()/3600:.1f} hours)")
            return True
            
        return False
        
    async def generate_marketing_message(self) -> Optional[str]:
        """Generate and return a marketing message"""
        try:
            if not await self.should_send_marketing():
                return None
                
            # Get marketing template from character config
            template = self.character.get("marketing_template", "")
            if not template:
                logger.error("No marketing template found in character config")
                return None
                
            # Generate message using LLM
            message = await self.generation_manager.generate_marketing_message(
                template=template,
                character_name=self.character.get("name", "")
            )
            
            if message and not message.startswith("Error:"):
                self.last_marketing_time = datetime.now()
                self.message_count = 0  # Reset message count
                self.start_time = datetime.now()  # Reset timer
                logger.info("Marketing message generated and timer reset")
                return message
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating marketing message: {e}")
            return None
