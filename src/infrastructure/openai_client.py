import base64

import openai
from pydantic import BaseModel

from src.data.value_objects import Recommendation, Sentiment

from ..config import OPENAI_API_KEY

SENTIMENT_BASE_PROMPT = """You are an AI trained in financial market analysis with expertise in sentiment evaluation. Your task is to analyze the sentiment surrounding a given asset (stock) based on recent news, market trends, and provided data. Consider the following in your analysis:

1. Overall market conditions and sector-specific trends
2. Recent news and events related to the asset or its industry
3. Technical indicators and price movements
4. Comparative performance against market benchmarks
5. Analyst opinions and institutional investor actions

Provide a nuanced sentiment analysis that goes beyond simple positive/negative classifications. Consider the short-term and long-term implications of the information provided. Your analysis should be objective, data-driven, and contextualized within the broader market landscape."""

RECOMMENDATON_BASE_PROMPT = """You are an AI financial advisor with extensive knowledge of global markets, economic trends, and investment strategies. Your task is to provide a well-reasoned investment recommendation based on the following inputs:

1. Stock details
2. Current market data and recent price action
3. Sentiment analysis results
4. Historical performance and volatility
5. Relevant news and economic indicators
6. Client's investment strategy
7. Current market conditions and sector trends

Your recommendation should be clear, actionable, and tailored to the specific asset and strategy. Consider both potential risks and opportunities in your analysis. Provide a confidence level for your recommendation and explain the key factors influencing your decision. Your advice should be rational and supported by data-driven insights, not emotional or speculative."""


class SentimentResponse(BaseModel):
    sentiment: Sentiment
    confidence: float
    intent: str

    def to_dict(self):
        return {
            "sentiment": self.sentiment.value,
            "confidence": self.confidence,
            "intent": self.intent,
        }


class SupportAndResistance(BaseModel):
    support: float
    resistance: float
    ratio: float


class EntryExit(BaseModel):
    price: float
    time: str


class RecommendationResponse(BaseModel):
    recommendation: Recommendation
    confidence: float
    intent: str
    pattern: str
    position: str
    support_and_resistance: SupportAndResistance
    entry: EntryExit
    exit: EntryExit


class OpenAIClient:
    def __init__(self):
        self.model = "gpt-4o-2024-08-06"
        self.client = openai.AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            max_retries=3,
        )

    async def get_sentiment(self, prompt: str) -> SentimentResponse | None:
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SENTIMENT_BASE_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format=SentimentResponse,
        )
        return response.choices[0].message.parsed

    async def get_recommendation(
        self, prompt: str, image_path: str
    ) -> RecommendationResponse | None:
        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        file_extension = image_path.split(".")[-1].lower()
        mime_type = mime_types.get(file_extension, "application/octet-stream")

        with open(image_path, "rb") as img_file:
            img_b64_str = base64.b64encode(img_file.read()).decode("utf-8")

        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": RECOMMENDATON_BASE_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{img_b64_str}"
                            },
                        },
                    ],
                },
            ],
            response_format=RecommendationResponse,
        )
        return response.choices[0].message.parsed
