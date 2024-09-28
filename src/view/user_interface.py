from typing import Tuple

import questionary

from src.data.entities import TimeFrame
from src.data.repository.trading_strategy import TradingStrategy
from src.data.value_objects import Asset, TimeRange


class UserInterface:
    def __init__(self, assets: list[Asset], strategies: list[TradingStrategy]):
        self.assets = assets
        self.strategies = strategies

    async def get_user_input(self) -> Tuple[Asset, TimeFrame, TradingStrategy] | None:
        try:
            asset = await self._get_asset()
            time_range = await self._get_time_range()
            time_interval = await self._get_time_interval()
            strategy = await self._get_strategy()
            if asset is None or time_range is None or strategy is None:
                return None
            return (
                asset,
                TimeFrame(time_range=time_range, time_interval=time_interval),
                strategy,
            )
        except KeyboardInterrupt:
            print("[-] User cancelled the operation")
            exit()

    async def _get_asset(self) -> Asset:
        asset_choices = [
            questionary.Choice(title=asset.symbol, value=asset) for asset in self.assets
        ]
        result = await questionary.select(
            "Select an asset (stock):", choices=asset_choices
        ).ask_async()
        return result

    async def _get_time_range(self) -> TimeRange:
        time_range_choices = [
            questionary.Choice(title=tr.value, value=tr) for tr in TimeRange
        ]
        result = await questionary.select(
            "Select time range:", choices=time_range_choices
        ).ask_async()
        return result

    async def _get_time_interval(self) -> TimeRange:
        time_interval_choices = [
            questionary.Choice(title=tr.value, value=tr) for tr in TimeRange
        ]
        result = await questionary.select(
            "Select time interval:", choices=time_interval_choices
        ).ask_async()
        return result

    async def _get_strategy(self) -> TradingStrategy:
        strategy_choices = [
            questionary.Choice(title=strategy.name, value=strategy)
            for strategy in self.strategies
        ]
        result = await questionary.select(
            "Select a strategy:", choices=strategy_choices
        ).ask_async()
        return result
