# Implementation Guide - Getting Started

## Step 1: Choose Your Data Source

### Option A: Quiver Quantitative API (Recommended for Starting)
**Pros**: Clean, structured data; easy to use; good documentation
**Cons**: Paid service ($15-30/month depending on plan)

```python
import requests

API_TOKEN = "your_token_here"
url = "https://api.quiverquant.com/beta/live/congresstrading"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

response = requests.get(url, headers=headers)
trades = response.json()
```

### Option B: Capitol Trades (Web Scraping)
**Pros**: Free; comprehensive data
**Cons**: Requires web scraping; may break if site changes

```python
import requests
from bs4 import BeautifulSoup

url = "https://www.capitoltrades.com/trades"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# Parse table data
```

### Option C: Official Senate/House Sites (Most Reliable but Complex)
**Pros**: Official source; free; most authoritative
**Cons**: Complex PDF parsing; inconsistent formats

```python
import requests
import pdfplumber

# Senate disclosures
url = "https://efdsearch.senate.gov/search/"
# Requires form submission and PDF parsing
```

### Option D: Use Pre-Aggregated Datasets
**Pros**: Quick start; historical data ready
**Cons**: May not be up-to-date

Sources:
- Kaggle datasets on congressional trading
- GitHub repositories with historical data
- Academic research datasets

## Step 2: Initial Project Setup

### Create Essential Files

**1. requirements.txt**
```txt
# Data manipulation
pandas>=2.1.0
numpy>=1.24.0
pyarrow>=13.0.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0  # If using PostgreSQL

# Market data
yfinance>=0.2.28
pandas-datareader>=0.10.0

# API clients
requests>=2.31.0
beautifulsoup4>=4.12.0
pdfplumber>=0.10.0

# Analysis
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0

# Jupyter
jupyter>=1.0.0
ipykernel>=6.25.0

# Testing
pytest>=7.4.0
pytest-mock>=3.11.0
pytest-cov>=4.1.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.66.0
```

**2. .env.example**
```env
# API Keys
QUIVER_API_TOKEN=your_token_here
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///data/database/trades.db
# For PostgreSQL: postgresql://user:password@localhost:5432/congressional_trades

# Analysis Settings
START_DATE=2020-01-01
END_DATE=2024-12-31
BENCHMARK_TICKER=SPY
RISK_FREE_RATE=0.04

# Data Sources
USE_QUIVER_API=true
USE_YAHOO_FINANCE=true
```

**3. .gitignore**
```gitignore
# Environment
.env
venv/
.venv/
env/

# Data
data/
outputs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

## Step 3: Create Core Data Models

**src/models/trade.py**
```python
from dataclasses import dataclass
from datetime import date
from typing import Optional
from enum import Enum

class TransactionType(Enum):
    PURCHASE = "Purchase"
    SALE = "Sale"
    EXCHANGE = "Exchange"

class Chamber(Enum):
    SENATE = "Senate"
    HOUSE = "House"

class Party(Enum):
    DEMOCRAT = "D"
    REPUBLICAN = "R"
    INDEPENDENT = "I"

@dataclass
class CongressionalTrade:
    """Represents a single congressional stock trade"""
    transaction_id: str
    politician_name: str
    politician_party: Party
    chamber: Chamber
    transaction_date: date
    disclosure_date: date
    ticker: str
    asset_description: str
    transaction_type: TransactionType
    amount_range: str
    amount_min: float
    amount_max: float
    owner: str
    
    @property
    def filing_delay_days(self) -> int:
        """Calculate days between transaction and disclosure"""
        return (self.disclosure_date - self.transaction_date).days
    
    @property
    def amount_estimated(self) -> float:
        """Estimate transaction amount as midpoint of range"""
        return (self.amount_min + self.amount_max) / 2
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'transaction_id': self.transaction_id,
            'politician_name': self.politician_name,
            'politician_party': self.politician_party.value,
            'chamber': self.chamber.value,
            'transaction_date': self.transaction_date,
            'disclosure_date': self.disclosure_date,
            'filing_delay_days': self.filing_delay_days,
            'ticker': self.ticker,
            'asset_description': self.asset_description,
            'transaction_type': self.transaction_type.value,
            'amount_range': self.amount_range,
            'amount_min': self.amount_min,
            'amount_max': self.amount_max,
            'amount_estimated': self.amount_estimated,
            'owner': self.owner,
        }
```

## Step 4: Implement Basic Data Ingestion

**src/ingestion/market_data.py**
```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional

class MarketDataFetcher:
    """Fetch historical stock prices"""
    
    def __init__(self):
        self.cache = {}
    
    def fetch_ticker_data(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with price data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"Warning: No data for {ticker}")
                return pd.DataFrame()
            
            df['ticker'] = ticker
            df.reset_index(inplace=True)
            
            # Standardize column names
            df.columns = df.columns.str.lower()
            
            return df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_tickers(
        self, 
        tickers: List[str], 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch data for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Combined DataFrame with all tickers
        """
        all_data = []
        
        for ticker in tickers:
            df = self.fetch_ticker_data(ticker, start_date, end_date)
            if not df.empty:
                all_data.append(df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def get_price_at_date(
        self, 
        ticker: str, 
        target_date: datetime
    ) -> Optional[float]:
        """
        Get closing price for a ticker on a specific date
        
        Args:
            ticker: Stock ticker
            target_date: Target date
            
        Returns:
            Closing price or None
        """
        # Fetch a small window around the target date
        start = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
        end = (target_date + timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = self.fetch_ticker_data(ticker, start, end)
        
        if df.empty:
            return None
        
        # Find closest date
        df['date'] = pd.to_datetime(df['date'])
        closest_idx = (df['date'] - target_date).abs().idxmin()
        
        return df.loc[closest_idx, 'close']
```

## Step 5: Basic Analysis Functions

**src/analysis/performance.py**
```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class PerformanceAnalyzer:
    """Calculate performance metrics for congressional trades"""
    
    def __init__(self, risk_free_rate: float = 0.04):
        self.risk_free_rate = risk_free_rate
    
    def calculate_forward_returns(
        self,
        trades_df: pd.DataFrame,
        prices_df: pd.DataFrame,
        periods: List[int] = [7, 30, 90, 180, 365]
    ) -> pd.DataFrame:
        """
        Calculate forward returns for each trade
        
        Args:
            trades_df: DataFrame with congressional trades
            prices_df: DataFrame with stock prices
            periods: List of days to calculate returns for
            
        Returns:
            DataFrame with forward returns
        """
        results = []
        
        for _, trade in trades_df.iterrows():
            ticker = trade['ticker']
            disclosure_date = pd.to_datetime(trade['disclosure_date'])
            
            # Get price at disclosure
            entry_price = self._get_price(prices_df, ticker, disclosure_date)
            
            if entry_price is None:
                continue
            
            result = {
                'transaction_id': trade['transaction_id'],
                'politician_name': trade['politician_name'],
                'ticker': ticker,
                'disclosure_date': disclosure_date,
                'entry_price': entry_price,
            }
            
            # Calculate returns for each period
            for days in periods:
                exit_date = disclosure_date + pd.Timedelta(days=days)
                exit_price = self._get_price(prices_df, ticker, exit_date)
                
                if exit_price is not None:
                    ret = (exit_price - entry_price) / entry_price
                    result[f'return_{days}d'] = ret
                else:
                    result[f'return_{days}d'] = None
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def _get_price(
        self, 
        prices_df: pd.DataFrame, 
        ticker: str, 
        date: pd.Timestamp
    ) -> float:
        """Helper to get price at specific date"""
        mask = (
            (prices_df['ticker'] == ticker) & 
            (prices_df['date'] == date)
        )
        
        matching = prices_df[mask]
        
        if matching.empty:
            # Try to find closest date within 5 days
            ticker_prices = prices_df[prices_df['ticker'] == ticker].copy()
            ticker_prices['date_diff'] = (
                ticker_prices['date'] - date
            ).abs()
            
            closest = ticker_prices[
                ticker_prices['date_diff'] <= pd.Timedelta(days=5)
            ].nsmallest(1, 'date_diff')
            
            if not closest.empty:
                return closest.iloc[0]['close']
            
            return None
        
        return matching.iloc[0]['close']
    
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
            Dictionary with summary stats
        """
        returns = returns_df[return_column].dropna()
        
        if len(returns) == 0:
            return {}
        
        stats = {
            'count': len(returns),
            'mean_return': returns.mean(),
            'median_return': returns.median(),
            'std_return': returns.std(),
            'min_return': returns.min(),
            'max_return': returns.max(),
            'win_rate': (returns > 0).mean(),
            'sharpe_ratio': self._calculate_sharpe(returns),
        }
        
        return stats
    
    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / 252)  # Daily rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def compare_to_benchmark(
        self,
        returns_df: pd.DataFrame,
        benchmark_returns: pd.Series,
        return_column: str = 'return_30d'
    ) -> Dict:
        """
        Compare performance to benchmark
        
        Args:
            returns_df: DataFrame with trade returns
            benchmark_returns: Series with benchmark returns
            return_column: Column to analyze
            
        Returns:
            Dictionary with comparison metrics
        """
        trade_returns = returns_df[return_column].dropna()
        
        if len(trade_returns) == 0:
            return {}
        
        # Calculate alpha (excess return)
        alpha = trade_returns.mean() - benchmark_returns.mean()
        
        # Calculate beta (market correlation)
        if len(trade_returns) >= 2:
            covariance = np.cov(trade_returns, benchmark_returns)[0, 1]
            variance = benchmark_returns.var()
            beta = covariance / variance if variance != 0 else 0
        else:
            beta = 0
        
        # Information ratio
        tracking_error = (trade_returns - benchmark_returns).std()
        information_ratio = alpha / tracking_error if tracking_error != 0 else 0
        
        return {
            'alpha': alpha,
            'beta': beta,
            'information_ratio': information_ratio,
            'trades_mean': trade_returns.mean(),
            'benchmark_mean': benchmark_returns.mean(),
            'outperformance_rate': (trade_returns > benchmark_returns).mean(),
        }
```

## Step 6: Create Simple Script to Start

**scripts/quick_start_analysis.py**
```python
"""
Quick start script for basic congressional trading analysis
"""
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def fetch_sample_data():
    """
    Fetch sample trade data and market data
    """
    # Sample trades (in real implementation, fetch from API/database)
    trades = [
        {
            'politician_name': 'Nancy Pelosi',
            'ticker': 'NVDA',
            'disclosure_date': '2023-07-01',
            'transaction_type': 'Purchase',
        },
        {
            'politician_name': 'Josh Gottheimer',
            'ticker': 'MSFT',
            'disclosure_date': '2023-06-15',
            'transaction_type': 'Purchase',
        },
    ]
    
    trades_df = pd.DataFrame(trades)
    trades_df['disclosure_date'] = pd.to_datetime(trades_df['disclosure_date'])
    
    return trades_df

def analyze_trades(trades_df):
    """
    Perform basic analysis on trades
    """
    results = []
    
    for _, trade in trades_df.iterrows():
        ticker = trade['ticker']
        disclosure_date = trade['disclosure_date']
        
        # Fetch price data
        start = disclosure_date
        end = disclosure_date + timedelta(days=90)
        
        stock = yf.Ticker(ticker)
        prices = stock.history(start=start, end=end)
        
        if prices.empty:
            continue
        
        # Calculate returns
        entry_price = prices.iloc[0]['Close']
        exit_price_30d = prices.iloc[min(30, len(prices)-1)]['Close']
        
        return_30d = (exit_price_30d - entry_price) / entry_price
        
        results.append({
            'politician': trade['politician_name'],
            'ticker': ticker,
            'disclosure_date': disclosure_date,
            'entry_price': entry_price,
            '30d_return': return_30d,
            '30d_return_pct': return_30d * 100,
        })
    
    return pd.DataFrame(results)

def main():
    print("Congressional Trading Analysis - Quick Start")
    print("=" * 50)
    
    # Fetch sample data
    print("\n1. Fetching sample trade data...")
    trades_df = fetch_sample_data()
    print(f"   Found {len(trades_df)} trades")
    
    # Analyze
    print("\n2. Analyzing returns...")
    results_df = analyze_trades(trades_df)
    
    # Display results
    print("\n3. Results:")
    print(results_df.to_string(index=False))
    
    # Summary statistics
    print("\n4. Summary Statistics:")
    print(f"   Mean 30-day return: {results_df['30d_return_pct'].mean():.2f}%")
    print(f"   Median 30-day return: {results_df['30d_return_pct'].median():.2f}%")
    print(f"   Win rate: {(results_df['30d_return'] > 0).mean() * 100:.1f}%")
    
    # Compare to market
    print("\n5. Benchmark Comparison:")
    spy = yf.Ticker("SPY")
    spy_prices = spy.history(
        start=results_df['disclosure_date'].min(),
        end=results_df['disclosure_date'].max() + timedelta(days=90)
    )
    
    if not spy_prices.empty:
        spy_return = (spy_prices['Close'].iloc[-1] - spy_prices['Close'].iloc[0]) / spy_prices['Close'].iloc[0]
        print(f"   S&P 500 return (same period): {spy_return * 100:.2f}%")
        print(f"   Congressional trades average: {results_df['30d_return_pct'].mean():.2f}%")

if __name__ == "__main__":
    main()
```

## Next Steps

1. **Set up project structure**:
   ```bash
   mkdir -p src/{ingestion,models,database,processing,analysis,visualization,utils}
   mkdir -p data/{raw,processed,database}
   mkdir -p scripts notebooks tests outputs
   touch src/__init__.py src/*/__init__.py
   ```

2. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Choose and test data source**:
   - Start with the quick start script above
   - Then implement full ingestion for your chosen source

4. **Build iteratively**:
   - Start with a small date range (e.g., 2023 only)
   - Test with a few politicians first
   - Validate data quality
   - Expand once the pipeline works

5. **Create analysis notebooks**:
   - Use Jupyter to explore the data
   - Prototype analysis methods
   - Visualize results
   - Document findings
