from fastapi import FastAPI
from pydantic import BaseModel

from app.plugins.manager import PluginManager
from app.brain.brain import Brain


app = FastAPI(title="LEO")

plugin_manager = PluginManager()
plugin_manager.load_plugins()

brain = Brain(plugin_manager)


class Prompt(BaseModel):
    message: str


@app.post("/ask")
async def ask(prompt: Prompt):
    return await brain.think(prompt.message)