from .base import BaseAgent
from ..prompts import HOST_INITIAL_PROMPT, HOST_EVALUATION_PROMPT
from ..config import settings
from typing import Dict
import json

class HostAgent(BaseAgent):
    name = "host"

    def generate_personalities_and_outline(self, paper: Dict) -> Dict:
        summary = json.dumps(paper, ensure_ascii=False)
        prompt = HOST_INITIAL_PROMPT.format(
            paper_summary=summary, num_guests=settings.NUM_GUESTS, target_minutes=settings.TARGET_MINUTES
        )
        response = self.invoke(prompt)
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            print("[MOCK DEBUG]: ", response)
            print("[MOCK] Usando fallback de personalidades y outline")
            return {
                "guests": [
                    {"name": "Dr. Luis Ramírez", "age": 52, "accent": "mexicano", "bio": "Físico teórico convertido a ML, explica con ejemplos cotidianos", "style": "claro y entusiasta"}
                ],
                "outline": [
                    "1. ¿Qué problema resolvía el mundo antes de los Transformers?",
                    "2. ¿Cuál es la idea revolucionaria del paper?",
                    "3. ¿Cómo funciona el mecanismo de atención?",
                    "4. ¿Por qué es tan rápido de entrenar?",
                    "5. ¿Cuáles fueron los resultados en traducción?",
                    "6. ¿Qué ha pasado desde 2017 hasta hoy?"
                ]
            }

    def evaluate_coverage(self, conversation: str, outline: str, current_round: int, max_rounds: int) -> str:
        prompt = HOST_EVALUATION_PROMPT.format(conversation=conversation, outline="\n".join(outline), current_round=current_round, max_rounds=max_rounds)
        return self.invoke(prompt)

    def _call_llm(self, prompt: str) -> str:
        # Aquí irá el call real a Groq/Ollama
        return "JSON or evaluation string from LLM"
