from typing import Dict, List, Optional
from pydantic import BaseModel

class Template(BaseModel):
    telegramMessageHandlerTemplate: str
    telegramShouldRespondTemplate: str
    discordMessageHandlerTemplate: str
    discordShouldRespondTemplate: str
    telegramMarketingTemplate: str
    discordMarketingTemplate: str

class Character(BaseModel):
    name: str
    username: str
    modelProvider: str
    templates: Template
    clients: List[str]
