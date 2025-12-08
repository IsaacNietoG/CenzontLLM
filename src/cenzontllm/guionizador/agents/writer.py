from .base import BaseAgent
from typing import Dict
from ..prompts import WRITER_PROMPT
import json

class WriterAgent(BaseAgent):
    name = "writer"

    def write(self, conversation: str, guests: list, target_minutes: int) -> str:
        prompt = WRITER_PROMPT.format(conversation=conversation, guests=json.dumps(guests, ensure_ascii=False), target_minutes=target_minutes)
        return self.invoke(prompt)

    def _call_llm(self, prompt: str) -> str:
        return "Guion final from LLM"
