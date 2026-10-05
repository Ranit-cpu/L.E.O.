from abc import ABC, abstractmethod
from typing import Any


class Plugin(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def get_tool_definition(self) -> dict[str, Any]:
        """Return the tool definition used by the LLM."""
        raise NotImplementedError

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        raise NotImplementedError