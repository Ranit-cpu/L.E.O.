import importlib
import inspect
import pkgutil

from app.plugins.base import Plugin


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        package = "app.plugins"

        for _, module_name, _ in pkgutil.iter_modules(["app/plugins"]):

            if module_name in ("base", "manager"):
                continue

            module = importlib.import_module(f"{package}.{module_name}")

            for _, obj in inspect.getmembers(module):

                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Plugin)
                    and obj is not Plugin
                ):
                    plugin = obj()
                    self.plugins[plugin.name] = plugin

    def list_plugins(self):
        return list(self.plugins.keys())

    def get(self, name):
        return self.plugins.get(name)