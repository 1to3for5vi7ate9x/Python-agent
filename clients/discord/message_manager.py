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
        logger.info(f"Entering _send_with_typing, content: {content}")
        try:
            async with message.channel.typing():
                # Simulate typing (50ms per character, max 10 seconds)
                typing_duration = min(len(content) * 0.05, 10)
                await asyncio.sleep(typing_duration)
                logger.info(f"About to send reply: {content}")
                await message.reply(content)
                logger.info("Reply sent successfully (according to code)")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_message(self, message: discord.Message) -> None:
        logger.info(f"handle_message called with message: {message.content}")
        try: # Outer try block
            try:
                # Check if the message is from an allowed channel
                logger.info("Checking allowed channels")
                load_dotenv(override=True)
                allowed_channel_ids = os.getenv("DISCORD_ALLOWED_CHANNELS", "").split(",")
                logger.info(f"Allowed channel IDs: {allowed_channel_ids}")
                logger.info(f"Message channel ID: {message.channel.id}")
                if str(message.channel.id) not in allowed_channel_ids:
                    logger.info("Message is from a disallowed channel. Returning.")
                    return

                # Don't respond to our own messages if replies are disabled
                logger.info("Checking if replies are enabled")
                if os.getenv('ENABLE_REPLIES', 'true').lower() == 'false':
                    logger.info("Replies are disabled. Returning.")
                    return

                logger.info("Checking if message is from a bot")
                if message.author.bot:
                    logger.info("Message is from a bot. Returning.")
                    return

                # Get the user ID
                logger.info("Getting user ID")
                user_id = str(message.author.id)

                # Get the message content
                logger.info("Getting message content")
                content = message.content
                if not content:
                    logger.info("Message content is empty. Returning.")
                    return

                # Update conversation history
                logger.info("Updating conversation history")
                if user_id not in self.conversations:
                    self.conversations[user_id] = []
                self.conversations[user_id].append(f"User: {content}")

                # Get conversation history
                logger.info("Getting conversation history")
                conversation_history = "\\n".join(self.conversations[user_id])

                # Get response from message handler, passing conversation history
                logger.info("Calling message_handler.handle_message")
                response = await self.message_handler.handle_message(conversation_history)
                logger.info(f"Response from message_handler: {response}")
                if response and not response.startswith("Error:"):
                    self.conversations[user_id].append(f"Bot: {response}")  # Add bot response to history
                    logger.info(f"Sending response: {response}")
                    await self._send_with_typing(message, response)

            except Exception as e:
                logger.error(f"Error handling Discord message in existing block: {e}")
        except Exception as e: # Outer except block
            logger.error(f"Error in handle_message (outer block): {e}")

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
