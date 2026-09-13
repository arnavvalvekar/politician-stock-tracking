"""Generate comprehensive sample congressional trading dataset"""
import pandas as pd
import random
from datetime import datetime, timedelta

# Real politicians who actively trade
POLITICIANS = [
    {'name': 'Nancy Pelosi', 'party': 'D', 'chamber': 'House'},
    {'name': 'Josh Gottheimer', 'party': 'D', 'chamber': 'House'},
    {'name': 'Dan Crenshaw', 'party': 'R', 'chamber': 'House'},
    {'name': 'Tommy Tuberville', 'party': 'R', 'chamber': 'Senate'},
    {'name': 'Mark Kelly', 'party': 'D', 'chamber': 'Senate'},
    {'name': 'Rick Scott', 'party': 'R', 'chamber': 'Senate'},
]

TICKERS = ['NVDA', 'MSFT', 'AAPL', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'BAC']

AMOUNT_RANGES = [
    ('$15,001 - $50,000', 32500, 15001, 50000),
    ('$50,001 - $100,000', 75000, 50001, 100000),
    ('$100,001 - $250,000', 175000, 100001, 250000),
]

random.seed(42)
trades = []
start = datetime(2020, 1, 1)

for i in range(200):
    pol = random.choice(POLITICIANS)
    ticker = random.choice(TICKERS)
    days = random.randint(0, (datetime.now() - start).days)
    trans_date = start + timedelta(days=days)
    disc_date = trans_date + timedelta(days=random.randint(30, 45))
    trans_type = 'Purchase' if random.random() < 0.7 else 'Sale'
    amt_range, amt_est, amt_min, amt_max = random.choice(AMOUNT_RANGES)
    
    trades.append({
        'politician_name': pol['name'],
        'party': pol['party'],
        'chamber': pol['chamber'],
        'transaction_date': trans_date.strftime('%Y-%m-%d'),
        'disclosure_date': disc_date.strftime('%Y-%m-%d'),
        'ticker': ticker,
        'asset_description': f'{ticker} - Common Stock',
        'transaction_type': trans_type,
        'amount_range': amt_range,
        'amount_min': amt_min,
        'amount_max': amt_max,
        'amount_estimated': amt_est,
        'owner': 'Self',
    })

df = pd.DataFrame(trades).sort_values('transaction_date').reset_index(drop=True)
df.to_csv('data/raw/sample_congressional_trades_200.csv', index=False)
print(f"✓ Generated {len(df)} sample trades ({df['transaction_date'].min()} to {df['transaction_date'].max()})")
print(f"  Politicians: {df['politician_name'].nunique()} | Tickers: {df['ticker'].nunique()}")
print(f"  Saved to: data/raw/sample_congressional_trades_200.csv")
