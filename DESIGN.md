# Congressional Stock Trading Analysis - System Design

## Overview
This system analyzes historical congressional stock trading data to determine if following politician trades is a profitable investment strategy. The analysis focuses on measuring returns, timing delays, and risk-adjusted performance metrics.

## 1. Data Sources

### Primary Data Sources
1. **US Senate Financial Disclosures**
   - Official source: [Senate Electronic Financial Disclosures (EFD)](https://efdsearch.senate.gov/)
   - Format: PDFs and structured data
   - Frequency: Periodic Transaction Reports (PTR) filed within 30-45 days

2. **US House Financial Disclosures**
   - Official source: [House Financial Disclosure Reports](https://disclosures-clerk.house.gov/)
   - Format: PDFs
   - Frequency: Filed within 30-45 days of transaction

3. **Third-Party Aggregators (Recommended)**
   - **Capitol Trades** (capitoltrades.com) - aggregated, structured data
   - **Quiver Quantitative API** - provides JSON API access to congressional trades
   - **Unusual Whales API** - includes congress trading data
   - **House Stock Watcher** - community-driven data collection

### Market Data Sources
- **Yahoo Finance API** - free historical stock prices
- **Alpha Vantage** - free API with rate limits
- **Polygon.io** - real-time and historical market data
- **IEX Cloud** - comprehensive market data API

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA INGESTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  Congressional Trading Data  │  Market Data (Stock Prices)  │
│  - Quiver API / Capitol      │  - Yahoo Finance             │
│  - Senate/House PDFs         │  - Alpha Vantage             │
│  - Manual uploads            │  - Polygon.io                │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA STORAGE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  Raw Data Storage        │  Processed Data Storage          │
│  - JSON files            │  - Parquet/CSV                   │
│  - SQLite/PostgreSQL     │  - Time-series database          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  • Data cleaning and normalization                          │
│  • Transaction enrichment (add market prices)               │
│  • Portfolio construction for each politician               │
│  • Calculate derived metrics                                │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                      ANALYSIS LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  • Performance attribution analysis                         │
│  • Risk-adjusted returns (Sharpe, Sortino)                 │
│  • Comparison to benchmarks (S&P 500, sector ETFs)         │
│  • Statistical significance testing                         │
│  • Timing analysis (filing delay impact)                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   VISUALIZATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  • Jupyter notebooks for exploration                        │
│  • Static reports (HTML/PDF)                                │
│  • Dashboard (future phase)                                 │
└─────────────────────────────────────────────────────────────┘
```

## 3. Data Schema

### Congressional Trades Table
```
Transaction:
- transaction_id: unique identifier
- politician_name: string
- politician_party: string (D/R/I)
- chamber: string (Senate/House)
- transaction_date: date (actual trade date)
- disclosure_date: date (when filed)
- filing_delay_days: int (disclosure - transaction)
- ticker: string
- asset_description: string
- transaction_type: enum (Purchase, Sale, Exchange)
- amount_range: string (e.g., "$15,001 - $50,000")
- amount_min: float
- amount_max: float
- amount_estimated: float (midpoint)
- owner: string (self, spouse, child, joint)
- capital_gains_over_200: boolean
```

### Market Data Table
```
StockPrice:
- ticker: string
- date: date
- open: float
- high: float
- low: float
- close: float
- adjusted_close: float
- volume: int
```

### Performance Metrics Table
```
PerformanceMetrics:
- politician_name: string
- period: string (e.g., "2020-2023")
- total_return: float
- annualized_return: float
- sharpe_ratio: float
- sortino_ratio: float
- max_drawdown: float
- win_rate: float
- avg_holding_period_days: int
- total_transactions: int
- benchmark_sp500_return: float
- alpha: float (excess return vs benchmark)
- beta: float (market correlation)
```

## 4. Analysis Methodology

### 4.1 Portfolio Construction
For each politician, construct a hypothetical portfolio that mirrors their disclosed trades:
- Start with a virtual capital base (e.g., $100,000)
- Execute trades based on disclosure date + N days (simulate delay)
- Use amount range midpoint for position sizing
- Track portfolio value over time
- Assume proportional allocation when ranges overlap

### 4.2 Return Calculation Methods

**Method 1: Trade-by-Trade Analysis**
- Calculate return from entry to exit for each stock position
- Account for partial sales
- Aggregate across all trades for overall performance

**Method 2: Time-Weighted Returns**
- Calculate daily portfolio value
- Compute cumulative returns over time
- Compare to buy-and-hold benchmarks

**Method 3: Forward-Looking Returns**
- For each disclosed purchase, measure returns at:
  - 1 week, 1 month, 3 months, 6 months, 1 year forward
- Aggregate to see typical holding period performance

### 4.3 Key Performance Metrics

1. **Absolute Performance**
   - Total return %
   - Annualized return %
   - Win rate (% of profitable trades)

2. **Risk-Adjusted Performance**
   - Sharpe Ratio: (Return - Risk-free rate) / Volatility
   - Sortino Ratio: (Return - Risk-free rate) / Downside volatility
   - Maximum Drawdown: Largest peak-to-trough decline

3. **Relative Performance**
   - Alpha: Excess return vs S&P 500
   - Beta: Correlation with market
   - Information Ratio: Risk-adjusted alpha

4. **Timing Analysis**
   - Average filing delay impact on returns
   - Compare returns at disclosure vs actual trade date
   - Measure information decay

### 4.4 Statistical Testing
- Test if returns are significantly different from:
  - Zero (are they making money?)
  - S&P 500 returns (are they beating the market?)
  - Random portfolios (is it skill or luck?)
- Use t-tests, bootstrap confidence intervals
- Control for multiple comparisons (Bonferroni correction)

### 4.5 Segmentation Analysis
Break down performance by:
- Individual politicians (who performs best?)
- Party affiliation
- Chamber (Senate vs House)
- Committee membership (especially financial committees)
- Time period (bull vs bear markets)
- Sector/industry
- Transaction size

## 5. Technology Stack

### Recommended Stack
```
Language: Python 3.11+

Data Ingestion:
- requests: API calls
- beautifulsoup4: Web scraping
- pdfplumber: PDF parsing

Data Storage:
- SQLite (for prototyping) or PostgreSQL (for production)
- pandas: Data manipulation
- pyarrow: Parquet file handling

Market Data:
- yfinance: Yahoo Finance wrapper
- alpha_vantage: Alpha Vantage wrapper
- pandas_datareader: Multiple data sources

Analysis:
- numpy: Numerical computations
- scipy: Statistical tests
- statsmodels: Advanced statistics
- scikit-learn: ML utilities

Visualization:
- matplotlib: Basic plotting
- seaborn: Statistical visualization
- plotly: Interactive charts
- jupyter: Notebooks for exploration

Testing:
- pytest: Unit testing
- pytest-mock: Mocking
```

## 6. Implementation Phases

### Phase 1: Data Foundation (Current Focus)
- [ ] Set up project structure
- [ ] Implement data ingestion for congressional trades
- [ ] Implement market data fetching
- [ ] Create database schema
- [ ] Build data processing pipeline
- [ ] Write data quality checks

### Phase 2: Core Analysis
- [ ] Implement portfolio construction logic
- [ ] Calculate basic performance metrics
- [ ] Add benchmark comparisons
- [ ] Statistical significance testing
- [ ] Generate analysis reports

### Phase 3: Advanced Analytics
- [ ] Timing/delay analysis
- [ ] Sector and industry analysis
- [ ] Machine learning for pattern detection
- [ ] Clustering politicians by trading style
- [ ] Predictive modeling

### Phase 4: Dashboard (Future)
- [ ] Web framework setup (Flask/FastAPI + React)
- [ ] Real-time data updates
- [ ] Interactive visualizations
- [ ] Strategy backtesting interface
- [ ] Alert system for new trades

## 7. Key Considerations

### Survivorship Bias
- Include politicians who left office
- Account for incomplete data

### Look-Ahead Bias
- Only use information available at disclosure time
- Simulate realistic trading delays
- Consider market hours and execution

### Transaction Costs
- Model broker commissions (or assume zero for modern brokers)
- Consider bid-ask spreads
- Account for market impact on large trades

### Regulatory Constraints
- Trades disclosed in ranges, not exact amounts
- Some trades may be missing or incomplete
- Data quality varies by source

### Data Privacy
- Use only publicly disclosed information
- Follow terms of service for data providers
- Respect rate limits on APIs

## 8. Expected Outputs

### Analysis Reports
1. **Overall Market-Beating Analysis**
   - Do politicians as a group beat the market?
   - By how much and with what confidence?

2. **Top Performers Report**
   - Ranking of politicians by various metrics
   - Consistency analysis over time

3. **Timing Impact Study**
   - How much return is lost due to disclosure delays?
   - Optimal following strategy (immediate vs delayed)

4. **Sector Insights**
   - Which sectors show strongest performance?
   - Correlation with committee assignments

5. **Strategy Recommendations**
   - Which politicians to follow
   - Which types of trades to mimic
   - Risk management guidelines

## Next Steps

Start with Phase 1 by:
1. Setting up the project structure
2. Choosing a data source (recommend starting with Quiver API or Capitol Trades)
3. Building a simple data ingestion pipeline
4. Creating sample analysis notebooks

Once historical data is collected and analyzed, you can make an informed decision about whether this strategy is worth pursuing with a live dashboard.
