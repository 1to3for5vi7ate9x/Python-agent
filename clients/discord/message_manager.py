import discord
from loguru import logger
from core.message_handler import MessageHandler
import asyncio
import os
from dotenv import load_dotenv


class DiscordMessageManager:
    def __init__(self, runtime: dict):
        self.message_handler = MessageHandler(runtime["prompt_file"], runtime["character"])
        self.client = None
        self.conversations = {}  # Store conversation history: {user_id: [messages]}

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
            # Check if the message is from an allowed channel
            # allowed_channel_ids = "1301754237411262485,1128867684130508875".split(",")  # From .env
            # Reload environment variables
            load_dotenv(override=True)

            # Check if the message is from an allowed channel
            allowed_channel_ids = os.getenv("DISCORD_ALLOWED_CHANNELS", "").split(",")
            if str(message.channel.id) not in allowed_channel_ids:
                return

            # Don't respond to our own messages if replies are disabled
            if os.getenv('ENABLE_REPLIES', 'true').lower() == 'false':
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

            # Get response from message handler, passing conversation history
            response = await self.message_handler.handle_message(message, conversation_history)
            if response and not response.startswith("Error:"):
                self.conversations[user_id].append(f"Bot: {response}")  # Add bot response to history
                await self._send_with_typing(message, response)

        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")
