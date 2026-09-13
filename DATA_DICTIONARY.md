# Data Dictionary

## Congressional Trades Schema

### trades table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `transaction_id` | STRING (PK) | Unique identifier for the transaction | "PELOSI_2023_07_15_NVDA_001" | Generated from politician + date + ticker |
| `politician_name` | STRING | Full name of the politician | "Nancy Pelosi" | Standardized format: "First Last" |
| `politician_party` | ENUM | Political party affiliation | "D", "R", "I" | D=Democrat, R=Republican, I=Independent |
| `chamber` | ENUM | Congressional chamber | "Senate", "House" | |
| `state` | STRING | State represented | "CA", "TX" | Two-letter state code |
| `district` | STRING | Congressional district (House only) | "CA-12" | NULL for Senate |
| `transaction_date` | DATE | Date when trade was executed | 2023-07-15 | Actual trade date |
| `disclosure_date` | DATE | Date when trade was disclosed | 2023-08-20 | Date filed with clerk |
| `filing_delay_days` | INTEGER | Days between transaction and disclosure | 36 | Calculated: disclosure_date - transaction_date |
| `ticker` | STRING | Stock ticker symbol | "NVDA", "AAPL" | Uppercase, standardized |
| `asset_description` | STRING | Description of the asset | "NVIDIA Corporation - Common Stock" | From disclosure form |
| `asset_type` | STRING | Type of asset | "Stock", "Stock Option", "Bond" | Categorized |
| `transaction_type` | ENUM | Type of transaction | "Purchase", "Sale", "Exchange" | |
| `amount_range` | STRING | Disclosed amount range | "$15,001 - $50,000" | As reported |
| `amount_min` | FLOAT | Minimum amount | 15001.00 | Lower bound of range |
| `amount_max` | FLOAT | Maximum amount | 50000.00 | Upper bound of range |
| `amount_estimated` | FLOAT | Estimated amount (midpoint) | 32500.50 | (amount_min + amount_max) / 2 |
| `owner` | STRING | Who owns the asset | "Self", "Spouse", "Child", "Joint" | From disclosure |
| `comment` | TEXT | Additional notes | "Partial sale" | Optional field |
| `capital_gains_over_200` | BOOLEAN | Capital gains > $200 | TRUE, FALSE | From disclosure checkbox |
| `filing_id` | STRING | Original filing document ID | "20230820-001" | Reference to source document |
| `data_source` | STRING | Source of the data | "Quiver API", "Senate EFD" | Tracking data provenance |
| `created_at` | TIMESTAMP | When record was created | 2024-01-15 10:30:00 | System timestamp |
| `updated_at` | TIMESTAMP | When record was last updated | 2024-01-15 10:30:00 | System timestamp |

### Amount Ranges (STOCK Act Disclosure Categories)

| Range Code | Amount Range | Estimated Midpoint |
|-----------|--------------|-------------------|
| A | $1,001 - $15,000 | $8,000 |
| B | $15,001 - $50,000 | $32,500 |
| C | $50,001 - $100,000 | $75,000 |
| D | $100,001 - $250,000 | $175,000 |
| E | $250,001 - $500,000 | $375,000 |
| F | $500,001 - $1,000,000 | $750,000 |
| G | $1,000,001 - $5,000,000 | $3,000,000 |
| H | $5,000,001 - $25,000,000 | $15,000,000 |
| I | $25,000,001 - $50,000,000 | $37,500,000 |
| J | Over $50,000,000 | $50,000,000+ |

## Market Data Schema

### stock_prices table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `ticker` | STRING (PK) | Stock ticker symbol | "NVDA" | Part of composite key |
| `date` | DATE (PK) | Trading date | 2023-07-15 | Part of composite key |
| `open` | FLOAT | Opening price | 456.23 | |
| `high` | FLOAT | Highest price during day | 462.50 | |
| `low` | FLOAT | Lowest price during day | 454.10 | |
| `close` | FLOAT | Closing price | 460.75 | Unadjusted close |
| `adjusted_close` | FLOAT | Adjusted closing price | 459.80 | Adjusted for splits/dividends |
| `volume` | BIGINT | Trading volume | 45234100 | Number of shares traded |
| `dividend` | FLOAT | Dividend paid (if any) | 0.00 | NULL if no dividend |
| `split_ratio` | FLOAT | Stock split ratio (if any) | 1.0 | e.g., 2.0 for 2-for-1 split |
| `data_source` | STRING | Source of the data | "Yahoo Finance" | |
| `created_at` | TIMESTAMP | When record was created | 2024-01-15 10:30:00 | |

### Index: `idx_ticker_date` on `(ticker, date)`
### Index: `idx_date` on `(date)`

## Politicians Schema

### politicians table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `politician_id` | STRING (PK) | Unique identifier | "PELOSI_NANCY" | Generated from name |
| `full_name` | STRING | Full name | "Nancy Pelosi" | |
| `first_name` | STRING | First name | "Nancy" | |
| `last_name` | STRING | Last name | "Pelosi" | |
| `party` | ENUM | Political party | "D", "R", "I" | Current or most recent |
| `chamber` | ENUM | Congressional chamber | "Senate", "House" | Current or most recent |
| `state` | STRING | State represented | "CA" | |
| `district` | STRING | District (House only) | "CA-12" | NULL for Senate |
| `committees` | JSON | Committee memberships | ["Financial Services", "Budget"] | Array of committees |
| `start_date` | DATE | Start of service | 1987-01-06 | First day in Congress |
| `end_date` | DATE | End of service | NULL | NULL if currently serving |
| `is_active` | BOOLEAN | Currently serving | TRUE | |
| `website` | STRING | Official website | "https://..." | |
| `created_at` | TIMESTAMP | Record creation time | 2024-01-15 10:30:00 | |
| `updated_at` | TIMESTAMP | Last update time | 2024-01-15 10:30:00 | |

## Performance Metrics Schema

### performance_metrics table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `metric_id` | STRING (PK) | Unique identifier | "PELOSI_2020_2023" | politician_id + period |
| `politician_id` | STRING (FK) | References politicians table | "PELOSI_NANCY" | |
| `politician_name` | STRING | Full name | "Nancy Pelosi" | Denormalized for convenience |
| `analysis_period_start` | DATE | Start of analysis period | 2020-01-01 | |
| `analysis_period_end` | DATE | End of analysis period | 2023-12-31 | |
| `total_transactions` | INTEGER | Number of transactions | 156 | |
| `total_purchases` | INTEGER | Number of purchases | 98 | |
| `total_sales` | INTEGER | Number of sales | 58 | |
| `total_volume` | FLOAT | Total dollar volume | 5250000.00 | Estimated |
| `unique_tickers` | INTEGER | Number of unique stocks | 42 | |
| `avg_position_size` | FLOAT | Average transaction amount | 33654.00 | |
| `total_return_pct` | FLOAT | Total return percentage | 45.8 | Portfolio return |
| `annualized_return_pct` | FLOAT | Annualized return | 12.3 | CAGR |
| `sharpe_ratio` | FLOAT | Risk-adjusted return | 1.45 | (Return - RFR) / Volatility |
| `sortino_ratio` | FLOAT | Downside risk-adjusted | 1.82 | Uses downside deviation |
| `max_drawdown_pct` | FLOAT | Maximum drawdown | -15.3 | Largest peak-to-trough decline |
| `volatility_pct` | FLOAT | Return volatility (std dev) | 18.5 | Annualized |
| `win_rate_pct` | FLOAT | Percentage of winning trades | 64.5 | |
| `avg_gain_pct` | FLOAT | Average gain on winners | 23.4 | |
| `avg_loss_pct` | FLOAT | Average loss on losers | -8.7 | |
| `profit_factor` | FLOAT | Ratio of gains to losses | 2.69 | |
| `avg_holding_period_days` | INTEGER | Average days held | 127 | |
| `median_holding_period_days` | INTEGER | Median days held | 95 | |
| `benchmark_return_pct` | FLOAT | S&P 500 return (same period) | 38.2 | |
| `alpha_pct` | FLOAT | Excess return vs benchmark | 7.6 | |
| `beta` | FLOAT | Market correlation | 0.85 | |
| `information_ratio` | FLOAT | Risk-adjusted alpha | 0.67 | Alpha / Tracking Error |
| `tracking_error_pct` | FLOAT | Volatility of excess returns | 11.3 | |
| `calculated_at` | TIMESTAMP | When metrics were calculated | 2024-01-15 10:30:00 | |

### trade_returns table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `return_id` | STRING (PK) | Unique identifier | "PELOSI_2023_07_15_NVDA_001_30D" | transaction_id + period |
| `transaction_id` | STRING (FK) | References trades table | "PELOSI_2023_07_15_NVDA_001" | |
| `politician_name` | STRING | Full name | "Nancy Pelosi" | |
| `ticker` | STRING | Stock ticker | "NVDA" | |
| `entry_date` | DATE | Entry date (disclosure + delay) | 2023-08-20 | Simulated entry |
| `entry_price` | FLOAT | Entry price | 450.25 | Price at entry_date |
| `holding_period_days` | INTEGER | Number of days held | 30 | |
| `exit_date` | DATE | Exit date | 2023-09-19 | entry_date + holding_period |
| `exit_price` | FLOAT | Exit price | 475.80 | Price at exit_date |
| `return_pct` | FLOAT | Return percentage | 5.68 | (exit - entry) / entry * 100 |
| `return_absolute` | FLOAT | Dollar return | 1846.25 | Based on estimated position size |
| `benchmark_return_pct` | FLOAT | S&P 500 return (same period) | 2.3 | |
| `excess_return_pct` | FLOAT | Return vs benchmark | 3.38 | return_pct - benchmark_return |
| `calculated_at` | TIMESTAMP | When calculated | 2024-01-15 10:30:00 | |

## Portfolio Holdings Schema

### portfolio_holdings table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `holding_id` | STRING (PK) | Unique identifier | "PELOSI_NVDA_2023_07_15" | |
| `politician_id` | STRING (FK) | References politicians | "PELOSI_NANCY" | |
| `ticker` | STRING | Stock ticker | "NVDA" | |
| `acquisition_date` | DATE | When position opened | 2023-08-20 | Disclosure date + delay |
| `shares` | FLOAT | Number of shares | 72.22 | Estimated from amount range |
| `cost_basis` | FLOAT | Average cost per share | 450.25 | |
| `current_shares` | FLOAT | Current shares held | 72.22 | After any partial sales |
| `current_value` | FLOAT | Current market value | 34248.00 | shares * current_price |
| `unrealized_gain_loss` | FLOAT | Unrealized P&L | 1746.75 | current_value - cost_basis |
| `realized_gain_loss` | FLOAT | Realized P&L | 0.00 | From closed portions |
| `is_closed` | BOOLEAN | Position closed | FALSE | |
| `close_date` | DATE | When position closed | NULL | NULL if still open |
| `updated_at` | TIMESTAMP | Last update | 2024-01-15 10:30:00 | |

## Benchmark Data Schema

### benchmark_returns table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `benchmark_ticker` | STRING (PK) | Benchmark identifier | "SPY" | Part of composite key |
| `date` | DATE (PK) | Date | 2023-07-15 | Part of composite key |
| `close_price` | FLOAT | Closing price | 450.12 | |
| `daily_return_pct` | FLOAT | Daily return | 0.54 | |
| `cumulative_return_pct` | FLOAT | Cumulative return (YTD) | 18.3 | |
| `volatility_20d` | FLOAT | 20-day rolling volatility | 12.5 | Annualized |
| `data_source` | STRING | Data source | "Yahoo Finance" | |

Common benchmarks to track:
- SPY (S&P 500)
- QQQ (NASDAQ-100)
- DIA (Dow Jones)
- IWM (Russell 2000)
- Sector ETFs (XLF, XLK, XLE, etc.)

## Data Quality Flags

### data_quality_issues table

| Column Name | Data Type | Description | Example | Notes |
|------------|-----------|-------------|---------|-------|
| `issue_id` | STRING (PK) | Unique identifier | "DQ_001234" | |
| `record_id` | STRING | Reference to affected record | "PELOSI_2023_07_15_NVDA_001" | |
| `table_name` | STRING | Which table | "trades" | |
| `issue_type` | ENUM | Type of issue | "MISSING_PRICE", "INVALID_TICKER" | |
| `severity` | ENUM | Severity level | "WARNING", "ERROR" | |
| `description` | TEXT | Issue description | "No price data found for date" | |
| `detected_at` | TIMESTAMP | When detected | 2024-01-15 10:30:00 | |
| `resolved` | BOOLEAN | Issue resolved | FALSE | |
| `resolved_at` | TIMESTAMP | When resolved | NULL | |

## Notes on Data Types

### Enums
Define as constants in code or database enum types:
- `Party`: ['D', 'R', 'I']
- `Chamber`: ['Senate', 'House']
- `TransactionType`: ['Purchase', 'Sale', 'Exchange', 'Purchase (Partial)', 'Sale (Partial)']
- `AssetType`: ['Stock', 'Stock Option', 'Corporate Bond', 'Municipal Bond', 'ETF', 'Mutual Fund']
- `IssueSeverity`: ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
- `IssueType`: ['MISSING_PRICE', 'INVALID_TICKER', 'DUPLICATE_RECORD', 'OUTLIER_RETURN', 'MISSING_DISCLOSURE_DATE']

### Indexes
Recommended indexes for performance:
- `trades`: (politician_name, transaction_date), (ticker, transaction_date), (disclosure_date)
- `stock_prices`: (ticker, date), (date)
- `performance_metrics`: (politician_id, analysis_period_start)
- `trade_returns`: (transaction_id), (politician_name, entry_date)
- `portfolio_holdings`: (politician_id, ticker), (politician_id, is_closed)

### Foreign Key Relationships
- `trades.politician_name` → `politicians.full_name`
- `performance_metrics.politician_id` → `politicians.politician_id`
- `trade_returns.transaction_id` → `trades.transaction_id`
- `portfolio_holdings.politician_id` → `politicians.politician_id`
