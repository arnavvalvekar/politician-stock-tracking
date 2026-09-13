"""
Data validation and cleaning pipeline for congressional trading data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import re


class DataValidator:
    """Validate and clean congressional trading data"""
    
    # Valid ticker patterns
    TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}$')
    
    # Known invalid tickers
    INVALID_TICKERS = {
        'N/A', 'NA', 'UNKNOWN', 'CASH', 'VARIOUS', 'MULTIPLE',
        'SEE', 'ATTACHED', 'STATEMENT', 'FORM', 'NONE'
    }
    
    def __init__(self):
        self.validation_report = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'issues': []
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate and clean DataFrame
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Tuple of (cleaned_df, validation_report)
        """
        print("\n" + "="*60)
        print("DATA VALIDATION AND CLEANING")
        print("="*60)
        
        self.validation_report['total_records'] = len(df)
        original_count = len(df)
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # 1. Check required columns
        print("\n[1/8] Checking required columns...")
        required_cols = ['politician_name', 'ticker', 'transaction_date', 'chamber']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            self.validation_report['issues'].append(f"Missing required columns: {missing_cols}")
            print(f"  ✗ Missing columns: {missing_cols}")
            return pd.DataFrame(), self.validation_report
        print(f"  ✓ All required columns present")
        
        # 2. Clean politician names
        print("\n[2/8] Cleaning politician names...")
        df['politician_name'] = df['politician_name'].str.strip()
        df['politician_name'] = df['politician_name'].str.title()
        # Remove extra whitespace
        df['politician_name'] = df['politician_name'].str.replace(r'\s+', ' ', regex=True)
        print(f"  ✓ Cleaned {df['politician_name'].nunique()} unique politician names")
        
        # 3. Validate and clean tickers
        print("\n[3/8] Validating tickers...")
        initial_ticker_count = len(df)
        
        # Clean tickers
        df['ticker'] = df['ticker'].astype(str).str.upper().str.strip()
        
        # Remove invalid tickers
        df = df[~df['ticker'].isin(self.INVALID_TICKERS)]
        df = df[df['ticker'].str.match(self.TICKER_PATTERN, na=False)]
        
        removed = initial_ticker_count - len(df)
        if removed > 0:
            self.validation_report['issues'].append(f"Removed {removed} records with invalid tickers")
            print(f"  ⚠ Removed {removed} records with invalid tickers")
        print(f"  ✓ {len(df)} records with valid tickers remaining")
        print(f"    Unique tickers: {df['ticker'].nunique()}")
        
        # 4. Validate dates
        print("\n[4/8] Validating dates...")
        date_cols = ['transaction_date', 'disclosure_date']
        
        for col in date_cols:
            if col in df.columns:
                # Convert to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Remove records with invalid dates
                invalid_dates = df[col].isna().sum()
                if invalid_dates > 0:
                    self.validation_report['issues'].append(f"{invalid_dates} records with invalid {col}")
                    print(f"  ⚠ Removing {invalid_dates} records with invalid {col}")
                    df = df[df[col].notna()]
                
                # Check for future dates
                future_dates = (df[col] > pd.Timestamp.now()).sum()
                if future_dates > 0:
                    self.validation_report['issues'].append(f"{future_dates} records with future {col}")
                    print(f"  ⚠ Removing {future_dates} records with future {col}")
                    df = df[df[col] <= pd.Timestamp.now()]
        
        print(f"  ✓ All dates valid")
        
        # 5. Validate filing delays
        print("\n[5/8] Checking filing delays...")
        if 'disclosure_date' in df.columns:
            df['filing_delay_days'] = (df['disclosure_date'] - df['transaction_date']).dt.days
            
            # Flag suspicious delays (negative or > 365 days)
            negative_delays = (df['filing_delay_days'] < 0).sum()
            excessive_delays = (df['filing_delay_days'] > 365).sum()
            
            if negative_delays > 0:
                self.validation_report['issues'].append(f"{negative_delays} records with negative filing delay")
                print(f"  ⚠ Removing {negative_delays} records with negative filing delay")
                df = df[df['filing_delay_days'] >= 0]
            
            if excessive_delays > 0:
                self.validation_report['issues'].append(f"{excessive_delays} records with >365 day delay")
                print(f"  ⚠ Found {excessive_delays} records with excessive delay (>365 days)")
            
            print(f"  ✓ Median filing delay: {df['filing_delay_days'].median():.0f} days")
        
        # 6. Clean transaction types
        print("\n[6/8] Standardizing transaction types...")
        if 'transaction_type' in df.columns:
            df['transaction_type'] = df['transaction_type'].str.strip()
            
            # Standardize variations
            df['transaction_type'] = df['transaction_type'].replace({
                'purchase': 'Purchase',
                'buy': 'Purchase',
                'sale': 'Sale',
                'sell': 'Sale',
                'sale_full': 'Sale',
                'sale_partial': 'Sale (Partial)',
                'purchase_full': 'Purchase',
                'purchase_partial': 'Purchase (Partial)',
            }, regex=False)
            
            print(f"  ✓ Transaction types: {df['transaction_type'].value_counts().to_dict()}")
        
        # 7. Validate amount ranges
        print("\n[7/8] Validating amount ranges...")
        if 'amount' in df.columns:
            df = df.rename(columns={'amount': 'amount_range'})
        
        if 'amount_range' in df.columns:
            # Remove records with missing amounts
            missing_amounts = df['amount_range'].isna().sum()
            if missing_amounts > 0:
                print(f"  ⚠ Removing {missing_amounts} records with missing amounts")
                df = df[df['amount_range'].notna()]
            
            print(f"  ✓ All records have amount information")
        
        # 8. Remove duplicates
        print("\n[8/8] Removing duplicates...")
        duplicate_cols = ['politician_name', 'ticker', 'transaction_date', 'transaction_type']
        duplicates = df.duplicated(subset=duplicate_cols, keep='first').sum()
        
        if duplicates > 0:
            self.validation_report['issues'].append(f"Removed {duplicates} duplicate records")
            print(f"  ⚠ Removing {duplicates} duplicate records")
            df = df.drop_duplicates(subset=duplicate_cols, keep='first')
        
        print(f"  ✓ No duplicates remaining")
        
        # Final summary
        self.validation_report['valid_records'] = len(df)
        self.validation_report['invalid_records'] = original_count - len(df)
        
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Original records:  {original_count:,}")
        print(f"Valid records:     {len(df):,}")
        print(f"Removed records:   {original_count - len(df):,} ({(original_count - len(df))/original_count*100:.1f}%)")
        print(f"Data quality:      {len(df)/original_count*100:.1f}%")
        
        if len(df) > 0:
            print(f"\nDate range:        {df['transaction_date'].min().date()} to {df['transaction_date'].max().date()}")
            print(f"Politicians:       {df['politician_name'].nunique()}")
            print(f"Tickers:           {df['ticker'].nunique()}")
            print(f"Avg filing delay:  {df['filing_delay_days'].mean():.0f} days" if 'filing_delay_days' in df.columns else "")
        
        return df, self.validation_report
    
    def enrich_with_party_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich data with party affiliation (using common knowledge)
        
        Args:
            df: DataFrame with politician names
            
        Returns:
            DataFrame with party column added
        """
        # Common politician party mappings (as of 2024)
        party_map = {
            # Notable Democrats
            'Nancy Pelosi': 'D',
            'Josh Gottheimer': 'D',
            'Ro Khanna': 'D',
            'Mark Kelly': 'D',
            'Jon Ossoff': 'D',
            'Sheldon Whitehouse': 'D',
            'Debbie Stabenow': 'D',
            
            # Notable Republicans
            'Tommy Tuberville': 'R',
            'Dan Crenshaw': 'R',
            'Marsha Blackburn': 'R',
            'Rick Scott': 'R',
            'Pat Toomey': 'R',
            'Richard Burr': 'R',
            'Rand Paul': 'R',
            
            # Independents
            'Angus King': 'I',
            'Bernie Sanders': 'I',
        }
        
        if 'party' not in df.columns or df['party'].isna().all():
            df['party'] = df['politician_name'].map(party_map).fillna('I')
            print(f"✓ Added party affiliation for {(df['party'] != 'I').sum()} politicians")
        
        return df
    
    def get_quality_report(self) -> str:
        """Generate a detailed quality report"""
        report = []
        report.append("="*60)
        report.append("DATA QUALITY REPORT")
        report.append("="*60)
        report.append(f"Total Records Processed: {self.validation_report['total_records']:,}")
        report.append(f"Valid Records: {self.validation_report['valid_records']:,}")
        report.append(f"Invalid Records: {self.validation_report['invalid_records']:,}")
        report.append(f"Data Quality: {self.validation_report['valid_records']/self.validation_report['total_records']*100:.1f}%")
        
        if self.validation_report['issues']:
            report.append("\nIssues Found:")
            for issue in self.validation_report['issues']:
                report.append(f"  • {issue}")
        else:
            report.append("\nNo issues found!")
        
        return "\n".join(report)
