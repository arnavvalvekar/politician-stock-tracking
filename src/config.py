"""Configuration settings for the congressional trading analysis system"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure directories exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_DIR, OUTPUTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_DIR}/trades.db")

# API Keys
QUIVER_API_TOKEN = os.getenv("QUIVER_API_TOKEN", "")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")

# Analysis settings
START_DATE = os.getenv("START_DATE", "2020-01-01")
END_DATE = os.getenv("END_DATE", "2024-12-31")
BENCHMARK_TICKER = os.getenv("BENCHMARK_TICKER", "SPY")
RISK_FREE_RATE = float(os.getenv("RISK_FREE_RATE", "0.04"))

# Data source settings
USE_YAHOO_FINANCE = os.getenv("USE_YAHOO_FINANCE", "true").lower() == "true"

# Analysis parameters
FORWARD_RETURN_PERIODS = [7, 30, 90, 180, 365]  # Days
DELAY_SIMULATION_DAYS = 3  # Additional days after disclosure for realistic entry

# Cache settings
ENABLE_CACHE = True
CACHE_EXPIRY_DAYS = 7
