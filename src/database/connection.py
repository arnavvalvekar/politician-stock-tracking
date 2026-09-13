"""Database connection and operations"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import List, Optional
import pandas as pd

from .schema import Base, Trade, StockPriceModel, PoliticianModel, create_tables
from ..models.trade import CongressionalTrade, StockPrice
from ..config import DATABASE_URL


class Database:
    """Database connection and operations manager"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            database_url: Database URL (defaults to config value)
        """
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def initialize(self):
        """Initialize database tables"""
        create_tables(self.engine)
        
    @contextmanager
    def get_session(self):
        """
        Get database session with context manager
        
        Usage:
            with db.get_session() as session:
                session.query(Trade).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def insert_trade(self, trade: CongressionalTrade) -> bool:
        """
        Insert a single trade into database
        
        Args:
            trade: CongressionalTrade object
            
        Returns:
            True if successful, False otherwise
        """
        with self.get_session() as session:
            try:
                db_trade = Trade(
                    transaction_id=trade.transaction_id,
                    politician_name=trade.politician_name,
                    politician_party=trade.politician_party.value,
                    chamber=trade.chamber.value,
                    transaction_date=trade.transaction_date,
                    disclosure_date=trade.disclosure_date,
                    filing_delay_days=trade.filing_delay_days,
                    ticker=trade.ticker,
                    asset_description=trade.asset_description,
                    transaction_type=trade.transaction_type.value,
                    amount_range=trade.amount_range,
                    amount_min=trade.amount_min,
                    amount_max=trade.amount_max,
                    amount_estimated=trade.amount_estimated,
                    owner=trade.owner,
                    comment=trade.comment,
                    capital_gains_over_200=trade.capital_gains_over_200,
                    filing_id=trade.filing_id,
                    data_source=trade.data_source,
                    created_at=trade.created_at,
                    updated_at=trade.updated_at,
                )
                
                session.add(db_trade)
                session.commit()
                return True
                
            except Exception as e:
                print(f"Error inserting trade: {e}")
                return False
    
    def insert_trades_bulk(self, trades: List[CongressionalTrade]) -> int:
        """
        Insert multiple trades in bulk
        
        Args:
            trades: List of CongressionalTrade objects
            
        Returns:
            Number of trades successfully inserted
        """
        count = 0
        with self.get_session() as session:
            for trade in trades:
                try:
                    db_trade = Trade(
                        transaction_id=trade.transaction_id,
                        politician_name=trade.politician_name,
                        politician_party=trade.politician_party.value,
                        chamber=trade.chamber.value,
                        transaction_date=trade.transaction_date,
                        disclosure_date=trade.disclosure_date,
                        filing_delay_days=trade.filing_delay_days,
                        ticker=trade.ticker,
                        asset_description=trade.asset_description,
                        transaction_type=trade.transaction_type.value,
                        amount_range=trade.amount_range,
                        amount_min=trade.amount_min,
                        amount_max=trade.amount_max,
                        amount_estimated=trade.amount_estimated,
                        owner=trade.owner,
                        comment=trade.comment,
                        capital_gains_over_200=trade.capital_gains_over_200,
                        filing_id=trade.filing_id,
                        data_source=trade.data_source,
                        created_at=trade.created_at,
                        updated_at=trade.updated_at,
                    )
                    session.add(db_trade)
                    count += 1
                except Exception as e:
                    print(f"Error inserting trade {trade.transaction_id}: {e}")
            
            session.commit()
        
        print(f"Inserted {count} trades into database")
        return count
    
    def insert_stock_prices(self, prices_df: pd.DataFrame) -> int:
        """
        Insert stock prices from DataFrame
        
        Args:
            prices_df: DataFrame with columns: ticker, date, open, high, low, close, volume
            
        Returns:
            Number of records inserted
        """
        count = 0
        with self.get_session() as session:
            for _, row in prices_df.iterrows():
                try:
                    price = StockPriceModel(
                        ticker=row['ticker'],
                        date=row['date'],
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row['close'],
                        adjusted_close=row.get('adjusted_close', row['close']),
                        volume=row.get('volume'),
                        data_source=row.get('data_source', 'Yahoo Finance'),
                    )
                    session.add(price)
                    count += 1
                except Exception as e:
                    print(f"Error inserting price for {row.get('ticker')}: {e}")
            
            session.commit()
        
        print(f"Inserted {count} price records into database")
        return count
    
    def get_all_trades(self) -> pd.DataFrame:
        """Get all trades as DataFrame"""
        with self.get_session() as session:
            trades = session.query(Trade).all()
            
            if not trades:
                return pd.DataFrame()
            
            data = []
            for trade in trades:
                data.append({
                    'transaction_id': trade.transaction_id,
                    'politician_name': trade.politician_name,
                    'party': trade.politician_party.value,
                    'chamber': trade.chamber.value,
                    'transaction_date': trade.transaction_date,
                    'disclosure_date': trade.disclosure_date,
                    'filing_delay_days': trade.filing_delay_days,
                    'ticker': trade.ticker,
                    'transaction_type': trade.transaction_type.value,
                    'amount_estimated': trade.amount_estimated,
                })
            
            return pd.DataFrame(data)
    
    def get_trades_by_politician(self, politician_name: str) -> pd.DataFrame:
        """Get trades for a specific politician"""
        with self.get_session() as session:
            trades = session.query(Trade).filter(
                Trade.politician_name == politician_name
            ).all()
            
            if not trades:
                return pd.DataFrame()
            
            return pd.DataFrame([{
                'transaction_id': t.transaction_id,
                'transaction_date': t.transaction_date,
                'disclosure_date': t.disclosure_date,
                'ticker': t.ticker,
                'transaction_type': t.transaction_type.value,
                'amount_estimated': t.amount_estimated,
            } for t in trades])
    
    def get_unique_tickers(self) -> List[str]:
        """Get list of unique tickers from trades"""
        with self.get_session() as session:
            tickers = session.query(Trade.ticker).distinct().all()
            return [t[0] for t in tickers]
    
    def get_stock_prices(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get stock prices for a ticker in date range"""
        with self.get_session() as session:
            prices = session.query(StockPriceModel).filter(
                StockPriceModel.ticker == ticker,
                StockPriceModel.date >= start_date,
                StockPriceModel.date <= end_date
            ).all()
            
            if not prices:
                return pd.DataFrame()
            
            return pd.DataFrame([{
                'ticker': p.ticker,
                'date': p.date,
                'close': p.close,
            } for p in prices])
    
    def clear_all_data(self):
        """Clear all data from all tables (use with caution!)"""
        with self.get_session() as session:
            session.query(Trade).delete()
            session.query(StockPriceModel).delete()
            session.query(PoliticianModel).delete()
            session.commit()
        print("All data cleared from database")
