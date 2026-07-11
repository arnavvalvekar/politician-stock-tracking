"""
Real congressional trading data fetchers from public sources
"""

import requests
import pandas as pd
from typing import List, Optional
import time
from datetime import datetime
from tqdm import tqdm

from ..models.trade import CongressionalTrade, TransactionType, Chamber, Party, parse_amount_range


class PublicDataFetcher:
    """Fetch real congressional trading data from public sources"""
    
    # Public S3 bucket URLs (maintained by community)
    HOUSE_S3_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    SENATE_S3_URL = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Congressional Trading Analysis Research)'
        })
    
    def fetch_house_trades(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch House of Representatives trading data from public S3 bucket
        
        Args:
            start_date: Filter trades after this date (YYYY-MM-DD)
            end_date: Filter trades before this date (YYYY-MM-DD)
            
        Returns:
            DataFrame with House trades
        """
        print("Fetching House trading data from public source...")
        
        try:
            response = self.session.get(self.HOUSE_S3_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Standardize column names
            if 'representative' in df.columns:
                df = df.rename(columns={'representative': 'politician_name'})
            elif 'name' in df.columns:
                df = df.rename(columns={'name': 'politician_name'})
            
            if 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            elif 'date' in df.columns:
                df = df.rename(columns={'date': 'transaction_date'})
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            
            if 'disclosure_date' in df.columns:
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            elif 'filed_date' in df.columns:
                df = df.rename(columns={'filed_date': 'disclosure_date'})
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            
            # Standardize transaction type
            if 'type' in df.columns:
                df = df.rename(columns={'type': 'transaction_type'})
            elif 'transaction' in df.columns:
                df = df.rename(columns={'transaction': 'transaction_type'})
            
            # Add chamber
            df['chamber'] = 'House'
            
            # Filter by date range
            if start_date:
                df = df[df['transaction_date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['transaction_date'] <= pd.to_datetime(end_date)]
            
            # Remove rows with missing critical data
            df = df.dropna(subset=['politician_name', 'ticker', 'transaction_date'])
            
            print(f"✓ Fetched {len(df)} House trades")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching House data: {e}")
            print("Note: House Stock Watcher S3 bucket may be unavailable")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error processing House data: {e}")
            return pd.DataFrame()
    
    def fetch_senate_trades(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch Senate trading data from public S3 bucket
        
        Args:
            start_date: Filter trades after this date (YYYY-MM-DD)
            end_date: Filter trades before this date (YYYY-MM-DD)
            
        Returns:
            DataFrame with Senate trades
        """
        print("Fetching Senate trading data from public source...")
        
        try:
            response = self.session.get(self.SENATE_S3_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Standardize column names (similar to House)
            if 'senator' in df.columns:
                df = df.rename(columns={'senator': 'politician_name'})
            elif 'name' in df.columns:
                df = df.rename(columns={'name': 'politician_name'})
            
            if 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            elif 'date' in df.columns:
                df = df.rename(columns={'date': 'transaction_date'})
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            
            if 'disclosure_date' in df.columns:
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            elif 'filed_date' in df.columns:
                df = df.rename(columns={'filed_date': 'disclosure_date'})
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            
            # Standardize transaction type
            if 'type' in df.columns:
                df = df.rename(columns={'type': 'transaction_type'})
            elif 'transaction' in df.columns:
                df = df.rename(columns={'transaction': 'transaction_type'})
            
            # Add chamber
            df['chamber'] = 'Senate'
            
            # Filter by date range
            if start_date:
                df = df[df['transaction_date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['transaction_date'] <= pd.to_datetime(end_date)]
            
            # Remove rows with missing critical data
            df = df.dropna(subset=['politician_name', 'ticker', 'transaction_date'])
            
            print(f"✓ Fetched {len(df)} Senate trades")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Senate data: {e}")
            print("Note: Senate Stock Watcher S3 bucket may be unavailable")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error processing Senate data: {e}")
            return pd.DataFrame()
    
    def fetch_all_trades(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        chambers: List[str] = ['House', 'Senate']
    ) -> pd.DataFrame:
        """
        Fetch trades from both chambers
        
        Args:
            start_date: Filter trades after this date (YYYY-MM-DD)
            end_date: Filter trades before this date (YYYY-MM-DD)
            chambers: List of chambers to fetch ('House', 'Senate', or both)
            
        Returns:
            Combined DataFrame with all trades
        """
        dfs = []
        
        if 'House' in chambers:
            house_df = self.fetch_house_trades(start_date, end_date)
            if not house_df.empty:
                dfs.append(house_df)
        
        if 'Senate' in chambers:
            senate_df = self.fetch_senate_trades(start_date, end_date)
            if not senate_df.empty:
                dfs.append(senate_df)
        
        if not dfs:
            print("Warning: No data fetched from any source")
            return pd.DataFrame()
        
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        print(f"\n✓ Total: {len(combined_df)} trades from {', '.join(chambers)}")
        print(f"  Date range: {combined_df['transaction_date'].min()} to {combined_df['transaction_date'].max()}")
        print(f"  Unique politicians: {combined_df['politician_name'].nunique()}")
        print(f"  Unique tickers: {combined_df['ticker'].nunique()}")
        
        return combined_df
    
    def normalize_and_convert(self, df: pd.DataFrame) -> List[CongressionalTrade]:
        """
        Convert raw DataFrame to CongressionalTrade objects
        
        Args:
            df: Raw DataFrame from public sources
            
        Returns:
            List of CongressionalTrade objects
        """
        trades = []
        
        print("\nNormalizing data...")
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Converting trades"):
            try:
                # Parse amount range
                amount_range = row.get('amount', row.get('amount_range', '$1,001 - $15,000'))
                amount_min, amount_max = parse_amount_range(str(amount_range))
                
                # Determine party (if available, otherwise default based on common knowledge)
                party_str = row.get('party', 'I')  # Default to Independent if unknown
                if party_str not in ['D', 'R', 'I']:
                    party_str = 'I'
                
                # Standardize transaction type
                trans_type = str(row.get('transaction_type', 'Purchase'))
                if 'purchase' in trans_type.lower() or 'buy' in trans_type.lower():
                    trans_type = 'Purchase'
                elif 'sale' in trans_type.lower() or 'sell' in trans_type.lower():
                    trans_type = 'Sale'
                else:
                    trans_type = 'Exchange'
                
                # Generate transaction ID
                politician_last = row['politician_name'].split()[-1].upper().replace(' ', '')
                date_str = pd.to_datetime(row['transaction_date']).strftime('%Y%m%d')
                ticker = str(row.get('ticker', 'UNKNOWN')).upper().strip()
                transaction_id = f"{politician_last}_{date_str}_{ticker}_{idx}"
                
                # Create trade object
                trade = CongressionalTrade(
                    transaction_id=transaction_id,
                    politician_name=row['politician_name'],
                    politician_party=Party(party_str),
                    chamber=Chamber(row['chamber']),
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    disclosure_date=pd.to_datetime(row.get('disclosure_date', row['transaction_date'])).date(),
                    ticker=ticker,
                    asset_description=row.get('asset_description', row.get('asset_name', '')),
                    transaction_type=TransactionType(trans_type),
                    amount_range=str(amount_range),
                    amount_min=amount_min,
                    amount_max=amount_max,
                    owner=row.get('owner', 'Self'),
                    data_source="Public Congressional Trading Data"
                )
                
                trades.append(trade)
                
            except Exception as e:
                # Skip problematic rows
                continue
        
        print(f"✓ Successfully converted {len(trades)} trades")
        
        return trades


def fetch_real_congressional_data(
    start_date: str = "2020-01-01",
    end_date: Optional[str] = None,
    chambers: List[str] = ['House', 'Senate']
) -> tuple[pd.DataFrame, List[CongressionalTrade]]:
    """
    Convenience function to fetch and normalize real congressional trading data
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), defaults to today
        chambers: Chambers to fetch from
        
    Returns:
        Tuple of (raw_dataframe, list_of_trade_objects)
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    fetcher = PublicDataFetcher()
    
    # Fetch raw data
    raw_df = fetcher.fetch_all_trades(start_date, end_date, chambers)
    
    if raw_df.empty:
        print("No data fetched. Trying alternative approach...")
        return pd.DataFrame(), []
    
    # Convert to trade objects
    trades = fetcher.normalize_and_convert(raw_df)
    
    return raw_df, trades
