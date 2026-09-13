"""Performance analysis module"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from ..ingestion.market_data import MarketDataFetcher
from ..config import RISK_FREE_RATE, FORWARD_RETURN_PERIODS, DELAY_SIMULATION_DAYS


class PerformanceAnalyzer:
    """Calculate performance metrics for congressional trades"""
    
    def __init__(self, risk_free_rate: float = RISK_FREE_RATE):
        """
        Initialize performance analyzer
        
        Args:
            risk_free_rate: Annual risk-free rate (default from config)
        """
        self.risk_free_rate = risk_free_rate
        self.market_fetcher = MarketDataFetcher()
    
    def calculate_forward_returns(
        self,
        trades_df: pd.DataFrame,
        periods: List[int] = FORWARD_RETURN_PERIODS,
        entry_delay_days: int = DELAY_SIMULATION_DAYS,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Calculate forward returns for each trade
        
        Args:
            trades_df: DataFrame with congressional trades
            periods: List of days to calculate returns for (default: [7, 30, 90, 180, 365])
            entry_delay_days: Days after disclosure to simulate entry
            show_progress: Show progress during calculation
            
        Returns:
            DataFrame with forward returns for each period
        """
        results = []
        
        total = len(trades_df)
        for idx, (_, trade) in enumerate(trades_df.iterrows()):
            if show_progress and idx % 10 == 0:
                print(f"Processing trade {idx+1}/{total}...")
            
            ticker = trade['ticker']
            
            # Entry date is disclosure date + delay
            if isinstance(trade['disclosure_date'], str):
                disclosure_date = pd.to_datetime(trade['disclosure_date'])
            else:
                disclosure_date = pd.to_datetime(trade['disclosure_date'])
            
            entry_date = disclosure_date + pd.Timedelta(days=entry_delay_days)
            
            # Get entry price
            entry_price = self.market_fetcher.get_price_at_date(ticker, entry_date)
            
            if entry_price is None:
                continue
            
            result = {
                'transaction_id': trade.get('transaction_id', f"{ticker}_{disclosure_date}"),
                'politician_name': trade['politician_name'],
                'ticker': ticker,
                'transaction_date': trade['transaction_date'],
                'disclosure_date': disclosure_date,
                'entry_date': entry_date,
                'entry_price': entry_price,
                'amount_estimated': trade.get('amount_estimated', 0),
                'transaction_type': trade.get('transaction_type', 'Purchase'),
            }
            
            # Calculate returns for each period
            for days in periods:
                exit_date = entry_date + pd.Timedelta(days=days)
                exit_price = self.market_fetcher.get_price_at_date(ticker, exit_date)
                
                if exit_price is not None and entry_price > 0:
                    ret = (exit_price - entry_price) / entry_price
                    result[f'return_{days}d'] = ret
                    result[f'return_{days}d_pct'] = ret * 100
                else:
                    result[f'return_{days}d'] = None
                    result[f'return_{days}d_pct'] = None
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def calculate_summary_statistics(
        self,
        returns_df: pd.DataFrame,
        return_column: str = 'return_30d'
    ) -> Dict:
        """
        Calculate summary statistics for returns
        
        Args:
            returns_df: DataFrame with returns
            return_column: Column name for returns to analyze
            
        Returns:
            Dictionary with summary statistics
        """
        returns = returns_df[return_column].dropna()
        
        if len(returns) == 0:
            return {
                'error': 'No valid returns data',
                'count': 0
            }
        
        stats = {
            'count': len(returns),
            'mean_return': returns.mean(),
            'median_return': returns.median(),
            'std_return': returns.std(),
            'min_return': returns.min(),
            'max_return': returns.max(),
            'win_rate': (returns > 0).mean(),
            'avg_gain': returns[returns > 0].mean() if (returns > 0).any() else 0,
            'avg_loss': returns[returns < 0].mean() if (returns < 0).any() else 0,
        }
        
        # Sharpe ratio (annualized)
        if len(returns) >= 2:
            stats['sharpe_ratio'] = self._calculate_sharpe(returns)
        else:
            stats['sharpe_ratio'] = 0
        
        # Profit factor
        total_gains = returns[returns > 0].sum()
        total_losses = abs(returns[returns < 0].sum())
        stats['profit_factor'] = total_gains / total_losses if total_losses > 0 else 0
        
        return stats
    
    def calculate_politician_performance(
        self,
        trades_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        return_column: str = 'return_30d'
    ) -> pd.DataFrame:
        """
        Calculate performance metrics for each politician
        
        Args:
            trades_df: DataFrame with trades
            returns_df: DataFrame with returns
            return_column: Which return column to analyze
            
        Returns:
            DataFrame with performance by politician
        """
        # Merge trades with returns
        merged = returns_df.merge(
            trades_df[['transaction_id', 'politician_name', 'ticker']], 
            on='transaction_id',
            how='left',
            suffixes=('', '_trade')
        )
        
        # Group by politician
        politician_stats = []
        
        for politician in merged['politician_name'].unique():
            politician_data = merged[merged['politician_name'] == politician]
            politician_returns = politician_data[return_column].dropna()
            
            if len(politician_returns) == 0:
                continue
            
            stats = {
                'politician_name': politician,
                'total_trades': len(politician_data),
                'valid_returns': len(politician_returns),
                'mean_return': politician_returns.mean(),
                'median_return': politician_returns.median(),
                'std_return': politician_returns.std(),
                'win_rate': (politician_returns > 0).mean(),
                'total_estimated_volume': politician_data['amount_estimated'].sum(),
            }
            
            if len(politician_returns) >= 2:
                stats['sharpe_ratio'] = self._calculate_sharpe(politician_returns)
            else:
                stats['sharpe_ratio'] = 0
            
            politician_stats.append(stats)
        
        df = pd.DataFrame(politician_stats)
        df = df.sort_values('mean_return', ascending=False).reset_index(drop=True)
        
        return df
    
    def compare_to_benchmark(
        self,
        returns_df: pd.DataFrame,
        benchmark_ticker: str = 'SPY',
        return_column: str = 'return_30d'
    ) -> Dict:
        """
        Compare performance to benchmark
        
        Args:
            returns_df: DataFrame with trade returns
            benchmark_ticker: Benchmark ticker (default: SPY)
            return_column: Column to analyze
            
        Returns:
            Dictionary with comparison metrics
        """
        trade_returns = returns_df[return_column].dropna()
        
        if len(trade_returns) == 0:
            return {'error': 'No valid trade returns'}
        
        # Get benchmark returns for same period
        start_date = returns_df['entry_date'].min()
        end_date = returns_df['entry_date'].max() + pd.Timedelta(days=365)
        
        benchmark_df = self.market_fetcher.fetch_benchmark(
            benchmark_ticker,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if benchmark_df.empty:
            return {'error': f'No benchmark data for {benchmark_ticker}'}
        
        # Calculate average benchmark return for comparison period
        days = int(return_column.split('_')[1].replace('d', ''))
        benchmark_return = benchmark_df['close'].pct_change(days).mean()
        
        # Calculate metrics
        alpha = trade_returns.mean() - benchmark_return
        
        # Beta (simplified - using correlation as proxy)
        if len(trade_returns) >= 10:
            # Sample benchmark returns
            benchmark_sample = np.random.choice(
                benchmark_df['daily_return'].dropna(), 
                size=min(len(trade_returns), len(benchmark_df)), 
                replace=False
            )
            
            if len(benchmark_sample) == len(trade_returns):
                covariance = np.cov(trade_returns, benchmark_sample)[0, 1]
                variance = benchmark_sample.var()
                beta = covariance / variance if variance != 0 else 1
            else:
                beta = 1
        else:
            beta = 1
        
        # Information ratio
        tracking_error = (trade_returns - benchmark_return).std()
        information_ratio = alpha / tracking_error if tracking_error != 0 else 0
        
        return {
            'alpha': alpha,
            'alpha_pct': alpha * 100,
            'beta': beta,
            'information_ratio': information_ratio,
            'trades_mean_return': trade_returns.mean(),
            'trades_mean_return_pct': trade_returns.mean() * 100,
            'benchmark_mean_return': benchmark_return,
            'benchmark_mean_return_pct': benchmark_return * 100,
            'outperformance_rate': (trade_returns > benchmark_return).mean(),
            'tracking_error': tracking_error,
        }
    
    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Series of returns
            
        Returns:
            Sharpe ratio (annualized)
        """
        if len(returns) < 2:
            return 0.0
        
        # Daily risk-free rate
        daily_rf = self.risk_free_rate / 252
        
        excess_returns = returns - daily_rf
        
        if excess_returns.std() == 0:
            return 0.0
        
        # Annualize (assuming daily returns)
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
        return sharpe
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            returns: Series of returns
            
        Returns:
            Maximum drawdown (as negative decimal)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def generate_performance_report(
        self,
        trades_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        benchmark_ticker: str = 'SPY',
        return_column: str = 'return_30d'
    ) -> Dict:
        """
        Generate comprehensive performance report
        
        Args:
            trades_df: DataFrame with trades
            returns_df: DataFrame with returns
            benchmark_ticker: Benchmark ticker
            return_column: Return column to analyze
            
        Returns:
            Dictionary with comprehensive performance metrics
        """
        report = {
            'summary': self.calculate_summary_statistics(returns_df, return_column),
            'by_politician': self.calculate_politician_performance(
                trades_df, returns_df, return_column
            ).to_dict('records'),
            'vs_benchmark': self.compare_to_benchmark(
                returns_df, benchmark_ticker, return_column
            ),
        }
        
        # Add metadata
        report['metadata'] = {
            'total_trades': len(trades_df),
            'trades_with_returns': len(returns_df[return_column].dropna()),
            'date_range': (
                trades_df['transaction_date'].min(),
                trades_df['transaction_date'].max()
            ),
            'return_period_days': int(return_column.split('_')[1].replace('d', '')),
            'benchmark': benchmark_ticker,
        }
        
        return report
