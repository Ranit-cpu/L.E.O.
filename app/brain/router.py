import re


class IntentRouter:

    SYSTEM = {
        "cpu",
        "ram",
        "memory",
        "hostname",
        "disk",
        "storage",
        "system",
        "battery",
        "ip",
        "os",
        "uptime",
    }

    WEB = {
        "search",
        "google",
        "latest",
        "today",
        "current",
        "recent",
        "news",
        "find",
        "online",
        "internet",
        "weather",
    }

    def route(self, message: str):

        words = set(
            re.findall(r"\b\w+\b", message.lower())
        )

        if words & self.SYSTEM:
            return "system"

        if words & self.WEB:
            return "web"

        return "llm"