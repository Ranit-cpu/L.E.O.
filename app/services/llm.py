from typing import Any
from ollama import AsyncClient


class LLMService:

    def __init__(self):
        self.client = AsyncClient(
            host="http://127.0.0.1:11434"
        )
        self.model = "qwen3:1.7b"

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ):
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools or [],
            think=False,
            options={
                "temperature": 0.2,
                "num_predict": 96,
                "num_ctx": 4096,
            },
        )

        message = response.get("message", {})

        return {
            "message": {
                "role": message.get("role", "assistant"),
                "content": message.get("content", "").strip(),
                "tool_calls": message.get("tool_calls", []),
            }
        }