import platform
import socket
import time
from typing import Any

import psutil

from app.plugins.base import Plugin


class SystemPlugin(Plugin):

    name = "system"
    description = "Provides information about the local Linux computer."

    def get_tool_definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "system_info",
                "description": (
                    "Get information about the local computer such as "
                    "hostname, CPU usage, RAM usage, disk usage, operating system, "
                    "uptime, battery status, or IP address."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "info_type": {
                            "type": "string",
                            "enum": [
                                "hostname",
                                "cpu",
                                "ram",
                                "disk",
                                "os",
                                "uptime",
                                "battery",
                                "ip",
                            ],
                            "description": "The system information to retrieve.",
                        }
                    },
                    "required": ["info_type"],
                },
            },
        }

    async def execute(self, info_type: str) -> dict[str, Any]:

        if info_type == "hostname":
            return {
                "hostname": socket.gethostname()
            }

        if info_type == "cpu":
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.2)
            }

        if info_type == "ram":
            memory = psutil.virtual_memory()

            return {
                "memory_percent": memory.percent,
                "used_gb": round(memory.used / 1024**3, 2),
                "total_gb": round(memory.total / 1024**3, 2),
            }

        if info_type == "disk":
            disk = psutil.disk_usage("/")

            return {
                "disk_percent": disk.percent,
                "used_gb": round(disk.used / 1024**3, 2),
                "total_gb": round(disk.total / 1024**3, 2),
            }

        if info_type == "os":
            return {
                "system": platform.system(),
                "release": platform.release(),
            }

        if info_type == "uptime":
            seconds = int(time.time() - psutil.boot_time())

            return {
                "uptime_hours": round(seconds / 3600, 2)
            }

        if info_type == "battery":
            battery = psutil.sensors_battery()

            if battery is None:
                return {
                    "available": False,
                    "message": "No battery detected."
                }

            return {
                "available": True,
                "percent": battery.percent,
                "plugged_in": battery.power_plugged,
            }

        if info_type == "ip":
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("8.8.8.8", 80))
                ip_address = sock.getsockname()[0]
                sock.close()

                return {
                    "ip_address": ip_address
                }

            except socket.error:
                return {
                    "error": "Unable to determine local IP address."
                }

        return {
            "error": f"Unknown information type: {info_type}"
        }

    async def execute_from_text(self, command: str):

        command = command.lower()

        if "hostname" in command or "host name" in command:
            result = await self.execute(info_type="hostname")
            return f"Your hostname is {result['hostname']}."

        if "cpu" in command:
            result = await self.execute(info_type="cpu")
            return f"Your CPU usage is {result['cpu_percent']}%."

        if "ram" in command or "memory" in command:
            result = await self.execute(info_type="ram")
            return (
                f"Your RAM usage is {result['memory_percent']}%. "
                f"{result['used_gb']} GB of {result['total_gb']} GB is currently used."
            )

        if "disk" in command or "storage" in command:
            result = await self.execute(info_type="disk")
            return (
                f"Your disk usage is {result['disk_percent']}%. "
                f"{result['used_gb']} GB of {result['total_gb']} GB is currently used."
            )

        if "operating system" in command or " os " in f" {command} ":
            result = await self.execute(info_type="os")
            return f"You are running {result['system']} {result['release']}."

        if "uptime" in command:
            result = await self.execute(info_type="uptime")
            return f"Your system has been running for {result['uptime_hours']} hours."

        if "battery" in command:
            result = await self.execute(info_type="battery")

            if not result["available"]:
                return result["message"]

            status = "plugged in" if result["plugged_in"] else "on battery"
            return f"Your battery is at {result['percent']}% and you are {status}."

        if "ip address" in command or "ip" in command:
            result = await self.execute(info_type="ip")

            if "error" in result:
                return result["error"]

            return f"Your IP address is {result['ip_address']}."

        return "I couldn't determine the system information requested."