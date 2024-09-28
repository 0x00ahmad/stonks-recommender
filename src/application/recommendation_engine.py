import json

from src.config import RECOMMENDATION_PROMPT_FILE
from src.core.logger import get_logger, log_async
from src.data.entities import TimeFrame
from src.data.external.fetcher import AssetData, AssetDataFetcher
from src.data.repository.asset_data import (
    AssetDataRepository,
    AssetImageRepository,
)
from src.data.repository.sentiment import SentimentRepository

from ..data.repository.trading_strategy import TradingStrategy
from ..data.value_objects import Asset, Sentiment, TimeRange
from ..infrastructure.openai_client import OpenAIClient, RecommendationResponse
from ..infrastructure.prompt_loader import PromptLoader

logger = get_logger(__name__)


class RecommendationEngine:
    def __init__(
        self,
        openai_client: OpenAIClient,
        prompt_loader: PromptLoader,
        sentiment_repository: SentimentRepository,
        asset_data_fetcher: AssetDataFetcher,
        asset_data_repository: AssetDataRepository,
    ):
        self.openai_client = openai_client
        self.prompt_loader = prompt_loader
        self.sentiment_repository = sentiment_repository
        self.asset_data_fetcher = asset_data_fetcher
        self.asset_data_repository = asset_data_repository

    @log_async("INFO")
    async def get_recommendation(
        self,
        asset: Asset,
        sentiment: Sentiment,
        strategy: TradingStrategy,
        time_frame: TimeFrame,
    ) -> RecommendationResponse | None:
        await logger.async_info("Preparing to generate recommendation")

        asset_data = await self._get_asset_data(asset, time_frame)
        image_path = self._get_asset_image(asset_data, time_frame.time_range)

        await logger.async_debug("Loading the recommendation prompt")
        prompt = await self.prompt_loader.load_prompt(RECOMMENDATION_PROMPT_FILE)
        strategy_content = await strategy.get_strategy_content()

        sentiment_history = await self.sentiment_repository.get_sentiment_history(asset)
        recent_sentiments = [
            entry.sentiment.sentiment.value for entry in sentiment_history[-5:]
        ]

        formatted_prompt = prompt.format(
            asset=asset.symbol,
            asset_type=asset.asset_type.value,
            sentiment=sentiment.value,
            sentiment_history=", ".join(recent_sentiments),
            time_range=time_frame.time_range.value,
            time_interval=time_frame.time_interval.value,
            strategy=strategy_content,
            asset_data=json.dumps(asset_data.to_dict()),
        )

        await logger.async_debug(
            f"- - - Formatted prompt - - -\n{formatted_prompt}\n- - - - - - - - - - - - -"
        )

        res = await self.openai_client.get_recommendation(formatted_prompt, image_path)
        await logger.async_debug(f"Recommendation: {res}")
        if res is None:
            await logger.async_warning("Failed to generate recommendation")
            return None
        return res

    async def _get_asset_data(self, asset: Asset, time_frame: TimeFrame):
        await logger.async_debug(f"Fetching asset data for {asset.symbol}")
        asset_data = await AssetDataFetcher().fetch_asset_data(asset, time_frame)
        if asset_data is None:
            raise ValueError("Failed to fetch asset data")
        await self.asset_data_repository.save_asset_data(asset, asset_data)
        return asset_data

    def _get_asset_image(self, asset_data: AssetData, time_range: TimeRange) -> str:
        logger.debug(f"Generating candlestick chart for {asset_data.symbol}")
        return AssetImageRepository(asset_data).generate_candlestick_chart(time_range)
