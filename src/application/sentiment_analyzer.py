from datetime import date

from src.config import SENTIMENTS_PROMPT_FILE
from src.core.logger import get_logger, log_async
from src.data.entities import TimeFrame
from src.data.value_objects import Asset
from src.infrastructure.openai_client import OpenAIClient, SentimentResponse
from src.infrastructure.prompt_loader import PromptLoader

logger = get_logger(__name__)


class SentimentAnalyzer:
    def __init__(
        self,
        openai_client: OpenAIClient,
        prompt_loader: PromptLoader,
    ):
        self.openai_client = openai_client
        self.prompt_loader = prompt_loader

    @log_async("INFO")
    async def analyze_sentiment(
        self, asset: Asset, time_frame: TimeFrame
    ) -> SentimentResponse | None:
        await logger.async_info(f"Analyzing sentiment for {asset.symbol}")
        prompt = await self.prompt_loader.load_prompt(SENTIMENTS_PROMPT_FILE)
        now = date.today()
        prompt = prompt.format(
            asset=asset.symbol,
            asset_type=asset.asset_type,
            time_range=time_frame.time_range.value,
            time_interval=time_frame.time_interval.value,
            now=now,
        )
        await logger.async_debug(f"Prompt: {prompt}")
        res = await self.openai_client.get_sentiment(prompt)
        if res is None:
            await logger.async_error("Failed to analyze sentiment")
            return None
        logger.debug(f"Sentiment: {res}")
        return res
