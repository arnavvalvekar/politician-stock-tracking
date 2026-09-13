"""
Test script for fetching and analyzing real congressional trading data
"""

import sys
sys.path.append('.')

import pandas as pd
from datetime import datetime

from src.ingestion.real_data_fetcher import fetch_real_congressional_data
from src.processing.data_validator import DataValidator
from src.analysis.performance import PerformanceAnalyzer
from src.ingestion.market_data import MarketDataFetcher


def main():
    print("="*70)
    print("REAL CONGRESSIONAL TRADING DATA ANALYSIS")
    print("="*70)
    
    # Step 1: Fetch real data
    print("\n[STEP 1] Fetching real congressional trading data...")
    print("Note: This may take a moment as we download from public sources")
    print("-"*70)
    
    # Fetch last 2 years of data for reasonable dataset size
    start_date = "2022-01-01"
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    raw_df, trades = fetch_real_congressional_data(
        start_date=start_date,
        end_date=end_date,
        chambers=['House', 'Senate']
    )
    
    if raw_df.empty:
        print("\n⚠ Unable to fetch data from public sources")
        print("Public S3 buckets may be unavailable or deprecated")
        print("\nFalling back to sample data for demonstration...")
        
        from src.ingestion.congressional_trades import create_sample_trades
        trades = create_sample_trades()
        trades_df = pd.DataFrame([t.to_dict() for t in trades])
    else:
        # Step 2: Validate and clean data
        print("\n[STEP 2] Validating and cleaning data...")
        print("-"*70)
        
        validator = DataValidator()
        clean_df, validation_report = validator.validate_dataframe(raw_df)
        
        # Enrich with party data
        clean_df = validator.enrich_with_party_data(clean_df)
        
        # Convert to trades
        from src.ingestion.congressional_trades import CongressionalTradesIngestion
        ingestion = CongressionalTradesIngestion()
        trades = ingestion.load_from_dataframe(clean_df)
        trades_df = ingestion.to_dataframe()
        
        print(f"\n{validator.get_quality_report()}")
    
    # Step 3: Sample analysis
    print("\n[STEP 3] Running sample analysis...")
    print("-"*70)
    
    # Analyze a subset (top 50 trades for speed)
    print(f"\nTotal trades available: {len(trades_df)}")
    print("Analyzing sample of 50 most recent trades for performance...")
    
    # Get 50 most recent trades
    sample_df = trades_df.nlargest(50, 'disclosure_date')
    
    print(f"\nSample details:")
    print(f"  Date range: {sample_df['transaction_date'].min()} to {sample_df['transaction_date'].max()}")
    print(f"  Politicians: {sample_df['politician_name'].nunique()}")
    print(f"  Tickers: {sample_df['ticker'].nunique()}")
    
    # Get unique tickers
    tickers = sample_df['ticker'].unique().tolist()[:20]  # Limit to 20 tickers
    print(f"\n  Fetching market data for {len(tickers)} tickers...")
    
    # Fetch market data
    market_fetcher = MarketDataFetcher()
    prices_df = market_fetcher.fetch_multiple_tickers(
        tickers,
        start_date,
        end_date,
        show_progress=False
    )
    
    # Calculate returns (using smaller subset)
    sample_with_prices = sample_df[sample_df['ticker'].isin(tickers)].head(20)
    
    print(f"\n  Calculating returns for {len(sample_with_prices)} trades...")
    analyzer = PerformanceAnalyzer()
    returns_df = analyzer.calculate_forward_returns(
        sample_with_prices,
        periods=[30, 90],  # Just 30 and 90 day for speed
        show_progress=False
    )
    
    # Summary statistics
    if not returns_df.empty and returns_df['return_30d'].notna().any():
        stats = analyzer.calculate_summary_statistics(returns_df, 'return_30d')
        
        print("\n[STEP 4] Results Summary")
        print("="*70)
        print(f"\n30-Day Return Analysis:")
        print(f"  Trades analyzed:   {stats['count']}")
        print(f"  Mean return:       {stats['mean_return']*100:>6.2f}%")
        print(f"  Median return:     {stats['median_return']*100:>6.2f}%")
        print(f"  Win rate:          {stats['win_rate']*100:>6.1f}%")
        print(f"  Best trade:        {stats['max_return']*100:>6.2f}%")
        print(f"  Worst trade:       {stats['min_return']*100:>6.2f}%")
        print(f"  Sharpe ratio:      {stats['sharpe_ratio']:>6.2f}")
        
        # Top performers
        if len(returns_df) > 0:
            print(f"\n📊 Top 5 Performing Trades (30-day):")
            top_trades = returns_df.nlargest(5, 'return_30d_pct')[
                ['politician_name', 'ticker', 'entry_date', 'return_30d_pct']
            ]
            for _, trade in top_trades.iterrows():
                print(f"  {trade['politician_name']:20s} | {trade['ticker']:6s} | {trade['return_30d_pct']:>6.2f}%")
    
    print("\n" + "="*70)
    print("✅ REAL DATA ANALYSIS COMPLETE")
    print("="*70)
    
    # Statistics
    print(f"\nDataset Statistics:")
    print(f"  Total trades fetched:     {len(raw_df) if not raw_df.empty else 'N/A'}")
    print(f"  Valid trades:             {len(trades_df)}")
    print(f"  Date range:               {trades_df['transaction_date'].min()} to {trades_df['transaction_date'].max()}")
    print(f"  Unique politicians:       {trades_df['politician_name'].nunique()}")
    print(f"  Unique tickers:           {trades_df['ticker'].nunique()}")
    
    # Save results
    print(f"\nSaving results...")
    trades_df.to_csv('outputs/results/real_trades_dataset.csv', index=False)
    print(f"✓ Saved to: outputs/results/real_trades_dataset.csv")


if __name__ == "__main__":
    main()
