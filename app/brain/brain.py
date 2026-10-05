from app.brain.tool_executor import ToolExecutor
from app.brain.router import IntentRouter
from app.services.llm import LLMService


class Brain:

    def __init__(self, plugin_manager):
        self.max_history = 10
        self.plugin_manager = plugin_manager
        self.tool_executor = ToolExecutor(plugin_manager)
        self.router = IntentRouter()
        self.llm = LLMService()
        self.conversation_history = []

    async def think(self, message: str):

        route = self.router.route(message)

        # ==========================================
        # FAST PATH — SYSTEM
        # ==========================================

        if route == "system":

            plugin = self.plugin_manager.get("system")

            if not plugin:
                return {
                    "type": "error",
                    "message": "System plugin is unavailable."
                }

            return {
                "type": "tool",
                "message": await plugin.execute_from_text(message)
            }

        # ==========================================
        # FAST WEB PATH
        # Search FIRST, then ask Qwen to summarize.
        # This avoids Qwen tool-selection inference.
        # ==========================================

        if route == "web":

            plugin = self.plugin_manager.get("web_search")

            if not plugin:
                return {
                    "type": "error",
                    "message": "Web search plugin is unavailable."
                }

            search_result = await plugin.execute(message)

            if not search_result.get("results"):
                return {
                    "type": "web",
                    "message": "I couldn't find any useful results."
                }

            results_text = "\n\n".join(
                [
                    f"Title: {result['title']}\n"
                    f"URL: {result['url']}\n"
                    f"Summary: {result['snippet']}"
                    for result in search_result["results"]
                ]
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are L.E.O. — Local Execution & Overwatch Engine. "
                        "Answer naturally and concisely. "
                        "Use ONLY the provided search results for current "
                        "information. Do not invent facts. "
                        "Mention the relevant sources when useful."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "/no_think\n"
                        "Answer the user's question using the search results below. "
                        "Give only the final answer. "
                        "Keep it concise, maximum 2-3 sentences.\n\n"
                        f"User question:\n{message}\n\n"
                        f"Web search results:\n{results_text}"
                    )
                }
            ]

            response = await self.llm.chat(
                messages=messages
            )

            return {
                "type": "web",
                "message": response["message"]["content"]
            }

        # ==========================================
        # GENERAL LLM / TOOL-CALLING PATH
        # ==========================================

        messages = [
            {
                "role": "system",
                "content": (
                    "You are L.E.O. — Local Execution & Overwatch Engine. "
                    "You are a local AI desktop assistant. "
                    "Use available tools when necessary. "
                    "Be concise, natural and helpful. "
                    "Remember the previous conversation and use it to answer "
                    "follow-up questions correctly."
                )
            }
        ]

        messages.extend(self.conversation_history)

        messages.append({
            "role": "user",
            "content": message
        })

        tools = [
            plugin.get_tool_definition()
            for plugin in self.plugin_manager.plugins.values()
        ]

        print("DEBUG HISTORY:", messages)

        response = await self.llm.chat(
            messages=messages,
            tools=tools
        )

        assistant_message = response["message"]
        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message["content"]
            })

            self.conversation_history = self.conversation_history[-self.max_history:]

            return {
                "type": "llm",
                "message": assistant_message["content"]
            }

        messages.append(assistant_message)

        for tool_call in tool_calls:

            function = tool_call["function"]

            tool_name = function["name"]
            arguments = function.get("arguments", {})

            result = await self.tool_executor.execute(
                tool_name,
                arguments
            )

            messages.append({
                "role": "tool",
                "content": str(result)
            })

        final_response = await self.llm.chat(
            messages=messages
        )

        return {
            "type": "tool",
            "message": final_response["message"]["content"]
        }