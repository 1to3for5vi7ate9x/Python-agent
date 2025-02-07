import discord
from loguru import logger
from core.generation import GenerationManager
from .message_manager import DiscordMessageManager

class DiscordClient(discord.Client):
    def __init__(self, character: dict):
        super().__init__()
        self.generation_manager = GenerationManager()
        self.message_manager = DiscordMessageManager(
            runtime={"character": character},
            generation_manager=self.generation_manager
        )

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.message_manager.handle_message(message)
