import json
from dataclasses import dataclass

from .value_objects import Asset, Recommendation, Sentiment, TimeRange


@dataclass
class TradingDecision:
    asset: Asset
    sentiment: Sentiment
    recommendation: Recommendation
    time_range: TimeRange

    def to_dict(self):
        return {
            "asset": self.asset.to_dict(),
            "sentiment": self.sentiment.value,
            "time_range": self.time_range.value,
        }

    def json(self):
        return json.dumps(self.to_dict())


@dataclass
class TimeFrame:
    time_range: TimeRange
    time_interval: TimeRange
