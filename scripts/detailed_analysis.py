"""
Detailed analysis demo - run custom analysis on congressional trades
"""

import sys
import pandas as pd
from datetime import datetime
import json

sys.path.append('.')

from src.ingestion.congressional_trades import create_sample_trades
from src.ingestion.market_data import MarketDataFetcher
from src.analysis.performance import PerformanceAnalyzer


def main():
    print("=" * 70)
    print("DETAILED CONGRESSIONAL TRADING ANALYSIS")
    print("=" * 70)
    
    # Load trades
    print("\n📊 Loading trades...")
    trades = create_sample_trades()
    trades_df = pd.DataFrame([t.to_dict() for t in trades])
    
    print(f"\nTrade Details:")
    print("-" * 70)
    for _, trade in trades_df.iterrows():
        print(f"  {trade['politician_name']:20s} | {trade['ticker']:6s} | "
              f"{trade['transaction_date']} | {trade['transaction_type']:10s} | "
              f"${trade['amount_estimated']:,.0f}")
    
    # Fetch market data
    print("\n\n📈 Fetching market data...")
    market_fetcher = MarketDataFetcher()
    tickers = trades_df['ticker'].unique().tolist()
    prices_df = market_fetcher.fetch_multiple_tickers(
        tickers, '2023-01-01', datetime.now().strftime('%Y-%m-%d'),
        show_progress=False
    )
    
    # Calculate returns for all periods
    print("\n\n💰 Calculating returns across multiple time horizons...")
    analyzer = PerformanceAnalyzer()
    returns_df = analyzer.calculate_forward_returns(
        trades_df,
        periods=[7, 30, 90, 180, 365],
        show_progress=False
    )
    
    # Detailed results by holding period
    print("\n\n📊 RETURNS BY HOLDING PERIOD")
    print("=" * 70)
    
    for period in [7, 30, 90, 180, 365]:
        col = f'return_{period}d'
        stats = analyzer.calculate_summary_statistics(returns_df, col)
        
        if stats.get('count', 0) > 0:
            print(f"\n{period}-Day Returns:")
            print(f"  Count:          {stats['count']}")
            print(f"  Mean Return:    {stats['mean_return']*100:>6.2f}%")
            print(f"  Median Return:  {stats['median_return']*100:>6.2f}%")
            print(f"  Best Trade:     {stats['max_return']*100:>6.2f}%")
            print(f"  Worst Trade:    {stats['min_return']*100:>6.2f}%")
            print(f"  Win Rate:       {stats['win_rate']*100:>6.1f}%")
            print(f"  Sharpe Ratio:   {stats['sharpe_ratio']:>6.2f}")
    
    # Performance by politician
    print("\n\n👥 PERFORMANCE BY POLITICIAN (30-day returns)")
    print("=" * 70)
    
    politician_perf = analyzer.calculate_politician_performance(
        trades_df, returns_df, 'return_30d'
    )
    
    for _, pol in politician_perf.iterrows():
        print(f"\n{pol['politician_name']}:")
        print(f"  Trades:       {pol['total_trades']}")
        print(f"  Mean Return:  {pol['mean_return']*100:>6.2f}%")
        print(f"  Win Rate:     {pol['win_rate']*100:>6.1f}%")
        print(f"  Sharpe Ratio: {pol['sharpe_ratio']:>6.2f}")
    
    # Individual trade results
    print("\n\n📋 INDIVIDUAL TRADE RESULTS (30-day returns)")
    print("=" * 70)
    
    for _, ret in returns_df.iterrows():
        ret_30d = ret.get('return_30d_pct')
        if pd.notna(ret_30d):
            status = "✓ GAIN" if ret_30d > 0 else "✗ LOSS"
            print(f"{status:8s} | {ret['politician_name']:20s} | {ret['ticker']:6s} | "
                  f"Entry: ${ret['entry_price']:>7.2f} | Return: {ret_30d:>6.2f}%")
    
    # Benchmark comparison
    print("\n\n📊 BENCHMARK COMPARISON (vs S&P 500)")
    print("=" * 70)
    
    benchmark = analyzer.compare_to_benchmark(returns_df, 'SPY', 'return_30d')
    
    print(f"\nCongressional Trades:  {benchmark['trades_mean_return_pct']:>6.2f}%")
    print(f"S&P 500 Benchmark:     {benchmark['benchmark_mean_return_pct']:>6.2f}%")
    print(f"Alpha (outperformance):{benchmark['alpha_pct']:>6.2f}%")
    print(f"Beta (market correlation): {benchmark['beta']:>6.2f}")
    print(f"Information Ratio:     {benchmark['information_ratio']:>6.2f}")
    
    # Generate full report
    print("\n\n📄 GENERATING COMPREHENSIVE REPORT...")
    report = analyzer.generate_performance_report(
        trades_df, returns_df, 'SPY', 'return_30d'
    )
    
    # Save report
    with open('outputs/results/analysis_report.json', 'w') as f:
        # Convert date objects to strings for JSON serialization
        report_copy = report.copy()
        if 'metadata' in report_copy and 'date_range' in report_copy['metadata']:
            report_copy['metadata']['date_range'] = [
                str(d) for d in report_copy['metadata']['date_range']
            ]
        json.dump(report_copy, f, indent=2, default=str)
    
    print("✓ Report saved to: outputs/results/analysis_report.json")
    
    # Save detailed returns
    returns_df.to_csv('outputs/results/detailed_returns.csv', index=False)
    print("✓ Detailed returns saved to: outputs/results/detailed_returns.csv")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
