from typing import Any


class ToolExecutor:

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ):

        if tool_name == "system_info":

            plugin = self.plugin_manager.get("system")

            if not plugin:
                return {
                    "error": "System plugin is unavailable."
                }

            return await plugin.execute(**arguments)

        if tool_name == "web_search":

            plugin = self.plugin_manager.get("web_search")

            if not plugin:
                return {
                    "error": "Web search plugin is unavailable."
                }

            return await plugin.execute(**arguments)

        return {
            "error": f"Unknown tool: {tool_name}"
        }