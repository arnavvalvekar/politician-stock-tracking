# Congressional Stock Trading Analysis

Analyze historical congressional stock trading data to determine if following politician trades is a profitable investment strategy.

## 🎯 Project Goals

1. **Historical Analysis**: Evaluate whether congressional stock trades historically outperform the market
2. **Performance Metrics**: Calculate risk-adjusted returns, win rates, and benchmark comparisons
3. **Strategy Development**: Identify which politicians, sectors, and trade types are most profitable
4. **Future Dashboard**: Build an interactive dashboard to track ongoing performance (Phase 2)

## 📊 Key Questions to Answer

- Do politicians as a group beat the S&P 500?
- Which individual politicians show the best performance?
- How much return is lost due to the 30-45 day disclosure delay?
- Are certain sectors or committee assignments more profitable?
- What is the optimal strategy for following these trades?

## 🏗️ Current Status

**Phase 1: Design & Planning** ✅

We are currently in the design phase, establishing:
- System architecture
- Data sources and schemas
- Analysis methodology
- Technology stack
- Implementation roadmap

## 📚 Documentation

- **[DESIGN.md](./DESIGN.md)** - Comprehensive system design document
  - Data sources
  - Architecture diagram
  - Analysis methodology
  - Performance metrics
  - Implementation phases

- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Recommended project layout
  - Directory structure
  - File organization
  - Development workflow
  - Scalability considerations

- **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Technical implementation details
  - Data source options and code examples
  - Core data models
  - Analysis functions
  - Quick start script

## 🚀 Quick Start (Coming Soon)

Once implementation begins:

```bash
# 1. Clone and setup
git clone <repo-url>
cd politician-stock-tracking
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Fetch data
python scripts/fetch_trades.py --start-date 2020-01-01
python scripts/fetch_market_data.py

# 4. Run analysis
python scripts/run_analysis.py

# 5. View results
jupyter notebook notebooks/03_performance_analysis.ipynb
```

## 🛠️ Technology Stack

### Data & Analysis
- **Python 3.11+**: Core language
- **Pandas & NumPy**: Data manipulation
- **SQLite/PostgreSQL**: Data storage
- **yfinance**: Market data
- **SciPy & Statsmodels**: Statistical analysis

### Visualization
- **Matplotlib & Seaborn**: Static plots
- **Plotly**: Interactive charts
- **Jupyter**: Exploratory analysis

### Future Dashboard (Phase 2)
- **FastAPI/Flask**: Backend API
- **React**: Frontend UI
- **PostgreSQL**: Production database

## 📈 Analysis Approach

### Data Collection
1. Congressional trade disclosures (STOCK Act filings)
2. Historical stock prices for traded securities
3. Benchmark data (S&P 500, sector ETFs)

### Performance Calculation
1. **Forward Returns**: Measure returns at 1 week, 1 month, 3 months, 6 months, 1 year
2. **Portfolio Simulation**: Build hypothetical portfolios mimicking each politician
3. **Risk-Adjusted Metrics**: Calculate Sharpe ratio, Sortino ratio, maximum drawdown
4. **Benchmark Comparison**: Compare to S&P 500 and relevant sector indices
5. **Statistical Testing**: Determine if outperformance is significant

### Key Considerations
- **Disclosure Delay**: Trades disclosed 30-45 days after execution
- **Transaction Ranges**: Exact amounts not disclosed (e.g., "$15,001 - $50,000")
- **Survivorship Bias**: Include politicians who left office
- **Transaction Costs**: Model realistic execution costs

## 📊 Expected Outputs

### Phase 1 Deliverables
1. ✅ **Design Documentation** (Current)
2. 🔄 **Data Ingestion Pipeline** (Next)
3. 🔄 **Historical Performance Report**
   - Overall market-beating analysis
   - Top performing politicians ranking
   - Timing impact study
   - Sector performance breakdown
4. 🔄 **Strategy Recommendations**
   - Which politicians to follow
   - Trade size considerations
   - Risk management guidelines

### Phase 2 Deliverables (Future)
- Interactive web dashboard
- Real-time trade monitoring
- Automated alerts for new disclosures
- Portfolio backtesting interface

## 📖 Data Sources

### Congressional Trading Data
- **Quiver Quantitative API** (recommended, paid)
- **Capitol Trades** (free, requires scraping)
- **Senate/House Official Sites** (free, complex parsing)
- **Pre-aggregated datasets** (Kaggle, GitHub)

### Market Data
- **Yahoo Finance** (free, via yfinance)
- **Alpha Vantage** (free tier available)
- **Polygon.io** (paid, comprehensive)

See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for detailed instructions on each source.

## 🤝 Contributing

This is currently a personal analysis project. Contributions welcome after Phase 1 completion.

## ⚖️ Legal & Ethical Considerations

- All data used is publicly disclosed per the STOCK Act (2012)
- This project is for educational and research purposes
- Following congressional trades does not guarantee profits
- Consider consulting a financial advisor before making investment decisions
- Respect rate limits and terms of service for all data sources

## 📝 License

TBD

## 🗺️ Roadmap

- [x] **Phase 1.1**: System design and architecture ✅
- [ ] **Phase 1.2**: Data ingestion implementation
- [ ] **Phase 1.3**: Analysis pipeline development
- [ ] **Phase 1.4**: Historical performance report
- [ ] **Phase 2**: Dashboard development
- [ ] **Phase 3**: Real-time monitoring and alerts

## 📧 Contact

For questions or suggestions, please open an issue in this repository.

---

**Disclaimer**: This project analyzes publicly available data for educational purposes. Past performance does not guarantee future results. Always conduct your own research and consult with financial professionals before making investment decisions.
