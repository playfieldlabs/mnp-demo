from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    model: str = Field(default="claude-sonnet-4-5-20250929")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, gt=0)
    max_tool_calls: int = Field(default=4, ge=0)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentConfig":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_tool_calls": self.max_tool_calls,
        }
