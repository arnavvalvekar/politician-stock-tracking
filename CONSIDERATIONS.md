# Analysis Considerations & FAQs

## Key Challenges & Limitations

### 1. Disclosure Delay Problem

**Challenge**: Trades are disclosed 30-45 days after execution (STOCK Act requirement: within 45 days)

**Impact on Returns**:
- You can't trade at politician's execution price
- Must trade at disclosure date + processing time
- Market may have already moved significantly

**Mitigation Strategies**:
- Quantify the "delay cost" by comparing returns at transaction date vs disclosure date
- Focus on longer-term holdings where delay matters less
- Look for trades in less liquid stocks where information advantage persists longer

**Analysis Approach**:
```python
# Compare returns at different entry points
returns_at_transaction = calculate_returns(entry_date=transaction_date)
returns_at_disclosure = calculate_returns(entry_date=disclosure_date)
returns_at_disclosure_plus_3d = calculate_returns(entry_date=disclosure_date + 3 days)

delay_cost = returns_at_transaction - returns_at_disclosure
```

### 2. Transaction Amount Uncertainty

**Challenge**: Exact transaction amounts not disclosed, only ranges

**Example**: "$50,001 - $100,000" could be $50,002 or $99,999

**Impact**:
- Position sizing is estimated
- Portfolio construction is approximate
- Return calculations use midpoint estimates

**Mitigation Strategies**:
- Use midpoint as best estimate
- Run sensitivity analysis with min/max bounds
- Aggregate many trades to smooth out estimation errors

**Analysis Approach**:
```python
# Sensitivity analysis
returns_min = calculate_returns(amount=amount_min)
returns_mid = calculate_returns(amount=amount_estimated)
returns_max = calculate_returns(amount=amount_max)

# Report range of possible outcomes
print(f"Return range: {returns_min:.2f}% to {returns_max:.2f}%")
```

### 3. Missing or Incomplete Data

**Common Issues**:
- Late or missing disclosures
- Ticker symbols not standardized (especially options, bonds)
- "Various" or "See attached" instead of specific ticker
- Amended filings that correct earlier disclosures
- Politicians who leave office mid-analysis period

**Mitigation**:
- Implement robust data validation
- Manual review of questionable entries
- Track data quality metrics
- Document exclusions and their impact

**Data Quality Checks**:
```python
# Flag suspicious records
checks = {
    'missing_ticker': df['ticker'].isnull(),
    'invalid_ticker': ~df['ticker'].str.match(r'^[A-Z]{1,5}$'),
    'future_transaction': df['transaction_date'] > pd.Timestamp.now(),
    'negative_delay': df['filing_delay_days'] < 0,
    'excessive_delay': df['filing_delay_days'] > 180,
}
```

### 4. Survivorship Bias

**Challenge**: Politicians who performed poorly may have different trading patterns

**Types**:
- Politicians who lost re-election
- Politicians who retired
- Politicians who faced ethics investigations
- Incomplete data for early-career politicians

**Mitigation**:
- Include all politicians, not just "successful" ones
- Weight by number of trades or time period
- Analyze cohorts separately

### 5. Look-Ahead Bias

**Challenge**: Using information not available at the time of decision

**Common Mistakes**:
- Using adjusted prices from future splits/dividends at historical entry point
- Including trades disclosed after analysis period end
- Using ex-post optimal exit timing

**Prevention**:
```python
# Use point-in-time data only
def get_price_at_date(ticker, date, max_forward_days=3):
    """
    Get price as of date, without looking ahead
    - Use unadjusted prices for entry
    - Apply adjustments only to future prices
    - Allow small forward window for market hour issues
    """
    pass
```

### 6. Transaction Cost Assumptions

**Real-World Costs**:
- Broker commissions: $0-10 per trade (many now $0)
- Bid-ask spread: 0.01-0.5% for liquid stocks
- Market impact: minimal for retail sizes
- Slippage: 0.1-0.3% for realistic execution

**Analysis Approach**:
```python
# Model different cost scenarios
def calculate_net_returns(gross_returns, cost_scenario='conservative'):
    costs = {
        'optimistic': 0.001,   # 0.1% per trade
        'realistic': 0.003,    # 0.3% per trade
        'conservative': 0.005, # 0.5% per trade
    }
    
    cost_pct = costs[cost_scenario]
    # Subtract costs at entry and exit
    net_returns = gross_returns - (2 * cost_pct)
    return net_returns
```

### 7. Tax Implications (Not Modeled in Initial Analysis)

**Considerations**:
- Short-term vs long-term capital gains
- Wash sale rules
- Tax loss harvesting opportunities

**Note**: Initial analysis focuses on pre-tax returns. Tax impact varies by individual situation.

## Statistical Considerations

### Sample Size Issues

**Adequate Sample Sizes**:
- Individual politician: 50+ trades for meaningful analysis
- Aggregated analysis: 500+ trades across multiple politicians
- Time period: At least 2-3 years to include market cycles

**Small Sample Risks**:
- High variance in performance metrics
- Outliers have outsized impact
- Statistical significance difficult to achieve

### Multiple Comparisons Problem

**Challenge**: Testing many politicians/strategies increases false positive rate

**Example**:
- Test 100 politicians at p=0.05 significance level
- Expect ~5 to show "significant" results by chance alone

**Solution**: Bonferroni correction or False Discovery Rate control
```python
from statsmodels.stats.multitest import multipletests

# Adjust p-values for multiple comparisons
reject, pvals_corrected, _, _ = multipletests(
    pvals, 
    alpha=0.05, 
    method='fdr_bh'  # Benjamini-Hochberg procedure
)
```

### Regime Changes & Non-Stationarity

**Challenge**: Market conditions change over time

**Considerations**:
- Bull market (2020-2021) vs bear market (2022)
- Low interest rates (2010-2021) vs higher rates (2022+)
- Sector rotation and style drift

**Analysis Approach**:
- Break analysis into sub-periods
- Test robustness across market regimes
- Use rolling window analysis

```python
# Rolling performance analysis
window_size = 252  # 1 year
rolling_returns = []

for i in range(len(returns) - window_size):
    window_returns = returns[i:i+window_size]
    rolling_returns.append({
        'date': dates[i+window_size],
        'return': window_returns.mean(),
        'sharpe': calculate_sharpe(window_returns),
    })
```

## Interpretation Guidelines

### What Would Be Meaningful Results?

**Strong Evidence of Skill**:
- Consistent outperformance (3+ years)
- Sharpe ratio > 1.5
- Win rate > 60%
- Alpha > 5% annually with p < 0.01
- Outperformance across market regimes

**Weak/Inconclusive Evidence**:
- Outperformance in only 1-2 years
- High returns but also high volatility (Sharpe < 1.0)
- Significant results for only a few politicians
- Performance disappears after adjusting for factors (size, value, momentum)

**No Evidence**:
- Returns not significantly different from benchmark
- High variance with no consistent pattern
- Performance driven by 1-2 lucky trades

### Common Pitfalls in Interpretation

1. **Confusing Luck with Skill**
   - One good year doesn't prove skill
   - Need statistical significance tests
   - Consider prior probability (most investors don't beat market)

2. **Ignoring Risk**
   - High returns with high volatility isn't necessarily good
   - Use risk-adjusted metrics (Sharpe, Sortino)
   - Consider maximum drawdown

3. **Cherry-Picking Results**
   - Don't just highlight best performers
   - Report distribution of performance
   - Include failed strategies

4. **Overfitting**
   - Finding patterns in noise
   - Complex strategies that work on historical data but not future
   - Use out-of-sample testing

## Practical Implementation Challenges

### Data Quality & Cleaning

**Time Requirements**:
- Expect to spend 50%+ of time on data cleaning
- Many edge cases and exceptions
- Manual review often needed

**Common Issues**:
```python
# Examples of messy data
problematic_tickers = [
    "GOOG/GOOGL",  # Multiple share classes
    "FB",          # Now META (ticker changed)
    "Various",     # Not a real ticker
    "See attached",# Requires manual lookup
    "Stock Option", # Need to find underlying
]
```

### API Rate Limits

**Yahoo Finance**: ~2000 requests/hour
**Alpha Vantage**: 5 calls/minute (free tier)
**Quiver Quant**: Depends on plan

**Mitigation**:
- Implement caching
- Batch requests
- Use exponential backoff on failures
- Store downloaded data locally

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=5):
    """Decorator to enforce rate limiting"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

### Computational Performance

**For Large Datasets (10,000+ trades)**:
- Use vectorized pandas operations
- Consider Dask for parallel processing
- Store processed data in efficient formats (Parquet)
- Index database tables properly

```python
# Efficient: vectorized operation
df['return'] = (df['exit_price'] - df['entry_price']) / df['entry_price']

# Inefficient: row-by-row iteration
for idx, row in df.iterrows():
    df.loc[idx, 'return'] = (row['exit_price'] - row['entry_price']) / row['entry_price']
```

## Frequently Asked Questions

### Q: Is this legal?

**A**: Yes. All congressional trading data is public information, disclosed per the STOCK Act (2012). Using publicly available information for investment decisions is legal. This is not insider trading.

### Q: Has this been studied before?

**A**: Yes. Academic research has shown:
- Politicians' trades historically outperform market averages
- Effect is strongest for purchases (not sales)
- Outperformance diminishes when accounting for disclosure delay
- Members of financial committees show stronger performance

**Notable Studies**:
- Ziobrowski et al. (2004): Senators earned abnormal returns of 12% annually
- Eggers & Hainmueller (2013): Found smaller but still positive effects
- Multiple recent studies (2020+) show continued outperformance

### Q: Why would this work?

**Possible Explanations**:
1. **Information advantage**: Access to non-public policy information
2. **Network effects**: Connections to industry insiders
3. **Expertise**: Committee assignments provide deep sector knowledge
4. **Better advice**: Access to high-quality research and advisors
5. **Selection bias**: Wealthier, more educated individuals

### Q: What's the expected return?

**Realistic Expectations** (after disclosure delay):
- Optimistic: 3-8% annual alpha over S&P 500
- Realistic: 1-4% annual alpha
- Conservative: 0-2% annual alpha

**Note**: Past performance ≠ future results

### Q: Which politicians should I focus on?

**Criteria to Consider**:
- Committee memberships (Finance, Banking, Commerce)
- Trading frequency (more data = better signal)
- Historical performance (but beware survivorship bias)
- Disclosure promptness (shorter delays = more actionable)

### Q: Should I copy every trade?

**Probably not**:
- Diversification is important
- Some trades may be estate planning, not market timing
- Consider position sizing relative to your portfolio
- Apply your own risk management rules

### Q: What about options trades?

**More Complex**:
- Options disclosures often lack strike/expiration details
- Harder to replicate
- Higher risk
- Consider focusing on stock trades only

### Q: How often should I check for new disclosures?

**Recommendation**:
- Daily for active strategy
- Weekly for most investors
- Use alerts/notifications when possible

### Q: What about sales vs purchases?

**Research Findings**:
- Purchases show stronger signal (what to buy)
- Sales may be for portfolio rebalancing/tax reasons
- Consider focusing primarily on purchases

### Q: Can this be automated?

**Yes, but**:
- Requires robust error handling
- Need data quality checks
- Should include human review for large trades
- Consider starting semi-automated

## Next Steps After Analysis

### If Results Show Profitability:

1. **Validate findings**:
   - Out-of-sample testing
   - Sensitivity analysis
   - Peer review

2. **Develop trading rules**:
   - Entry criteria
   - Position sizing
   - Exit strategy
   - Risk management

3. **Build dashboard** (Phase 2):
   - Real-time monitoring
   - Automated alerts
   - Portfolio tracking

4. **Paper trade first**:
   - Test in simulation
   - Track performance
   - Refine strategy

5. **Start small**:
   - Allocate limited capital initially
   - Scale up if successful
   - Maintain discipline

### If Results Are Inconclusive:

- Expand time period
- Gather more data sources
- Refine analysis methods
- Consider alternative strategies
- Accept that delay may eliminate edge

### If Results Show No Profitability:

- Document findings
- Publish analysis (valuable negative result)
- Pivot to different strategy
- Consider other alternative data sources

## Resources & References

### Academic Papers
- Ziobrowski et al. (2004): "Abnormal Returns from the Common Stock Investments of the U.S. Senate"
- Eggers & Hainmueller (2013): "Political Capital"

### Data Sources
- Senate: https://efdsearch.senate.gov/
- House: https://disclosures-clerk.house.gov/
- Capitol Trades: https://www.capitoltrades.com/
- Quiver Quantitative: https://www.quiverquant.com/

### Tools & Libraries
- yfinance documentation: https://pypi.org/project/yfinance/
- pandas documentation: https://pandas.pydata.org/
- statsmodels: https://www.statsmodels.org/

### Communities
- r/wallstreetbets (controversial but active)
- r/investing
- r/algotrading
- QuantConnect forums
- Kaggle datasets & notebooks
