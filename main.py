import asyncio
import json
import signal
import sys
from typing import List, Any, Optional, Dict
from dotenv import load_dotenv
import os
from loguru import logger
import argparse

from clients.telegram.client import TelegramUserClient
from clients.discord.client import DiscordClient

class GracefulExit(SystemExit):
    pass

class AgentManager:
    def __init__(self, prompt_file: str = None):
        self.telegram_client = None
        self.discord_client = None
        self.tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        self.loop = None
        self.prompt_file = prompt_file
        # Load environment variables, removing comments
        from dotenv import dotenv_values
        dotenv_dict = dotenv_values(".env")
        for key, value in dotenv_dict.items():
            if value is not None:
                os.environ[key] = value

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

    async def start(self):
        self.loop = asyncio.get_running_loop()
        self.setup_signal_handlers()

        try:
            # Initialize clients based on environment variables
            if os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true':
                try:
                    self.telegram_client = TelegramUserClient(prompt_file=self.prompt_file)
                    self.tasks.append(asyncio.create_task(self.telegram_client.start()))
                    logger.info("Telegram user client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Telegram client: {e}")
            else:
                logger.info("Telegram client is disabled via environment variable.")

            if os.getenv("ENABLE_DISCORD", "false").lower() == "true" and os.getenv("DISCORD_TOKEN"):
                try:
                    self.discord_client = DiscordClient(prompt_file=self.prompt_file)
                    self.tasks.append(asyncio.create_task(self.discord_client.start(os.getenv("DISCORD_TOKEN"))))
                    logger.info("Discord user client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Discord client: {e}")
            else:
                logger.info("Discord client is disabled via environment variable.")

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
    parser = argparse.ArgumentParser(description="Run the agent with a specific prompt file.")
    parser.add_argument("--prompt_file", type=str, help="Path to the prompt file", default=None)
    args = parser.parse_args()

    try:
        agent = AgentManager(prompt_file=args.prompt_file)
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
