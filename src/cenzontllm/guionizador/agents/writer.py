from typing import List, Dict
from .base import BaseAgent
from ..prompts import WRITER_PROMPT
from ..config import settings
import json

class WriterAgent(BaseAgent):
    name = "writer"

    def write(self, conversation: str, guests: List[dict], target_minutes: int) -> str:
        # SI ESTAMOS EN MODO GROQ, USAMOS EL LLM REAL
        if settings.RUN_MODE == "groq":
            print("[GROQ WRITER] Generando guion final con Llama 3.3 70B...")
            print("[GROQ DEBUG] ", conversation)
            prompt = WRITER_PROMPT.format(
                conversation=conversation,
                guests=json.dumps(guests, ensure_ascii=False),
                target_minutes=target_minutes
            )
            return self.invoke(prompt)

        # MOCK: guion bonito para pruebas
        print("[MOCK WRITER] Generando guion de ejemplo...")
        return f"""# CenzontLLM – Ciencia en Voz Alta

**Ana [enthusiastic]:** ¡Hola a todos y bienvenidos a CenzontLLM! Hoy tenemos un paper legendario: "Attention Is All You Need".

**Dr. {guests[0]['name'] if guests else 'Ramírez'} [serious_explanatory]:** Así es, Ana. Este paper revolucionó todo...

[SFX: música épica]

¡Y eso es todo por hoy! Duración estimada: ~{target_minutes} minutos
---
Generado automáticamente por CenzontLLM
"""

    def _call_llm(self, prompt: str) -> str:
        raise NotImplementedError("LLM real no implementado aún")
