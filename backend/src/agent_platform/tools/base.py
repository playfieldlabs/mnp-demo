from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def output_schema(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def context(self) -> str:
        pass

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> Any:
        pass
