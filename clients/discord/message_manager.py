import discord
from loguru import logger
from core.message_handler import MessageHandler
import asyncio

class DiscordMessageManager:
    def __init__(self, runtime: dict):
        self.message_handler = MessageHandler(runtime["prompt_file"], runtime["character"])
        self.client = None

    async def _send_with_typing(self, message: discord.Message, content: str) -> None:
        """Send a message with typing animation"""
        try:
            async with message.channel.typing():
                # Simulate typing (50ms per character, max 10 seconds)
                typing_duration = min(len(content) * 0.05, 10)
                await asyncio.sleep(typing_duration)
                await message.reply(content)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_message(self, message: discord.Message) -> None:
        try:
            # Don't respond to our own messages
            if message.author.bot:
                return

            # Get the message content
            content = message.content
            if not content:
                return

            # Get response from message handler
            response = await self.message_handler.handle_message(content)
            if response and not response.startswith("Error:"):
                await self._send_with_typing(message, response)

        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")
            
    async def send_marketing_message(self, channel_id: int) -> None:
        try:
            # Generate marketing message
            message = await self.message_handler.marketing_manager.generate_marketing_message()
            
            if message and not message.startswith("Error:") and self.client:
                channel = self.client.get_channel(channel_id)
                if channel:
                    async with channel.typing():
                        # Simulate typing (50ms per character, max 10 seconds)
                        typing_duration = min(len(message) * 0.05, 10)
                        await asyncio.sleep(typing_duration)
                        await channel.send(message)
                        logger.info(f"Sent marketing message to channel {channel_id}")
                else:
                    logger.error(f"Could not find channel {channel_id}")
        except Exception as e:
            logger.error(f"Error sending marketing message: {e}")
