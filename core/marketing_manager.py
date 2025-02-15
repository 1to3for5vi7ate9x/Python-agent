from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from loguru import logger
from .generation import GenerationManager

# Get environment configurations
ENABLE_MARKETING = os.getenv('ENABLE_MARKETING', 'true').lower() == 'true'
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'

# Marketing settings with environment variable overrides
MARKETING_MESSAGE_THRESHOLD = int(os.getenv('MARKETING_MESSAGE_THRESHOLD', '5'))
MARKETING_TIME_THRESHOLD_HOURS = float(os.getenv('MARKETING_TIME_THRESHOLD_HOURS', '6.0'))
MARKETING_COOLDOWN_HOURS = float(os.getenv('MARKETING_COOLDOWN_HOURS', '6.0'))
MARKETING_ACTIVITY_THRESHOLD = int(os.getenv('MARKETING_ACTIVITY_THRESHOLD', '10'))  # Messages to consider group as active
MARKETING_COOLDOWN_REDUCTION = float(os.getenv('MARKETING_COOLDOWN_REDUCTION', '0.2'))  # Hours to reduce from cooldown per activity threshold
MARKETING_MIN_COOLDOWN_HOURS = float(os.getenv('MARKETING_MIN_COOLDOWN_HOURS', '1.0'))  # Minimum cooldown period
MARKETING_MAX_LENGTH = int(os.getenv('MARKETING_MAX_LENGTH', '500'))  # Maximum length of marketing messages

class MarketingManager:
    def __init__(self, prompt_content: str, character: Dict, generation_manager: GenerationManager):
        self.prompt_content = prompt_content
        self.character = character
        self.generation_manager = generation_manager
        self.message_count = 0
        self.activity_count = 0  # Track messages for activity-based cooldown reduction
        self.last_marketing_time: Optional[datetime] = None
        self.base_cooldown = timedelta(hours=MARKETING_COOLDOWN_HOURS)
        self.marketing_cooldown = self.base_cooldown
        self.message_threshold = MARKETING_MESSAGE_THRESHOLD
        self.time_threshold = timedelta(hours=MARKETING_TIME_THRESHOLD_HOURS)
        self.start_time = datetime.now()

        logger.info(f"Initialized MarketingManager for character '{character.get('name', 'unknown')}'")
        logger.info(f"Settings: message_threshold={self.message_threshold}, time_threshold={self.time_threshold.total_seconds()/3600}h, cooldown={self.marketing_cooldown.total_seconds()/3600}h")

    def record_message(self) -> None:
        """Record a new message in the group and adjust cooldown based on activity"""
        if not ENABLE_MARKETING:
            return

        self.message_count += 1
        self.activity_count += 1

        # Reduce cooldown if group is active
        if self.activity_count >= MARKETING_ACTIVITY_THRESHOLD:
            reduction = timedelta(hours=MARKETING_COOLDOWN_REDUCTION)
            min_cooldown = timedelta(hours=MARKETING_MIN_COOLDOWN_HOURS)
            self.marketing_cooldown = max(min_cooldown, self.base_cooldown - reduction)
            self.activity_count = 0  # Reset activity counter

            if ENABLE_DEBUG_LOGS:
                logger.debug(f"Reduced marketing cooldown to {self.marketing_cooldown.total_seconds()/3600:.1f}h (min={min_cooldown.total_seconds()/3600:.1f}h)")

        if ENABLE_DEBUG_LOGS:
            time_since_start = datetime.now() - self.start_time
            time_since_last = datetime.now() - (self.last_marketing_time or self.start_time)
            logger.debug(f"Message recorded: count={self.message_count}, activity={self.activity_count}/{MARKETING_ACTIVITY_THRESHOLD}, "
                        f"time_since_start={time_since_start.total_seconds()/3600:.1f}h, "
                        f"time_since_last_marketing={time_since_last.total_seconds()/3600:.1f}h")

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

            if ENABLE_DEBUG_LOGS:
                logger.info(f"Generating marketing message for {character_name}")

            # Generate message using LLM
            prompt = f"""
{self.prompt_content}

Generate a concise marketing message related to NeuronLink.
"""
            message = await self.generation_manager.generate_text(prompt)


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
