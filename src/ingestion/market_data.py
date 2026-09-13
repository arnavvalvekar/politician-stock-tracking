"""Market data fetching module using yfinance"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from tqdm import tqdm
import time

from ..models.trade import StockPrice


class MarketDataFetcher:
    """Fetch historical stock prices using Yahoo Finance"""
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize the market data fetcher
        
        Args:
            cache_enabled: Whether to cache downloaded data
        """
        self.cache_enabled = cache_enabled
        self.cache: Dict[str, pd.DataFrame] = {}
    
    def fetch_ticker_data(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with price data
        """
        cache_key = f"{ticker}_{start_date}_{end_date}"
        
        # Check cache
        if use_cache and self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"Warning: No data for {ticker}")
                return pd.DataFrame()
            
            # Reset index to make Date a column
            df.reset_index(inplace=True)
            
            # Standardize column names
            df.columns = df.columns.str.lower()
            
            # Add ticker column
            df['ticker'] = ticker
            
            # Select and rename columns
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'dividends': 'dividend',
                'stock splits': 'split_ratio',
            })
            
            # Ensure we have the columns we need
            required_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in required_cols if col in df.columns]]
            
            # Add adjusted close (same as close for now)
            df['adjusted_close'] = df['close']
            
            # Convert date to date type
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Cache the result
            if self.cache_enabled:
                self.cache[cache_key] = df.copy()
            
            return df
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_tickers(
        self, 
        tickers: List[str], 
        start_date: str, 
        end_date: str,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Fetch data for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            show_progress: Whether to show progress bar
            
        Returns:
            Combined DataFrame with all tickers
        """
        all_data = []
        
        iterator = tqdm(tickers, desc="Fetching market data") if show_progress else tickers
        
        for ticker in iterator:
            df = self.fetch_ticker_data(ticker, start_date, end_date)
            if not df.empty:
                all_data.append(df)
            
            # Rate limiting - be nice to Yahoo Finance
            time.sleep(0.1)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def get_price_at_date(
        self, 
        ticker: str, 
        target_date: datetime,
        max_days_forward: int = 5
    ) -> Optional[float]:
        """
        Get closing price for a ticker on a specific date
        
        If exact date not available (market closed), finds nearest trading day
        within max_days_forward window.
        
        Args:
            ticker: Stock ticker
            target_date: Target date
            max_days_forward: Max days to look forward for price
            
        Returns:
            Closing price or None if not found
        """
        # Fetch a small window around the target date
        start = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
        end = (target_date + timedelta(days=max_days_forward)).strftime('%Y-%m-%d')
        
        df = self.fetch_ticker_data(ticker, start, end)
        
        if df.empty:
            return None
        
        # Convert target_date to date if it's datetime
        if isinstance(target_date, datetime):
            target_date = target_date.date()
        
        # Try exact date first
        exact_match = df[df['date'] == target_date]
        if not exact_match.empty:
            return float(exact_match.iloc[0]['close'])
        
        # Find closest date within max_days_forward
        df['date'] = pd.to_datetime(df['date'])
        target_dt = pd.to_datetime(target_date)
        
        # Only look forward, not backward
        future_prices = df[df['date'] >= target_dt]
        
        if not future_prices.empty:
            closest_idx = (future_prices['date'] - target_dt).abs().idxmin()
            days_diff = (future_prices.loc[closest_idx, 'date'] - target_dt).days
            
            if days_diff <= max_days_forward:
                return float(future_prices.loc[closest_idx, 'close'])
        
        return None
    
    def get_prices_for_date_range(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get all prices between start and end date
        
        Args:
            ticker: Stock ticker
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with date and close price
        """
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        df = self.fetch_ticker_data(ticker, start_str, end_str)
        
        if df.empty:
            return pd.DataFrame()
        
        return df[['date', 'close', 'ticker']]
    
    def fetch_benchmark(
        self,
        benchmark_ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch benchmark data (e.g., S&P 500)
        
        Args:
            benchmark_ticker: Benchmark ticker (e.g., 'SPY')
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with benchmark prices and returns
        """
        df = self.fetch_ticker_data(benchmark_ticker, start_date, end_date)
        
        if df.empty:
            return df
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change()
        
        # Calculate cumulative return
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        return df
    
    def calculate_returns(
        self,
        ticker: str,
        entry_date: datetime,
        exit_date: datetime
    ) -> Optional[float]:
        """
        Calculate return between entry and exit dates
        
        Args:
            ticker: Stock ticker
            entry_date: Entry date
            exit_date: Exit date
            
        Returns:
            Return as decimal (e.g., 0.15 for 15%) or None
        """
        entry_price = self.get_price_at_date(ticker, entry_date)
        exit_price = self.get_price_at_date(ticker, exit_date)
        
        if entry_price is None or exit_price is None:
            return None
        
        if entry_price == 0:
            return None
        
        return (exit_price - entry_price) / entry_price
    
    def clear_cache(self):
        """Clear the price cache"""
        self.cache.clear()
