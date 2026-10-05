from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.plugins.base import Plugin


class WebSearchPlugin(Plugin):

    name = "web_search"
    description = "Searches the internet for current information."

    def get_tool_definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": (
                    "Search the internet for current, recent, or factual "
                    "information that may not be available in the local model."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    async def execute(self, query: str) -> dict[str, Any]:

        url = "https://html.duckduckgo.com/html/"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            )
        }

        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True
        ) as client:

            response = await client.get(
                url,
                params={"q": query},
                headers=headers
            )

            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        for result in soup.select(".result")[:5]:

            title_element = result.select_one(".result__title")
            link_element = result.select_one(".result__a")
            snippet_element = result.select_one(".result__snippet")

            if not title_element or not link_element:
                continue

            results.append({
                "title": title_element.get_text(" ", strip=True),
                "url": link_element.get("href"),
                "snippet": (
                    snippet_element.get_text(" ", strip=True)
                    if snippet_element
                    else ""
                )
            })

        return {
            "query": query,
            "results": results
        }