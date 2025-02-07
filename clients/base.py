from abc import ABC, abstractmethod
from typing import Any
from core.generation import GenerationManager

class BaseMessageManager(ABC):
    def __init__(self, runtime: dict, generation_manager: GenerationManager):
        self.runtime = runtime
        self.generation_manager = generation_manager

    @abstractmethod
    async def handle_message(self, message: Any) -> None:
        pass

    @abstractmethod
    async def send_marketing_message(self, chat_id: Any) -> None:
        pass
