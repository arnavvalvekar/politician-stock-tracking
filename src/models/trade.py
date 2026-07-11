"""Data models for congressional trading analysis"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class TransactionType(Enum):
    """Type of transaction"""
    PURCHASE = "Purchase"
    SALE = "Sale"
    EXCHANGE = "Exchange"
    PURCHASE_PARTIAL = "Purchase (Partial)"
    SALE_PARTIAL = "Sale (Partial)"


class Chamber(Enum):
    """Congressional chamber"""
    SENATE = "Senate"
    HOUSE = "House"


class Party(Enum):
    """Political party"""
    DEMOCRAT = "D"
    REPUBLICAN = "R"
    INDEPENDENT = "I"


@dataclass
class CongressionalTrade:
    """Represents a single congressional stock trade"""
    
    transaction_id: str
    politician_name: str
    politician_party: Party
    chamber: Chamber
    transaction_date: date
    disclosure_date: date
    ticker: str
    asset_description: str
    transaction_type: TransactionType
    amount_range: str
    amount_min: float
    amount_max: float
    owner: str = "Self"
    comment: Optional[str] = None
    capital_gains_over_200: bool = False
    filing_id: Optional[str] = None
    data_source: str = "Manual"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Convert string enums to proper enum types"""
        if isinstance(self.politician_party, str):
            self.politician_party = Party(self.politician_party)
        if isinstance(self.chamber, str):
            self.chamber = Chamber(self.chamber)
        if isinstance(self.transaction_type, str):
            self.transaction_type = TransactionType(self.transaction_type)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def filing_delay_days(self) -> int:
        """Calculate days between transaction and disclosure"""
        return (self.disclosure_date - self.transaction_date).days
    
    @property
    def amount_estimated(self) -> float:
        """Estimate transaction amount as midpoint of range"""
        return (self.amount_min + self.amount_max) / 2
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'transaction_id': self.transaction_id,
            'politician_name': self.politician_name,
            'politician_party': self.politician_party.value,
            'chamber': self.chamber.value,
            'transaction_date': self.transaction_date,
            'disclosure_date': self.disclosure_date,
            'filing_delay_days': self.filing_delay_days,
            'ticker': self.ticker,
            'asset_description': self.asset_description,
            'transaction_type': self.transaction_type.value,
            'amount_range': self.amount_range,
            'amount_min': self.amount_min,
            'amount_max': self.amount_max,
            'amount_estimated': self.amount_estimated,
            'owner': self.owner,
            'comment': self.comment,
            'capital_gains_over_200': self.capital_gains_over_200,
            'filing_id': self.filing_id,
            'data_source': self.data_source,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CongressionalTrade':
        """Create instance from dictionary"""
        return cls(
            transaction_id=data['transaction_id'],
            politician_name=data['politician_name'],
            politician_party=Party(data['politician_party']),
            chamber=Chamber(data['chamber']),
            transaction_date=data['transaction_date'],
            disclosure_date=data['disclosure_date'],
            ticker=data['ticker'],
            asset_description=data['asset_description'],
            transaction_type=TransactionType(data['transaction_type']),
            amount_range=data['amount_range'],
            amount_min=data['amount_min'],
            amount_max=data['amount_max'],
            owner=data.get('owner', 'Self'),
            comment=data.get('comment'),
            capital_gains_over_200=data.get('capital_gains_over_200', False),
            filing_id=data.get('filing_id'),
            data_source=data.get('data_source', 'Manual'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


@dataclass
class StockPrice:
    """Represents stock price data for a single day"""
    
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
    dividend: Optional[float] = None
    split_ratio: Optional[float] = None
    data_source: str = "Yahoo Finance"
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.adjusted_close is None:
            self.adjusted_close = self.close
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'ticker': self.ticker,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'adjusted_close': self.adjusted_close,
            'volume': self.volume,
            'dividend': self.dividend,
            'split_ratio': self.split_ratio,
            'data_source': self.data_source,
            'created_at': self.created_at,
        }


@dataclass
class Politician:
    """Represents a politician's profile"""
    
    politician_id: str
    full_name: str
    first_name: str
    last_name: str
    party: Party
    chamber: Chamber
    state: str
    district: Optional[str] = None
    committees: list = field(default_factory=list)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    website: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.party, str):
            self.party = Party(self.party)
        if isinstance(self.chamber, str):
            self.chamber = Chamber(self.chamber)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'politician_id': self.politician_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'party': self.party.value,
            'chamber': self.chamber.value,
            'state': self.state,
            'district': self.district,
            'committees': self.committees,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'website': self.website,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


# Amount range mapping for STOCK Act disclosures
AMOUNT_RANGES = {
    'A': (1_001, 15_000),
    'B': (15_001, 50_000),
    'C': (50_001, 100_000),
    'D': (100_001, 250_000),
    'E': (250_001, 500_000),
    'F': (500_001, 1_000_000),
    'G': (1_000_001, 5_000_000),
    'H': (5_000_001, 25_000_000),
    'I': (25_000_001, 50_000_000),
    'J': (50_000_001, 100_000_000),
}


def parse_amount_range(amount_str: str) -> tuple[float, float]:
    """
    Parse amount range string into min and max values
    
    Args:
        amount_str: String like "$15,001 - $50,000" or range code like "B"
        
    Returns:
        Tuple of (min_amount, max_amount)
    """
    # Check if it's a range code
    if amount_str.strip().upper() in AMOUNT_RANGES:
        return AMOUNT_RANGES[amount_str.strip().upper()]
    
    # Try to parse dollar range
    try:
        # Remove $ and commas, split on -
        cleaned = amount_str.replace('$', '').replace(',', '')
        parts = [p.strip() for p in cleaned.split('-')]
        
        if len(parts) == 2:
            return (float(parts[0]), float(parts[1]))
        elif 'Over' in amount_str or 'over' in amount_str:
            # Handle "Over $50,000,000"
            amount = float(cleaned.split()[-1])
            return (amount, amount * 2)  # Estimate upper bound
    except Exception as e:
        print(f"Warning: Could not parse amount range '{amount_str}': {e}")
    
    # Default fallback
    return (1_000, 15_000)
