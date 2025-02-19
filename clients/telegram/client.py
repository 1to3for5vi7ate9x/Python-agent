from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import Channel, Chat
from core.generation import GenerationManager
from .message_manager import TelegramMessageManager
import os
from loguru import logger

class TelegramUserClient:
    def __init__(self, character: dict):
        # Initialize Telegram client with user credentials
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        
        # Set up session in the sessions directory
        os.makedirs('sessions', exist_ok=True)
        session_path = os.path.join('sessions', 'user_session')
        
        # Get allowed chats
        self.allowed_groups = os.getenv('TELEGRAM_ALLOWED_GROUPS', '').split(',')
        self.allowed_groups = [g.strip() for g in self.allowed_groups if g.strip()]
        self.allowed_chat_ids = set()
        
        # Initialize client and message manager
        self.client = TelegramClient(
            session_path,
            self.api_id,
            self.api_hash
        )
        
        self.message_manager = TelegramMessageManager(
            runtime={"character": character, "prompt_file": character.get("prompt_file")}
        )

    async def _resolve_allowed_chats(self):
        async for dialog in self.client.iter_dialogs():
            if isinstance(dialog.entity, (Channel, Chat)):
                if dialog.name in self.allowed_groups:
                    self.allowed_chat_ids.add(dialog.id)
                    logger.info(f"Found allowed chat: {dialog.name} (ID: {dialog.id})")

    async def start(self):
        await self.client.start(phone=self.phone)
        await self._resolve_allowed_chats()
        
        @self.client.on(NewMessage(incoming=True))
        async def handle_new_message(event):
            # Only respond in allowed chats
            if event.chat_id not in self.allowed_chat_ids:
                return
                
            await self.message_manager.handle_message(event)
        
        logger.info(f"Started Telegram user client with allowed groups: {self.allowed_groups}")
        await self.client.run_until_disconnected()
