import os

from src.infrastructure.prompt_loader import PromptLoader


class TradingStrategy:
    def __init__(self, name: str, prompt_loader: PromptLoader):
        self.name = name
        self.prompt_loader = prompt_loader

    def get_name(self) -> str:
        return self.name.split(".")[0]

    async def get_strategy_content(self) -> str:
        name = self.name if self.name.endswith(".txt") else f"{self.name}.txt"
        return await self.prompt_loader.load_prompt(name)


def get_all_trading_strategies(
    filepath: str, loader: PromptLoader
) -> list[TradingStrategy]:
    return [TradingStrategy(name, loader) for name in os.listdir(filepath)]
