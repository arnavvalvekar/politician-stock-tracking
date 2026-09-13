"""Database schema definitions"""

from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Boolean, 
    ForeignKey, Enum as SQLEnum, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TransactionTypeEnum(enum.Enum):
    """Transaction type enumeration"""
    PURCHASE = "Purchase"
    SALE = "Sale"
    EXCHANGE = "Exchange"
    PURCHASE_PARTIAL = "Purchase (Partial)"
    SALE_PARTIAL = "Sale (Partial)"


class ChamberEnum(enum.Enum):
    """Congressional chamber enumeration"""
    SENATE = "Senate"
    HOUSE = "House"


class PartyEnum(enum.Enum):
    """Political party enumeration"""
    DEMOCRAT = "D"
    REPUBLICAN = "R"
    INDEPENDENT = "I"


class Trade(Base):
    """Congressional trades table"""
    __tablename__ = 'trades'
    
    transaction_id = Column(String(100), primary_key=True)
    politician_name = Column(String(200), nullable=False, index=True)
    politician_party = Column(SQLEnum(PartyEnum), nullable=False)
    chamber = Column(SQLEnum(ChamberEnum), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    disclosure_date = Column(Date, nullable=False, index=True)
    filing_delay_days = Column(Integer)
    ticker = Column(String(10), nullable=False, index=True)
    asset_description = Column(String(500))
    transaction_type = Column(SQLEnum(TransactionTypeEnum), nullable=False)
    amount_range = Column(String(100))
    amount_min = Column(Float)
    amount_max = Column(Float)
    amount_estimated = Column(Float)
    owner = Column(String(50), default="Self")
    comment = Column(Text)
    capital_gains_over_200 = Column(Boolean, default=False)
    filing_id = Column(String(100))
    data_source = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Trade {self.politician_name} - {self.ticker} on {self.transaction_date}>"


class StockPriceModel(Base):
    """Stock prices table"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float)
    volume = Column(Integer)
    dividend = Column(Float)
    split_ratio = Column(Float)
    data_source = Column(String(100), default="Yahoo Finance")
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<StockPrice {self.ticker} on {self.date}: ${self.close}>"


class PoliticianModel(Base):
    """Politicians table"""
    __tablename__ = 'politicians'
    
    politician_id = Column(String(100), primary_key=True)
    full_name = Column(String(200), nullable=False, unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    party = Column(SQLEnum(PartyEnum), nullable=False)
    chamber = Column(SQLEnum(ChamberEnum), nullable=False)
    state = Column(String(2))
    district = Column(String(10))
    committees = Column(Text)  # JSON string
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    website = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Politician {self.full_name} ({self.party.value}-{self.chamber.value})>"


class PerformanceMetrics(Base):
    """Performance metrics table"""
    __tablename__ = 'performance_metrics'
    
    metric_id = Column(String(200), primary_key=True)
    politician_id = Column(String(100))
    politician_name = Column(String(200), nullable=False, index=True)
    analysis_period_start = Column(Date, nullable=False)
    analysis_period_end = Column(Date, nullable=False)
    total_transactions = Column(Integer)
    total_purchases = Column(Integer)
    total_sales = Column(Integer)
    total_volume = Column(Float)
    unique_tickers = Column(Integer)
    avg_position_size = Column(Float)
    total_return_pct = Column(Float)
    annualized_return_pct = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown_pct = Column(Float)
    volatility_pct = Column(Float)
    win_rate_pct = Column(Float)
    avg_gain_pct = Column(Float)
    avg_loss_pct = Column(Float)
    profit_factor = Column(Float)
    avg_holding_period_days = Column(Integer)
    median_holding_period_days = Column(Integer)
    benchmark_return_pct = Column(Float)
    alpha_pct = Column(Float)
    beta = Column(Float)
    information_ratio = Column(Float)
    tracking_error_pct = Column(Float)
    calculated_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<PerformanceMetrics {self.politician_name} {self.analysis_period_start} to {self.analysis_period_end}>"


class TradeReturn(Base):
    """Individual trade returns table"""
    __tablename__ = 'trade_returns'
    
    return_id = Column(String(200), primary_key=True)
    transaction_id = Column(String(100), ForeignKey('trades.transaction_id'))
    politician_name = Column(String(200), index=True)
    ticker = Column(String(10), index=True)
    entry_date = Column(Date)
    entry_price = Column(Float)
    holding_period_days = Column(Integer)
    exit_date = Column(Date)
    exit_price = Column(Float)
    return_pct = Column(Float)
    return_absolute = Column(Float)
    benchmark_return_pct = Column(Float)
    excess_return_pct = Column(Float)
    calculated_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    trade = relationship("Trade")
    
    def __repr__(self):
        return f"<TradeReturn {self.ticker} {self.holding_period_days}d: {self.return_pct:.2f}%>"


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully")


def drop_tables(engine):
    """Drop all tables from the database"""
    Base.metadata.drop_all(engine)
    print("Database tables dropped successfully")
