from typing_extensions import override
from comfy_api.latest import ComfyExtension, io
from .unload_timer import init


init()

class UnloadTimerExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
        ]


async def comfy_entrypoint() -> UnloadTimerExtension:  # ComfyUI calls this to load your extension and its nodes.
    return UnloadTimerExtension()


# NODE_CLASS_MAPPINGS = { }
WEB_DIRECTORY = "./js"
