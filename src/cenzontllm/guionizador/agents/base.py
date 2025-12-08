from abc import ABC, abstractmethod
from ..config import settings
from ..mocks import mock_invoke
from typing import Dict, Any

if settings.RUN_MODE == "groq":
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)

class BaseAgent(ABC):
    name: str = "base"

    def invoke(self, input_data: Any) -> str:
        if settings.RUN_MODE == "mock":
            print(f"[MOCK {self.name.upper()}] Procesando...")
            return mock_invoke(self.name, prompt)

        # GROQ
        print(f"[GROQ {self.name.upper()}] Llama 3.1 70B trabajando...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=settings.MODEL,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
        )
        return chat_completion.choices[0].message.content.strip()

    @abstractmethod
    def _call_llm(self, input_data: Any) -> str:
        pass
