import json
from datetime import datetime, timezone

import pytest

from src.data.external.fetcher import (
    AssetData,
    CurrentTradingPeriod,
    Indicator,
    Meta,
    StockInfo,
    TradingPeriod,
)


@pytest.fixture
def sample_trading_period():
    return TradingPeriod(
        timezone="America/New_York", start=1632747600, end=1632834000, gmtoffset=-14400
    )


@pytest.fixture
def sample_current_trading_period(sample_trading_period):
    return CurrentTradingPeriod(
        pre=sample_trading_period,
        regular=sample_trading_period,
        post=sample_trading_period,
    )


@pytest.fixture
def sample_meta(sample_current_trading_period, sample_trading_period):
    return Meta(
        currency="USD",
        symbol="AAPL",
        exchangeName="NASDAQ",
        instrumentType="EQUITY",
        firstTradeDate=345479400,
        regularMarketTime=1632825600,
        gmtoffset=-14400,
        timezone="EDT",
        exchangeTimezoneName="America/New_York",
        regularMarketPrice=142.94,
        chartPreviousClose=146.92,
        previousClose=146.92,
        scale=3,
        priceHint=2,
        currentTradingPeriod=sample_current_trading_period,
        tradingPeriods=[[sample_trading_period]],
        dataGranularity="1d",
        range="1mo",
        validRanges=[
            "1d",
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
            "ytd",
            "max",
        ],
    )


@pytest.fixture
def sample_indicator():
    return Indicator(
        quote=[
            {
                "open": [142.94],
                "close": [144.84],
                "low": [142.94],
                "high": [145.09],
                "volume": [75699061],
            }
        ]
    )


@pytest.fixture
def sample_stock_info(sample_meta, sample_indicator):
    return StockInfo(
        meta=sample_meta, timestamp=[1632825600], indicators=sample_indicator
    )


@pytest.fixture
def sample_asset_data(sample_stock_info):
    return AssetData(
        symbol="AAPL", info=sample_stock_info, created_at=datetime.now(timezone.utc)
    )


def test_trading_period_serialization(sample_trading_period):
    json_data = sample_trading_period.json()
    deserialized = TradingPeriod.parse_raw(json_data)
    assert deserialized == sample_trading_period


def test_current_trading_period_serialization(sample_current_trading_period):
    json_data = sample_current_trading_period.json()
    deserialized = CurrentTradingPeriod.parse_raw(json_data)
    assert deserialized == sample_current_trading_period


def test_meta_serialization(sample_meta):
    json_data = sample_meta.json()
    deserialized = Meta.parse_raw(json_data)
    assert deserialized == sample_meta


def test_indicator_serialization(sample_indicator):
    json_data = sample_indicator.json()
    deserialized = Indicator.parse_raw(json_data)
    assert deserialized == sample_indicator


def test_stock_info_serialization(sample_stock_info):
    json_data = sample_stock_info.json()
    deserialized = StockInfo.parse_raw(json_data)
    assert deserialized == sample_stock_info


def test_asset_data_serialization(sample_asset_data):
    json_data = sample_asset_data.json()
    deserialized = AssetData.parse_raw(json_data)
    assert deserialized == sample_asset_data


def test_asset_data_to_dict(sample_asset_data):
    dict_data = sample_asset_data.to_dict()
    assert isinstance(dict_data, dict)
    assert dict_data["symbol"] == sample_asset_data.symbol
    assert isinstance(dict_data["info"], dict)
    assert isinstance(dict_data["created_at"], str)


def test_asset_data_from_dict(sample_asset_data):
    dict_data = sample_asset_data.to_dict()
    json_str = json.dumps(dict_data)
    deserialized = AssetData.parse_raw(json_str)
    assert deserialized == sample_asset_data


def test_nested_structure_preservation(sample_asset_data):
    json_str = sample_asset_data.json()
    deserialized = AssetData.parse_raw(json_str)
    assert (
        deserialized.info.meta.currentTradingPeriod.regular.timezone
        == sample_asset_data.info.meta.currentTradingPeriod.regular.timezone
    )


def test_datetime_serialization(sample_asset_data):
    json_str = sample_asset_data.json()
    deserialized = AssetData.parse_raw(json_str)
    assert deserialized.created_at == sample_asset_data.created_at


def test_list_serialization(sample_asset_data):
    json_str = sample_asset_data.json()
    deserialized = AssetData.parse_raw(json_str)
    assert deserialized.info.meta.validRanges == sample_asset_data.info.meta.validRanges


def test_empty_indicator_quote(sample_asset_data):
    sample_asset_data.info.indicators.quote = []
    json_str = sample_asset_data.json()
    deserialized = AssetData.parse_raw(json_str)
    assert deserialized.info.indicators.quote == []
