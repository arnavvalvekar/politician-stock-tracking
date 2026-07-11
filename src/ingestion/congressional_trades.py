"""Congressional trades data ingestion"""

import pandas as pd
from datetime import datetime
from typing import List, Optional
import hashlib

from ..models.trade import CongressionalTrade, TransactionType, Chamber, Party, parse_amount_range


class CongressionalTradesIngestion:
    """Ingest congressional trading data from various sources"""
    
    def __init__(self):
        self.trades: List[CongressionalTrade] = []
    
    def load_from_csv(self, csv_path: str) -> List[CongressionalTrade]:
        """
        Load trades from CSV file
        
        Expected CSV columns:
        - politician_name
        - party (D/R/I)
        - chamber (Senate/House)
        - transaction_date (YYYY-MM-DD)
        - disclosure_date (YYYY-MM-DD)
        - ticker
        - asset_description
        - transaction_type (Purchase/Sale/Exchange)
        - amount_range (e.g., "$15,001 - $50,000")
        - owner (optional)
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of CongressionalTrade objects
        """
        df = pd.read_csv(csv_path)
        trades = []
        
        for idx, row in df.iterrows():
            try:
                # Parse amount range
                amount_min, amount_max = parse_amount_range(row['amount_range'])
                
                # Generate transaction ID
                transaction_id = self._generate_transaction_id(
                    row['politician_name'],
                    row['transaction_date'],
                    row['ticker']
                )
                
                # Create trade object
                trade = CongressionalTrade(
                    transaction_id=transaction_id,
                    politician_name=row['politician_name'],
                    politician_party=Party(row['party']),
                    chamber=Chamber(row['chamber']),
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    disclosure_date=pd.to_datetime(row['disclosure_date']).date(),
                    ticker=row['ticker'].upper().strip(),
                    asset_description=row.get('asset_description', ''),
                    transaction_type=TransactionType(row['transaction_type']),
                    amount_range=row['amount_range'],
                    amount_min=amount_min,
                    amount_max=amount_max,
                    owner=row.get('owner', 'Self'),
                    comment=row.get('comment'),
                    data_source=f"CSV: {csv_path}"
                )
                
                trades.append(trade)
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                print(f"Row data: {row.to_dict()}")
                continue
        
        self.trades.extend(trades)
        print(f"Loaded {len(trades)} trades from {csv_path}")
        
        return trades
    
    def load_from_dataframe(self, df: pd.DataFrame) -> List[CongressionalTrade]:
        """
        Load trades from pandas DataFrame
        
        Args:
            df: DataFrame with trade data (same columns as CSV)
            
        Returns:
            List of CongressionalTrade objects
        """
        trades = []
        
        for idx, row in df.iterrows():
            try:
                amount_min, amount_max = parse_amount_range(row['amount_range'])
                
                transaction_id = self._generate_transaction_id(
                    row['politician_name'],
                    str(row['transaction_date']),
                    row['ticker']
                )
                
                trade = CongressionalTrade(
                    transaction_id=transaction_id,
                    politician_name=row['politician_name'],
                    politician_party=Party(row['party']),
                    chamber=Chamber(row['chamber']),
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    disclosure_date=pd.to_datetime(row['disclosure_date']).date(),
                    ticker=row['ticker'].upper().strip(),
                    asset_description=row.get('asset_description', ''),
                    transaction_type=TransactionType(row['transaction_type']),
                    amount_range=row['amount_range'],
                    amount_min=amount_min,
                    amount_max=amount_max,
                    owner=row.get('owner', 'Self'),
                    comment=row.get('comment'),
                    data_source="DataFrame"
                )
                
                trades.append(trade)
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        self.trades.extend(trades)
        return trades
    
    def create_manual_trade(
        self,
        politician_name: str,
        party: str,
        chamber: str,
        transaction_date: str,
        disclosure_date: str,
        ticker: str,
        transaction_type: str,
        amount_range: str,
        asset_description: str = "",
        owner: str = "Self"
    ) -> CongressionalTrade:
        """
        Manually create a single trade
        
        Args:
            politician_name: Full name of politician
            party: "D", "R", or "I"
            chamber: "Senate" or "House"
            transaction_date: Date in YYYY-MM-DD format
            disclosure_date: Date in YYYY-MM-DD format
            ticker: Stock ticker symbol
            transaction_type: "Purchase", "Sale", or "Exchange"
            amount_range: Amount range string or code
            asset_description: Optional description
            owner: Who owns the asset
            
        Returns:
            CongressionalTrade object
        """
        amount_min, amount_max = parse_amount_range(amount_range)
        
        transaction_id = self._generate_transaction_id(
            politician_name,
            transaction_date,
            ticker
        )
        
        trade = CongressionalTrade(
            transaction_id=transaction_id,
            politician_name=politician_name,
            politician_party=Party(party),
            chamber=Chamber(chamber),
            transaction_date=pd.to_datetime(transaction_date).date(),
            disclosure_date=pd.to_datetime(disclosure_date).date(),
            ticker=ticker.upper().strip(),
            asset_description=asset_description,
            transaction_type=TransactionType(transaction_type),
            amount_range=amount_range,
            amount_min=amount_min,
            amount_max=amount_max,
            owner=owner,
            data_source="Manual"
        )
        
        self.trades.append(trade)
        return trade
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert loaded trades to DataFrame
        
        Returns:
            DataFrame with all trade data
        """
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame([trade.to_dict() for trade in self.trades])
    
    def filter_by_politician(self, politician_name: str) -> List[CongressionalTrade]:
        """Filter trades by politician name"""
        return [t for t in self.trades if t.politician_name == politician_name]
    
    def filter_by_ticker(self, ticker: str) -> List[CongressionalTrade]:
        """Filter trades by ticker"""
        ticker = ticker.upper().strip()
        return [t for t in self.trades if t.ticker == ticker]
    
    def filter_by_date_range(
        self,
        start_date: str,
        end_date: str,
        use_transaction_date: bool = True
    ) -> List[CongressionalTrade]:
        """
        Filter trades by date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_transaction_date: If True, filter by transaction_date; else disclosure_date
            
        Returns:
            Filtered list of trades
        """
        start = pd.to_datetime(start_date).date()
        end = pd.to_datetime(end_date).date()
        
        if use_transaction_date:
            return [t for t in self.trades if start <= t.transaction_date <= end]
        else:
            return [t for t in self.trades if start <= t.disclosure_date <= end]
    
    def get_unique_tickers(self) -> List[str]:
        """Get list of unique tickers"""
        return sorted(list(set(t.ticker for t in self.trades)))
    
    def get_unique_politicians(self) -> List[str]:
        """Get list of unique politician names"""
        return sorted(list(set(t.politician_name for t in self.trades)))
    
    def summary_stats(self) -> dict:
        """Get summary statistics"""
        if not self.trades:
            return {}
        
        df = self.to_dataframe()
        
        return {
            'total_trades': len(self.trades),
            'unique_politicians': len(self.get_unique_politicians()),
            'unique_tickers': len(self.get_unique_tickers()),
            'purchases': len([t for t in self.trades if 'Purchase' in t.transaction_type.value]),
            'sales': len([t for t in self.trades if 'Sale' in t.transaction_type.value]),
            'date_range': (df['transaction_date'].min(), df['transaction_date'].max()),
            'avg_filing_delay_days': df['filing_delay_days'].mean(),
            'total_volume_estimated': df['amount_estimated'].sum(),
        }
    
    def _generate_transaction_id(
        self,
        politician_name: str,
        transaction_date: str,
        ticker: str
    ) -> str:
        """
        Generate unique transaction ID
        
        Format: LASTNAME_YYYYMMDD_TICKER_HASH
        """
        # Get last name
        last_name = politician_name.split()[-1].upper().replace(' ', '')
        
        # Format date
        date_str = pd.to_datetime(transaction_date).strftime('%Y%m%d')
        
        # Create hash for uniqueness (in case of multiple trades same day)
        hash_input = f"{politician_name}_{transaction_date}_{ticker}_{datetime.now().timestamp()}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6]
        
        return f"{last_name}_{date_str}_{ticker.upper()}_{hash_suffix}"


def create_sample_trades() -> List[CongressionalTrade]:
    """
    Create sample trades for testing
    
    Returns:
        List of sample CongressionalTrade objects
    """
    ingestion = CongressionalTradesIngestion()
    
    # Sample trades based on real politician trading patterns
    sample_data = [
        {
            'politician_name': 'Nancy Pelosi',
            'party': 'D',
            'chamber': 'House',
            'transaction_date': '2023-07-01',
            'disclosure_date': '2023-08-15',
            'ticker': 'NVDA',
            'transaction_type': 'Purchase',
            'amount_range': '$1,000,001 - $5,000,000',
            'asset_description': 'NVIDIA Corporation - Common Stock',
        },
        {
            'politician_name': 'Nancy Pelosi',
            'party': 'D',
            'chamber': 'House',
            'transaction_date': '2023-06-15',
            'disclosure_date': '2023-07-28',
            'ticker': 'MSFT',
            'transaction_type': 'Purchase',
            'amount_range': '$500,001 - $1,000,000',
            'asset_description': 'Microsoft Corporation - Common Stock',
        },
        {
            'politician_name': 'Josh Gottheimer',
            'party': 'D',
            'chamber': 'House',
            'transaction_date': '2023-05-10',
            'disclosure_date': '2023-06-20',
            'ticker': 'AAPL',
            'transaction_type': 'Purchase',
            'amount_range': '$100,001 - $250,000',
            'asset_description': 'Apple Inc. - Common Stock',
        },
        {
            'politician_name': 'Tommy Tuberville',
            'party': 'R',
            'chamber': 'Senate',
            'transaction_date': '2023-04-05',
            'disclosure_date': '2023-05-15',
            'ticker': 'GOOGL',
            'transaction_type': 'Purchase',
            'amount_range': '$50,001 - $100,000',
            'asset_description': 'Alphabet Inc. - Class A Common Stock',
        },
        {
            'politician_name': 'Dan Crenshaw',
            'party': 'R',
            'chamber': 'House',
            'transaction_date': '2023-03-20',
            'disclosure_date': '2023-04-25',
            'ticker': 'TSLA',
            'transaction_type': 'Purchase',
            'amount_range': '$15,001 - $50,000',
            'asset_description': 'Tesla Inc. - Common Stock',
        },
    ]
    
    for trade_data in sample_data:
        ingestion.create_manual_trade(**trade_data)
    
    return ingestion.trades
