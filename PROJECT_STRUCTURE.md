# Project Structure

## Recommended Directory Layout

```
politician-stock-tracking/
├── README.md                          # Project overview and quick start
├── DESIGN.md                          # Comprehensive design document
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment variables
├── .gitignore                         # Git ignore rules
│
├── config/                            # Configuration files
│   ├── __init__.py
│   ├── settings.py                    # Application settings
│   └── data_sources.yaml              # Data source configurations
│
├── data/                              # Data storage (git-ignored)
│   ├── raw/                           # Raw downloaded data
│   │   ├── congressional_trades/     # Raw trade disclosures
│   │   └── market_data/               # Raw stock prices
│   ├── processed/                     # Cleaned and processed data
│   │   ├── trades.parquet
│   │   ├── prices.parquet
│   │   └── portfolios.parquet
│   └── database/                      # SQLite database files
│       └── trades.db
│
├── src/                               # Source code
│   ├── __init__.py
│   │
│   ├── ingestion/                     # Data ingestion modules
│   │   ├── __init__.py
│   │   ├── base.py                    # Base ingestion class
│   │   ├── congressional_trades.py   # Fetch congressional data
│   │   ├── market_data.py            # Fetch stock prices
│   │   └── parsers/                   # Data parsers
│   │       ├── __init__.py
│   │       ├── senate_pdf.py
│   │       ├── house_pdf.py
│   │       └── api_parsers.py
│   │
│   ├── models/                        # Data models and schema
│   │   ├── __init__.py
│   │   ├── trade.py                   # Trade data model
│   │   ├── stock_price.py            # Stock price model
│   │   ├── politician.py             # Politician model
│   │   └── portfolio.py              # Portfolio model
│   │
│   ├── database/                      # Database operations
│   │   ├── __init__.py
│   │   ├── connection.py             # DB connection management
│   │   ├── schema.py                 # Database schema
│   │   └── queries.py                # Common queries
│   │
│   ├── processing/                    # Data processing
│   │   ├── __init__.py
│   │   ├── cleaner.py                # Data cleaning
│   │   ├── enricher.py               # Add market data to trades
│   │   ├── portfolio_builder.py     # Build politician portfolios
│   │   └── aggregator.py            # Aggregate metrics
│   │
│   ├── analysis/                      # Analysis modules
│   │   ├── __init__.py
│   │   ├── performance.py            # Performance calculations
│   │   ├── risk_metrics.py          # Risk-adjusted metrics
│   │   ├── benchmarks.py            # Benchmark comparisons
│   │   ├── statistical_tests.py     # Significance testing
│   │   └── segmentation.py          # Segmented analysis
│   │
│   ├── visualization/                 # Visualization utilities
│   │   ├── __init__.py
│   │   ├── charts.py                 # Chart generation
│   │   ├── reports.py               # Report generation
│   │   └── templates/               # Report templates
│   │       └── report_template.html
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── date_utils.py             # Date handling
│       ├── validators.py             # Data validation
│       └── logging_config.py        # Logging setup
│
├── scripts/                           # Executable scripts
│   ├── fetch_trades.py               # Download congressional trades
│   ├── fetch_market_data.py         # Download stock prices
│   ├── process_data.py              # Run data processing
│   ├── run_analysis.py              # Run analysis
│   └── generate_report.py           # Generate reports
│
├── notebooks/                         # Jupyter notebooks
│   ├── 01_data_exploration.ipynb    # Explore raw data
│   ├── 02_data_quality.ipynb        # Data quality checks
│   ├── 03_performance_analysis.ipynb # Performance analysis
│   ├── 04_timing_analysis.ipynb     # Timing and delay analysis
│   └── 05_strategy_development.ipynb # Strategy development
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── test_ingestion/              # Ingestion tests
│   ├── test_processing/             # Processing tests
│   ├── test_analysis/               # Analysis tests
│   └── test_utils/                  # Utility tests
│
├── docs/                              # Additional documentation
│   ├── api_documentation.md
│   ├── data_dictionary.md
│   └── analysis_methodology.md
│
└── outputs/                           # Generated outputs
    ├── reports/                       # Analysis reports
    │   ├── html/
    │   └── pdf/
    ├── figures/                       # Generated plots
    └── results/                       # Analysis results
        └── performance_metrics.csv
```

## Key Files Explanation

### Configuration
- **`config/settings.py`**: Central configuration (database paths, API keys, analysis parameters)
- **`config/data_sources.yaml`**: Data source URLs and credentials
- **`.env`**: Environment variables for API keys (not committed to git)

### Source Code Organization
- **`src/ingestion/`**: Responsible for fetching data from various sources
- **`src/models/`**: Define data structures and validation
- **`src/database/`**: Handle all database operations
- **`src/processing/`**: Transform raw data into analysis-ready format
- **`src/analysis/`**: Core analysis logic
- **`src/visualization/`**: Generate charts and reports

### Scripts
Executable scripts that tie everything together:
- Fetch new data
- Process and clean data
- Run analyses
- Generate reports

### Notebooks
Interactive exploration and analysis:
- Data exploration and validation
- Prototyping analysis methods
- Generating insights
- Creating visualizations

### Tests
Comprehensive test coverage:
- Unit tests for each module
- Integration tests for pipelines
- Data validation tests

## Development Workflow

### Initial Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_database.py
```

### Typical Analysis Workflow
```bash
# 1. Fetch latest congressional trade data
python scripts/fetch_trades.py --start-date 2020-01-01

# 2. Fetch corresponding market data
python scripts/fetch_market_data.py

# 3. Process and enrich data
python scripts/process_data.py

# 4. Run analysis
python scripts/run_analysis.py --period 2020-2023

# 5. Generate report
python scripts/generate_report.py --output outputs/reports/html/
```

### Interactive Analysis
```bash
# Start Jupyter
jupyter notebook notebooks/
```

## Data Flow

1. **Ingestion** → Raw data saved to `data/raw/`
2. **Processing** → Cleaned data saved to `data/processed/` and `data/database/`
3. **Analysis** → Results saved to `outputs/results/`
4. **Visualization** → Charts and reports saved to `outputs/figures/` and `outputs/reports/`

## Git Ignore Recommendations

The following should be excluded from git:
- `data/` (all data files)
- `outputs/` (generated outputs)
- `.env` (environment variables)
- `*.db` (database files)
- `__pycache__/` (Python cache)
- `.pytest_cache/` (pytest cache)
- `.ipynb_checkpoints/` (Jupyter checkpoints)
- `venv/` or `.venv/` (virtual environment)

## Scalability Considerations

### For Small Scale (Prototype)
- Use SQLite for database
- Store data as CSV/Parquet files
- Run analysis locally

### For Medium Scale
- Migrate to PostgreSQL
- Use Parquet for efficient columnar storage
- Implement incremental data updates
- Cache processed results

### For Large Scale (Future)
- Consider cloud database (AWS RDS, Google Cloud SQL)
- Use data warehouse (Snowflake, BigQuery)
- Implement parallel processing (Dask, Apache Spark)
- Deploy as web service with API
