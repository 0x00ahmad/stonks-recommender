import json
import os
from datetime import datetime
from typing import Any

import aiofiles
import mplfinance as mpf
import pandas as pd

from src.core.logger import get_logger, log_async
from src.data.external.fetcher import AssetData
from src.data.value_objects import Asset, TimeRange, get_offset_by_from_time_range

logger = get_logger(__name__)


class AssetDataRepository:
    def __init__(self, base_dir: str = "repository/asset_data"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    @log_async("DEBUG")
    async def save_asset_data(self, asset: Asset, data: AssetData):
        os.makedirs(
            os.path.join(self.base_dir, asset.symbol.replace("/", "_")), exist_ok=True
        )
        file_path = self._get_file_path(asset)
        await logger.async_debug(f"Saving asset data for {asset.symbol}")
        async with aiofiles.open(file_path, mode="w") as f:
            await f.write(json.dumps(data.to_dict(), indent=2))

    @log_async("DEBUG")
    async def get_asset_data(self, asset: Asset) -> dict:
        file_path = self._get_file_path(asset)
        await logger.async_debug(f"Retrieving asset data for {asset.symbol}")
        if not os.path.exists(file_path):
            return {}
        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()
            return json.loads(content) if content else {}

    def _get_file_path(self, asset: Asset) -> str:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(
            self.base_dir, f"{asset.symbol.replace('/', '_')}/{now}.json"
        )


class AssetImageRepository:
    def __init__(
        self, data: AssetData, base_dir: str = "repository/asset_data"
    ) -> None:
        self.data = data
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    @staticmethod
    def calculate_support_resistance(df, window=14):
        support = df["Low"].rolling(window=window).min().iloc[-1]
        resistance = df["High"].rolling(window=window).max().iloc[-1]
        return support, resistance

    def generate_candlestick_chart(self, time_range: TimeRange) -> str:
        logger.debug(f"Generating candlestick chart for {self.data.symbol}")
        dates = pd.to_datetime(self.data.info.timestamp, unit="s")
        df: pd.DataFrame = pd.DataFrame(
            {
                "Open": self.data.info.indicators.quote[0]["open"],
                "High": self.data.info.indicators.quote[0]["high"],
                "Low": self.data.info.indicators.quote[0]["low"],
                "Close": self.data.info.indicators.quote[0]["close"],
                "Volume": self.data.info.indicators.quote[0]["volume"],
            },
            index=dates,
        )

        offset_by: Any = get_offset_by_from_time_range(time_range)
        back_till = df.index[-1] - pd.DateOffset(**offset_by)
        df = df.loc[df.index >= back_till]

        support, resistance = self.calculate_support_resistance(df, window=14)

        logger.debug(f"Support: {support}, Resistance: {resistance}")

        save_filepath = f"{self.base_dir}/{self.data.symbol.replace('/', '_')}/{time_range.value}.png"

        mpf.plot(
            df,
            type="candle",
            volume=True,
            style="yahoo",
            savefig=save_filepath,
            scale_width_adjustment=dict(volume=0.7),
            figsize=(16, 9),
            xrotation=0,
            tight_layout=True,
            hlines=dict(
                hlines=[support, resistance], colors=["g", "r"], linestyle="-."
            ),
        )

        return save_filepath
