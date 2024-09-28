from dataclasses import dataclass
from enum import Enum


class AssetType(Enum):
    STOCK = "stock"
    FOREX = "forex"
    CRYPTO = "crypto"


@dataclass
class Asset:
    symbol: str
    asset_type: AssetType

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "asset_type": self.asset_type.value,
        }


class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Recommendation(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class TimeRange(Enum):
    MINS_15 = "15m"
    MINS_30 = "30m"
    HOURS_1 = "1h"
    HOURS_2 = "2h"
    HOURS_4 = "4h"
    HOURS_6 = "6h"
    HOURS_8 = "8h"
    DAY_1 = "1d"
    DAY_5 = "5d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"
    MONTH_3 = "3mo"
    MONTH_6 = "6mo"
    YEAR_1 = "1y"
    YEAR_5 = "5y"


def get_offset_by_from_time_range(time_range: TimeRange) -> dict[str, int]:
    match time_range:
        case TimeRange.MINS_15:
            return dict(minutes=15)
        case TimeRange.MINS_30:
            return dict(minutes=30)
        case TimeRange.HOURS_1:
            return dict(hours=1)
        case TimeRange.HOURS_2:
            return dict(hours=2)
        case TimeRange.HOURS_4:
            return dict(hours=4)
        case TimeRange.HOURS_6:
            return dict(hours=6)
        case TimeRange.HOURS_8:
            return dict(hours=8)
        case TimeRange.DAY_1:
            return dict(days=1)
        case TimeRange.DAY_5:
            return dict(days=5)
        case TimeRange.WEEK_1:
            return dict(weeks=1)
        case TimeRange.MONTH_1:
            return dict(months=1)
        case TimeRange.MONTH_3:
            return dict(months=3)
        case TimeRange.MONTH_6:
            return dict(months=6)
        case TimeRange.YEAR_1:
            return dict(years=1)
        case TimeRange.YEAR_5:
            return dict(years=5)
        case _:
            raise ValueError(f"Unsupported TimeRange: {time_range}")
    return dict()
