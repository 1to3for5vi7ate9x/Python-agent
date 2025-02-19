import discord
from loguru import logger
from core.message_handler import MessageHandler
import asyncio
import os
from dotenv import load_dotenv
from core.generation import GenerationManager
import time
from datetime import datetime, timedelta
from typing import Optional, Dict


class DiscordMessageManager:
    def __init__(self, runtime: dict):
        self.client = None
        self.conversations = {}  # Store conversation history: {user_id: [messages]}
        self.prompt_file = runtime["prompt_file"]
        self.relevance_prompt_file = "prompts/relevance/relevance_prompt.txt"  # Path to the relevance prompt
        self.message_handler = MessageHandler(
            prompt_file=self.prompt_file,
            character={},
            relevance_prompt_file=self.relevance_prompt_file
        )

        # Set log level based on environment variable
        logger.remove()  # Remove default handler
        if os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true':
            logger.add(lambda msg: print(msg), level="DEBUG") # Add this to see all logs in console
        else:
            logger.add(lambda msg: print(msg), level="INFO")  # Add a handler with INFO level

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

            # Get response from message handler
            response = await self.message_handler.handle_message(message, conversation_history)
            if response and not response.startswith("Error:"):
                self.conversations[user_id].append(f"Bot: {response}")  # Add bot response to history
                await self._send_with_typing(message, response)

        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")

    async def _send_with_typing(self, message: discord.Message, response: str) -> None:
        """Simulate typing and send a message."""
        async with message.channel.typing():
            await asyncio.sleep(len(response) * 0.2)  # Simulate typing speed
            await message.channel.send(response)
