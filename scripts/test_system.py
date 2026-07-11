"""
Quick test script to validate the congressional trading analysis system
"""

import sys
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append('.')

from src.ingestion.congressional_trades import create_sample_trades
from src.ingestion.market_data import MarketDataFetcher
from src.analysis.performance import PerformanceAnalyzer


def main():
    print("=" * 60)
    print("Congressional Trading Analysis - System Test")
    print("=" * 60)
    
    # Step 1: Load sample trades
    print("\n[1/5] Loading sample congressional trades...")
    trades = create_sample_trades()
    trades_df = pd.DataFrame([t.to_dict() for t in trades])
    print(f"✓ Loaded {len(trades_df)} sample trades")
    print(f"  Politicians: {', '.join(trades_df['politician_name'].unique())}")
    print(f"  Tickers: {', '.join(trades_df['ticker'].unique())}")
    
    # Step 2: Fetch market data
    print("\n[2/5] Fetching market data...")
    market_fetcher = MarketDataFetcher()
    tickers = trades_df['ticker'].unique().tolist()
    
    start_date = '2023-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    prices_df = market_fetcher.fetch_multiple_tickers(
        tickers, 
        start_date, 
        end_date,
        show_progress=False
    )
    print(f"✓ Fetched {len(prices_df)} price records for {len(tickers)} tickers")
    
    # Step 3: Calculate forward returns
    print("\n[3/5] Calculating forward returns...")
    analyzer = PerformanceAnalyzer()
    
    returns_df = analyzer.calculate_forward_returns(
        trades_df,
        periods=[30, 90, 180],  # Use fewer periods for quick test
        entry_delay_days=3,
        show_progress=False
    )
    print(f"✓ Calculated returns for {len(returns_df)} trades")
    
    # Step 4: Analyze performance
    print("\n[4/5] Analyzing performance...")
    stats = analyzer.calculate_summary_statistics(returns_df, 'return_30d')
    
    print("\n30-Day Return Statistics:")
    print(f"  Count: {stats['count']}")
    print(f"  Mean Return: {stats['mean_return']*100:.2f}%")
    print(f"  Median Return: {stats['median_return']*100:.2f}%")
    print(f"  Win Rate: {stats['win_rate']*100:.1f}%")
    print(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
    
    # Step 5: Compare to benchmark
    print("\n[5/5] Comparing to S&P 500...")
    benchmark_comparison = analyzer.compare_to_benchmark(
        returns_df,
        benchmark_ticker='SPY',
        return_column='return_30d'
    )
    
    print("\nBenchmark Comparison:")
    print(f"  Congressional Trades: {benchmark_comparison['trades_mean_return_pct']:.2f}%")
    print(f"  S&P 500: {benchmark_comparison['benchmark_mean_return_pct']:.2f}%")
    print(f"  Alpha (excess return): {benchmark_comparison['alpha_pct']:.2f}%")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("\nAll components working correctly:")
    print("  ✓ Data ingestion")
    print("  ✓ Market data fetching")
    print("  ✓ Forward returns calculation")
    print("  ✓ Performance analysis")
    print("  ✓ Benchmark comparison")
    
    print("\nNext steps:")
    print("  1. Run the Jupyter notebook: notebooks/01_initial_analysis.ipynb")
    print("  2. Add real congressional trading data")
    print("  3. Expand analysis to multiple years")
    print("  4. Generate comprehensive reports")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
