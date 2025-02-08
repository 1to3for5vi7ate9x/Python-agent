import asyncio
import json
import signal
import sys
from typing import List, Any, Optional, Dict
from dotenv import load_dotenv
import os
from loguru import logger

from clients.telegram.client import TelegramUserClient
from clients.discord.client import DiscordClient
from core.character_manager import CharacterManager

class GracefulExit(SystemExit):
    pass

class AgentManager:
    def __init__(self):
        self.telegram_client = None
        self.discord_client = None
        self.tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        self.loop = None
        load_dotenv()

    def setup_signal_handlers(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            self.loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(sig=s))
            )

    async def shutdown(self, sig=None):
        if sig:
            logger.info(f"Received exit signal {sig.name}...")

        self.shutdown_event.set()

        # Close Discord client
        if self.discord_client:
            logger.info("Closing Discord client...")
            await self.discord_client.close()

        # Close Telegram client
        if self.telegram_client:
            logger.info("Closing Telegram client...")
            await self.telegram_client.client.disconnect()

        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()

        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        if self.loop:
            self.loop.stop()
        raise GracefulExit()

    def select_character(self) -> Optional[Dict]:
        """Select a character to use for the agent"""
        character_manager = CharacterManager()
        return character_manager.select_character()
    
    async def start(self):
        self.loop = asyncio.get_running_loop()
        self.setup_signal_handlers()

        try:
            # Select character
            character = self.select_character()
            if not character:
                logger.error("No character selected. Exiting...")
                await self.shutdown()
                return
                
            logger.info(f"Selected character: {character['name']}")

            # Initialize clients based on character configuration
            if "telegram" in character["clients"]:
                try:
                    self.telegram_client = TelegramUserClient(character=character)
                    self.tasks.append(asyncio.create_task(self.telegram_client.start()))
                    logger.info("Telegram user client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Telegram client: {e}")

            if "discord" in character["clients"]:
                try:
                    self.discord_client = DiscordClient(character=character)
                    self.tasks.append(asyncio.create_task(self.discord_client.start(os.getenv("DISCORD_TOKEN"))))
                    logger.info("Discord user client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Discord client: {e}")

            if not self.tasks:
                logger.error("No clients were initialized successfully")
                await self.shutdown()
                return

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            logger.error(f"Error in main: {e}")
            await self.shutdown()
            raise

def main():
    try:
        agent = AgentManager()
        asyncio.run(agent.start())
    except GracefulExit:
        logger.info("Shutdown complete.")
    except KeyboardInterrupt:
        # This should not happen as we handle it with signals
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
