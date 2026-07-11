# Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/arnavvalvekar/politician-stock-tracking.git
cd politician-stock-tracking
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

## Running the Analysis

### Option 1: Quick Test (Recommended First Step)

Run the automated test script to validate everything works:

```bash
python scripts/test_system.py
```

**Expected Output:**
```
Congressional Trading Analysis - System Test
✓ Loaded 5 sample trades
✓ Fetched 4,410 price records
✓ Calculated returns for 5 trades
30-Day Return Statistics:
  Mean Return: ~5%
  Win Rate: 80%
  Sharpe Ratio: ~8
✓ SYSTEM TEST COMPLETE
```

### Option 2: Interactive Analysis (Jupyter Notebook)

For detailed exploration and visualizations:

```bash
jupyter notebook notebooks/01_initial_analysis.ipynb
```

The notebook includes:
- Loading congressional trades
- Fetching market data
- Calculating forward returns
- Performance analysis
- Benchmark comparison (vs S&P 500)
- Visualizations and charts

### Option 3: Python Script

Use the modules directly in your own scripts:

```python
import pandas as pd
from src.ingestion.congressional_trades import create_sample_trades
from src.ingestion.market_data import MarketDataFetcher
from src.analysis.performance import PerformanceAnalyzer

# Load sample trades
trades = create_sample_trades()
trades_df = pd.DataFrame([t.to_dict() for t in trades])

# Fetch market data
market_fetcher = MarketDataFetcher()
tickers = trades_df['ticker'].unique()
prices_df = market_fetcher.fetch_multiple_tickers(
    tickers, '2023-01-01', '2024-12-31'
)

# Analyze performance
analyzer = PerformanceAnalyzer()
returns_df = analyzer.calculate_forward_returns(trades_df)

# Get summary statistics
stats = analyzer.calculate_summary_statistics(returns_df, 'return_30d')
print(f"Mean Return: {stats['mean_return']*100:.2f}%")
print(f"Win Rate: {stats['win_rate']*100:.1f}%")
print(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")

# Compare to benchmark
benchmark = analyzer.compare_to_benchmark(returns_df, 'SPY', 'return_30d')
print(f"Alpha: {benchmark['alpha_pct']:.2f}%")
```

## Adding Your Own Data

### From CSV File

Create a CSV file with these columns:

```csv
politician_name,party,chamber,transaction_date,disclosure_date,ticker,asset_description,transaction_type,amount_range,owner
Nancy Pelosi,D,House,2023-07-01,2023-08-15,NVDA,NVIDIA Corporation,Purchase,"$1,000,001 - $5,000,000",Self
```

Then load it:

```python
from src.ingestion.congressional_trades import CongressionalTradesIngestion

ingestion = CongressionalTradesIngestion()
trades = ingestion.load_from_csv('path/to/your/trades.csv')
trades_df = ingestion.to_dataframe()
```

### Manual Entry

```python
from src.ingestion.congressional_trades import CongressionalTradesIngestion

ingestion = CongressionalTradesIngestion()
trade = ingestion.create_manual_trade(
    politician_name="John Doe",
    party="D",
    chamber="Senate",
    transaction_date="2024-01-15",
    disclosure_date="2024-02-20",
    ticker="AAPL",
    transaction_type="Purchase",
    amount_range="$50,001 - $100,000"
)
```

## Database Usage (Optional)

To persist data to a database:

```python
from src.database.connection import Database

# Initialize database
db = Database()
db.initialize()

# Insert trades
db.insert_trades_bulk(trades)

# Insert stock prices
db.insert_stock_prices(prices_df)

# Query data
all_trades = db.get_all_trades()
politician_trades = db.get_trades_by_politician("Nancy Pelosi")
```

## Understanding the Output

### Performance Metrics

- **Mean Return**: Average return across all trades
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns (>1 is good, >2 is excellent)
- **Alpha**: Excess return compared to S&P 500 (positive = outperformance)
- **Beta**: Correlation with market (1 = moves with market)

### Forward Returns

The system calculates returns at multiple time horizons:
- **7d**: 1 week after disclosure + entry delay
- **30d**: 1 month after disclosure + entry delay
- **90d**: 3 months after disclosure + entry delay
- **180d**: 6 months after disclosure + entry delay
- **365d**: 1 year after disclosure + entry delay

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:

```bash
cd /path/to/politician-stock-tracking
python scripts/test_system.py
```

### Market Data Errors

If market data fetching fails:
1. Check internet connection
2. Try a different date range
3. Check if ticker symbols are valid

### Slow Performance

To speed up analysis:
1. Use caching (enabled by default)
2. Reduce the number of forward return periods
3. Analyze fewer trades initially

## Next Steps

1. ✅ Run `scripts/test_system.py` to validate installation
2. ✅ Explore `notebooks/01_initial_analysis.ipynb`
3. 🔄 Add real congressional trading data
4. 🔄 Expand analysis to multiple years
5. 🔄 Generate comprehensive reports

## Common Use Cases

### Analyze Specific Politician

```python
# Filter trades for a specific politician
politician_trades = trades_df[trades_df['politician_name'] == 'Nancy Pelosi']

# Calculate returns
returns = analyzer.calculate_forward_returns(politician_trades)

# Get performance
perf = analyzer.calculate_politician_performance(politician_trades, returns)
```

### Compare Multiple Time Periods

```python
# Analyze different holding periods
for period in [7, 30, 90, 180, 365]:
    stats = analyzer.calculate_summary_statistics(
        returns_df, 
        f'return_{period}d'
    )
    print(f"{period}-day return: {stats['mean_return']*100:.2f}%")
```

### Export Results

```python
# Export to CSV
returns_df.to_csv('outputs/results/trade_returns.csv', index=False)

# Export performance by politician
politician_perf = analyzer.calculate_politician_performance(
    trades_df, returns_df
)
politician_perf.to_csv('outputs/results/politician_performance.csv', index=False)
```

## Support

For issues or questions:
1. Check [DESIGN.md](./DESIGN.md) for architecture details
2. Check [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for code examples
3. Check [CONSIDERATIONS.md](./CONSIDERATIONS.md) for FAQs
4. Open an issue on GitHub

## Documentation

- [DESIGN.md](./DESIGN.md) - System architecture and methodology
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Directory layout
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Technical details
- [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) - Database schemas
- [CONSIDERATIONS.md](./CONSIDERATIONS.md) - Challenges and FAQs
