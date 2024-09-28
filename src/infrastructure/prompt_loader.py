import aiofiles
import os


class PromptLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    async def load_prompt(self, filename: str, subdir: str = "") -> str:
        path = os.path.join(self.base_dir, subdir, filename)
        async with aiofiles.open(path, mode="r") as file:
            return await file.read()
