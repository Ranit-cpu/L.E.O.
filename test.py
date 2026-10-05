import asyncio

from app.services.llm import LLMService


async def main():
    leo = LLMService()

    reply = await leo.chat("what's the time")

    print(reply)


asyncio.run(main())