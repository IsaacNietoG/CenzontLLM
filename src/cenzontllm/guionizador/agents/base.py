from abc import ABC, abstractmethod
from ..config import settings
from ..mocks import mock_invoke
from typing import Dict, Any

class BaseAgent(ABC):
    name: str

    def invoke(self, input_data: Any) -> str:
        if settings.RUN_MODE == "mock":
            return mock_invoke(self.name, str(input_data))
        return self._call_llm(input_data)

    @abstractmethod
    def _call_llm(self, input_data: Any) -> str:
        pass
