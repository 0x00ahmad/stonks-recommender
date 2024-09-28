import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

today = date.today().strftime("%Y-%m-%d")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
YH_RAPID_API_KEY = os.getenv("YH_RAPID_API_KEY") or ""

LOG_FILEPATH = f"logs/{today}.log"

os.makedirs("logs", exist_ok=True)

STRATEGIES_DIR = "data/strategies"

PROMPT_DIR = "prompts"

SENTIMENTS_PROMPT_FILE = "sentiment_analysis.txt"
RECOMMENDATION_PROMPT_FILE = "recommendation.txt"
