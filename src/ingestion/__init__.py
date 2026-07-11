"""Data ingestion modules"""

from .market_data import MarketDataFetcher
from .congressional_trades import CongressionalTradesIngestion, create_sample_trades
from .real_data_fetcher import PublicDataFetcher, fetch_real_congressional_data

__all__ = [
    'MarketDataFetcher',
    'CongressionalTradesIngestion',
    'create_sample_trades',
    'PublicDataFetcher',
    'fetch_real_congressional_data'
]
