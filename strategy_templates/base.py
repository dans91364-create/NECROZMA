"""
Base Strategy Class for NECROZMA Trading System
"""
from typing import Dict
import pandas as pd

EPSILON = 1e-10  # Small value to prevent division by zero


class Strategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str, params: Dict):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params
        self.rules = []
        
    def add_rule(self, rule: Dict):
        """Add a trading rule"""
        self.rules.append(rule)
    
    @staticmethod
    def extract_date_from_index(index_value):
        """
        Extract date from index value with multiple fallback methods
        
        Args:
            index_value: pandas index value (could be Timestamp, datetime, or string)
            
        Returns:
            Extracted date as string in YYYY-MM-DD format for consistent comparison
        """
        if hasattr(index_value, 'date'):
            return str(index_value.date())
        elif hasattr(index_value, 'strftime'):
            return str(index_value)[:10]
        else:
            return str(index_value)[:10]
    
    def apply_max_trades_per_day_filter(self, signals: pd.Series, df: pd.DataFrame, 
                                       buy_signal: pd.Series, sell_signal: pd.Series,
                                       max_trades_per_day: int) -> pd.Series:
        """
        Apply max trades per day limit to signals
        
        Args:
            signals: Empty signal series to populate
            df: DataFrame with index (must have DatetimeIndex or convertible index)
            buy_signal: Boolean series indicating buy signals
            sell_signal: Boolean series indicating sell signals
            max_trades_per_day: Maximum number of trades allowed per day
            
        Returns:
            Signal series with max trades per day limit applied
        """
        total_trades_today = 0
        current_day = ""
        
        for i in range(len(signals)):
            current_time = df.index[i]
            trade_date = self.extract_date_from_index(current_time)
            
            if trade_date != current_day:
                current_day = trade_date
                total_trades_today = 0
            
            if total_trades_today >= max_trades_per_day:
                continue
            
            if buy_signal.iloc[i]:
                signals.iloc[i] = 1
                total_trades_today += 1
            elif sell_signal.iloc[i]:
                signals.iloc[i] = -1
                total_trades_today += 1
        
        return signals
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals
        
        Args:
            df: DataFrame with features
            
        Returns:
            Series with signals (1=buy, -1=sell, 0=neutral)
        """
        raise NotImplementedError("Subclasses must implement generate_signals")
    
    def to_dict(self) -> Dict:
        """Convert strategy to dictionary"""
        return {
            "name": self.name,
            "params": self.params,
            "rules": self.rules,
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
