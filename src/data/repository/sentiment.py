import json
import os
from datetime import datetime
from typing import List

import aiofiles
from pydantic import BaseModel

from src.core.logger import get_logger, log_async
from src.infrastructure.openai_client import SentimentResponse

from ..value_objects import Asset

logger = get_logger(__name__)


class SentimentHistory(BaseModel):
    sentiment: SentimentResponse
    timestamp: datetime

    def to_dict(self):
        return {
            "sentiment": self.sentiment.to_dict(),
            "timestamp": self.timestamp.isoformat(),
        }


class SentimentRepository:
    def __init__(self, base_dir: str = "repository/sentiment"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    @log_async("DEBUG")
    async def append_sentiment(self, asset: Asset, sentiment: SentimentResponse):
        logger.debug(f"Saving sentiment {sentiment} for {asset.symbol}")
        file_path = self._get_file_path(asset)
        history = await self.get_sentiment_history(asset)
        nl = [e.to_dict() for e in history]
        nl.append(
            SentimentHistory(sentiment=sentiment, timestamp=datetime.now()).to_dict()
        )
        async with aiofiles.open(file_path, mode="w") as f:
            await f.write(json.dumps(nl, indent=2))
        logger.debug(f"Sentiment {sentiment.sentiment} added for {asset.symbol}")

    @log_async("DEBUG")
    async def get_sentiment_history(self, asset: Asset) -> List[SentimentHistory]:
        logger.debug(f"Getting sentiment history for {asset.symbol}")
        file_path = self._get_file_path(asset)
        if not os.path.exists(file_path):
            return []
        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()
            loaded = json.loads(content) if content else []
            return [
                SentimentHistory(
                    sentiment=SentimentResponse(**e["sentiment"]),
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                )
                for e in loaded
            ]

    def _get_file_path(self, asset: Asset) -> str:
        return os.path.join(self.base_dir, f"{asset.symbol.replace('/', '_')}.json")
