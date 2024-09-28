from datetime import datetime
from typing import Optional

import aiohttp
from pydantic import BaseModel

from src.config import YH_RAPID_API_KEY
from src.core.logger import get_logger, log_async
from src.data.entities import TimeFrame
from src.data.value_objects import Asset, AssetType

logger = get_logger(__name__)


class TradingPeriod(BaseModel):
    timezone: str
    start: int
    end: int
    gmtoffset: int


class CurrentTradingPeriod(BaseModel):
    pre: TradingPeriod
    regular: TradingPeriod
    post: TradingPeriod


class Meta(BaseModel):
    currency: str
    symbol: str
    exchangeName: str
    instrumentType: str
    firstTradeDate: int
    regularMarketTime: int
    gmtoffset: int
    timezone: str
    exchangeTimezoneName: str
    regularMarketPrice: float
    chartPreviousClose: float
    previousClose: float
    scale: int
    priceHint: int
    currentTradingPeriod: CurrentTradingPeriod
    tradingPeriods: list[list[TradingPeriod]]
    dataGranularity: str
    range: str
    validRanges: list[str]


class Indicator(BaseModel):
    quote: list[dict]


class StockInfo(BaseModel):
    meta: Meta
    timestamp: list[int]
    indicators: Indicator


class AssetData(BaseModel):
    symbol: str
    info: StockInfo
    created_at: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "info": self.info.dict(),
            "created_at": self.created_at.isoformat(),
        }


# INFO: Main class below


class AssetDataFetcher:
    def __init__(self):
        self.base_headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "yh-finance.p.rapidapi.com",
            "x-rapidapi-key": YH_RAPID_API_KEY,
        }

    @log_async("DEBUG")
    async def fetch_asset_data(
        self, asset: Asset, time_frame: TimeFrame
    ) -> Optional[AssetData]:
        if asset.asset_type == AssetType.STOCK:
            return await self.fetch_stock_data(asset, time_frame)
        elif asset.asset_type == AssetType.FOREX:
            raise NotImplementedError("Forex data fetching is not implemented")
        else:
            raise ValueError(f"Unsupported asset type: {asset.asset_type}")

    async def fetch_stock_data(
        self, asset: Asset, time_frame: TimeFrame
    ) -> Optional[AssetData]:
        await logger.async_info(f"Fetching stock data for {asset.symbol}")

        url = "https://yh-finance.p.rapidapi.com/stock/v3/get-chart?interval={time_interval}&symbol={symbol}&range={time_range}&region=US&includePrePost=false&useYfid=true&includeAdjustedClose=true&events=capitalGain%2Cdiv%2Csplit".format(
            symbol=asset.symbol,
            time_interval=time_frame.time_interval.value,
            time_range=time_frame.time_range.value,
        )

        async with aiohttp.ClientSession(headers=self.base_headers) as session:
            response = await session.get(url=url, headers=self.base_headers)
            if response.status != 200:
                await logger.async_error(f"Failed to fetch data for {asset.symbol}")
                await logger.async_debug(f"Response code: {response.status}")
                await logger.async_debug(f"Response text: {response.text()}")
                return None
            data = await response.json()
            logger.debug(f"Received Data from API : {data}")
            return AssetData(
                symbol=asset.symbol,
                info=StockInfo(**data["chart"]["result"][0]),
                created_at=datetime.now(),
            )
