import asyncio
import json
import os
import sys
from datetime import datetime

import aiofiles

from src.application.recommendation_engine import RecommendationEngine
from src.application.sentiment_analyzer import SentimentAnalyzer
from src.config import PROMPT_DIR, STRATEGIES_DIR
from src.core.logger import get_logger, log_async
from src.data.entities import TimeFrame
from src.data.external.fetcher import AssetDataFetcher
from src.data.repository.asset_data import AssetDataRepository
from src.data.repository.sentiment import SentimentRepository
from src.data.repository.trading_strategy import (
    TradingStrategy,
    get_all_trading_strategies,
)
from src.data.value_objects import Asset, AssetType
from src.infrastructure.openai_client import (
    OpenAIClient,
    RecommendationResponse,
    SentimentResponse,
)
from src.infrastructure.prompt_loader import PromptLoader
from src.view.printers import pretty_print_recommendation
from src.view.user_interface import UserInterface

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger(__name__)

ASSETS = []

with open("data/stocks.txt", "r") as f:
    for line in f:
        if not line.strip():
            continue
        ASSETS.append(Asset(line.strip(), AssetType.STOCK))


@log_async("INFO")
async def save_recommendation(
    asset: Asset,
    time_frame: TimeFrame,
    strategy: TradingStrategy,
    sentiment: SentimentResponse,
    rec_res: RecommendationResponse,
):
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = f"recommendations/{today}"
    now = datetime.now().strftime("%H-%M-%S")
    os.makedirs(base_dir, exist_ok=True)
    async with aiofiles.open(
        f"{base_dir}/{asset.symbol}_{strategy.get_name()}_{now}.json",
        mode="w",
    ) as f:
        await f.write(
            json.dumps(
                {
                    "asset": asset.symbol,
                    "strategy": strategy.get_name(),
                    "time_range": time_frame.time_range.value,
                    "time_interval": time_frame.time_interval.value,
                    "sentiment": sentiment.to_dict(),
                    "pattern": rec_res.pattern,
                    "support_and_resistance": dict(rec_res.support_and_resistance),
                    "entry": dict(rec_res.entry),
                    "exit": dict(rec_res.exit),
                    "position": rec_res.position,
                    "recommendation": {
                        "decision": rec_res.recommendation.name,
                        "confidence": rec_res.confidence,
                        "intent": rec_res.intent,
                    },
                },
                indent=4,
            )
        )


@log_async("INFO")
async def main():
    logger.info("Starting the application")
    openai_client = OpenAIClient()
    prompt_loader = PromptLoader(PROMPT_DIR)

    sentiment_repository = SentimentRepository()
    asset_data_fetcher = AssetDataFetcher()
    asset_data_repository = AssetDataRepository()

    sentiment_analyzer = SentimentAnalyzer(openai_client, prompt_loader)
    recommendation_engine = RecommendationEngine(
        openai_client,
        prompt_loader,
        sentiment_repository,
        asset_data_fetcher,
        asset_data_repository,
    )

    strategies = get_all_trading_strategies(
        STRATEGIES_DIR, PromptLoader(STRATEGIES_DIR)
    )

    logger.debug(f"Loaded {len(strategies)} strategies")

    ui = UserInterface(ASSETS, strategies)

    user_input = await ui.get_user_input()

    if user_input is None:
        logger.error("User input is invalid")
        return

    asset, time_frame, strategy = user_input

    sentiment = await sentiment_analyzer.analyze_sentiment(
        asset=asset, time_frame=time_frame
    )

    if sentiment is None:
        logger.error("Sentiment could not be analyzed")
        return

    rec_res = await recommendation_engine.get_recommendation(
        sentiment=sentiment.sentiment,
        asset=asset,
        strategy=strategy,
        time_frame=time_frame,
    )

    if rec_res is None:
        logger.error("Recommendation could not be generated")
        return

    await save_recommendation(
        asset=asset,
        time_frame=time_frame,
        strategy=strategy,
        sentiment=sentiment,
        rec_res=rec_res,
    )
    await sentiment_repository.append_sentiment(asset=asset, sentiment=sentiment)

    logger.info("Application finished")

    pretty_print_recommendation(
        asset=asset,
        time_frame=time_frame,
        strategy=strategy,
        sentiment=sentiment,
        rec_res=rec_res,
    )


if __name__ == "__main__":
    asyncio.run(main())
