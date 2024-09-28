from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.data.entities import TimeFrame
from src.data.repository.trading_strategy import TradingStrategy
from src.data.value_objects import Asset
from src.infrastructure.openai_client import (
    RecommendationResponse,
    SentimentResponse,
)


def pretty_print_recommendation(
    asset: Asset,
    time_frame: TimeFrame,
    strategy: TradingStrategy,
    sentiment: SentimentResponse,
    rec_res: RecommendationResponse,
):
    console = Console()

    # Main panel
    main_panel = Panel(
        f"[bold cyan]Trading Recommendation for {asset.symbol}[/bold cyan]\n"
        f"[cyan]Strategy:[/cyan] {strategy.get_name()}\n"
        f"[cyan]Time Frame:[/cyan] {time_frame.time_range.value} ({time_frame.time_interval.value} intervals)",
        title="Trading Analysis",
        expand=False,
    )

    # Sentiment table
    sentiment_table = Table(title="Sentiment Analysis", box=box.ROUNDED)
    sentiment_table.add_column("Metric", style="cyan")
    sentiment_table.add_column("Value", style="green")
    sentiment_table.add_row("Sentiment", sentiment.sentiment.value)
    sentiment_table.add_row("Confidence", f"{sentiment.confidence:.2f}")
    sentiment_table.add_row("Intent", sentiment.intent)

    # Recommendation table
    rec_color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(
        rec_res.recommendation.value.upper(), "white"
    )

    rec_table = Table(title="Recommendation", box=box.ROUNDED)
    rec_table.add_column("Metric", style="cyan")
    rec_table.add_column("Value", style="green")
    rec_table.add_row(
        "Decision",
        f"[bold {rec_color}]{rec_res.recommendation.value}[/bold {rec_color}]",
    )
    rec_table.add_row("Confidence", f"{rec_res.confidence:.2f}")
    rec_table.add_row("Intent", rec_res.intent)
    rec_table.add_row("Pattern", rec_res.pattern)
    rec_table.add_row("Position", rec_res.position)

    # Support and Resistance table
    sr_table = Table(title="Support and Resistance", box=box.ROUNDED)
    sr_table.add_column("Metric", style="cyan")
    sr_table.add_column("Value", style="green")
    sr_table.add_row("Support", f"${rec_res.support_and_resistance.support:.2f}")
    sr_table.add_row("Resistance", f"${rec_res.support_and_resistance.resistance:.2f}")
    sr_table.add_row("Ratio", f"{rec_res.support_and_resistance.ratio:.2f}")

    # Entry and Exit table
    ee_table = Table(title="Entry and Exit Points", box=box.ROUNDED)
    ee_table.add_column("Point", style="cyan")
    ee_table.add_column("Price", style="green")
    ee_table.add_column("Time", style="yellow")
    ee_table.add_row("Entry", f"${rec_res.entry.price:.2f}", rec_res.entry.time)
    ee_table.add_row("Exit", f"${rec_res.exit.price:.2f}", rec_res.exit.time)

    # Print everything
    console.print(main_panel)
    console.print(sentiment_table)
    console.print(rec_table)
    console.print(sr_table)
    console.print(ee_table)
