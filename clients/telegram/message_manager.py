from telethon import events
from loguru import logger
from core.message_handler import MessageHandler
from telethon import events
from loguru import logger
from core.message_handler import MessageHandler
import asyncio
import json
import os
from datetime import datetime

class TelegramMessageManager:
    def __init__(self, runtime: dict):
        os.makedirs('logs', exist_ok=True)
        self.log_file = open('logs/telegram_log.json', 'a')
        self.conversations = {}  # Store conversation history: {chat_id: [messages]}
        self.prompt_file = runtime["prompt_file"]
        self.relevance_prompt_file = "prompts/relevance/relevance_prompt.txt"  # Path to the relevance prompt
        self.message_handler = MessageHandler(
            prompt_file=self.prompt_file,
            character={},
            relevance_prompt_file=self.relevance_prompt_file
        )

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
            message_text = event.message.text
            if not message_text:
                return

            # Get the chat ID
            chat_id = str(event.chat_id)

            # Update conversation history
            if chat_id not in self.conversations:
                self.conversations[chat_id] = []
            self.conversations[chat_id].append(f"User: {message_text}")

            # Get conversation history
            conversation_history = "\\n".join(self.conversations[chat_id])

            # Get response from message handler
            response = await self.message_handler.handle_message(event, conversation_history)
            if response and not response.startswith("Error:"):
                self.conversations[chat_id].append(f"Bot: {response}")  # Add bot response to history
                await self._send_with_typing(event, response)
                self.log_reply(message_text, response)

        except Exception as e:
            logger.error(f"Error handling Telegram message: {e}")

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
