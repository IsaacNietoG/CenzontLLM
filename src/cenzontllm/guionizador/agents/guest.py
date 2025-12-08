from .base import BaseAgent
from ..prompts import GUEST_RESPONSE_PROMPT
from typing import Dict

class GuestAgent(BaseAgent):
    name = "guest"

    def respond(self, question: str, history: str, guest_profile: Dict) -> str:
        prompt = GUEST_RESPONSE_PROMPT.format(
            name=guest_profile["name"], age=guest_profile["age"], accent=guest_profile["accent"],
            bio=guest_profile["bio"], style=guest_profile["style"], question=question, history=history
        )
        return self.invoke(prompt)

    def _call_llm(self, prompt: str) -> str:
        return "Respuesta del guest from LLM"
