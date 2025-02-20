from telethon import events
from loguru import logger
from core.message_handler import MessageHandler
import asyncio
import json
import os
from datetime import datetime

class TelegramMessageManager:
    def __init__(self, runtime: dict):
        self.message_handler = MessageHandler(runtime["prompt_file"], runtime["character"])
        os.makedirs('logs', exist_ok=True)
        self.log_file = open('logs/telegram_log.json', 'a')

    async def _send_with_typing(self, event, message: str) -> None:
        """Send a message with typing animation"""
        try:
            async with event.client.action(event.chat_id, 'typing'):
                # Simulate typing (50ms per character, max 10 seconds)
                typing_duration = min(len(message) * 0.05, 10)
                await asyncio.sleep(typing_duration)
                await event.reply(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_message(self, event: events.NewMessage.Event) -> None:
        try:
            # Don't respond to our own messages
            if event.message.out:
                return

            # Get the message text
            message = event.message.text
            if not message:
                return

            # Get response from message handler
            response = await self.message_handler.handle_message(message)
            if response and not response.startswith("Error:"):
                await self._send_with_typing(event, response)
                self.log_reply(message, response)

        except Exception as e:
            logger.error(f"Error handling Telegram message: {e}")

    async def send_marketing_message(self, chat_id: int) -> None:
        try:
            # Generate marketing message
            message = await self.message_handler.marketing_manager.generate_marketing_message()
            
            if message and not message.startswith("Error:") and hasattr(self, 'client'):
                async with self.client.action(chat_id, 'typing'):
                    # Simulate typing (50ms per character, max 10 seconds)
                    typing_duration = min(len(message) * 0.05, 10)
                    await asyncio.sleep(typing_duration)
                    await self.client.send_message(chat_id, message)
                    logger.info(f"Sent marketing message to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error sending marketing message: {e}")

    def log_reply(self, original_message: str, reply: str):
        """Log the original message and the reply to a JSON file."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'original_message': original_message,
                'reply': reply
            }
            self.log_file.write(json.dumps(log_entry) + '\\n')
            self.log_file.flush()
        except Exception as e:
            logger.error(f"Error logging reply: {e}")

    def __del__(self):
        self.log_file.close()
