"""Donchian Channel Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy


class DonchianBreakout(Strategy):
    """
    Donchian Channel Breakout
    
    Logic: Buy when price breaks above upper channel, sell when breaks below lower channel
    Best for: Breakout trading in trending markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("DonchianBreakout", params)
        self.period = params.get("period", 20)
        
        self.rules = [
            {"type": "entry_long", "condition": f"price breaks above {self.period}-period high"},
            {"type": "entry_short", "condition": f"price breaks below {self.period}-period low"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            upper_band = high.rolling(self.period).max()
            lower_band = low.rolling(self.period).min()
            
            signals[(close > upper_band.shift(1))] = 1
            signals[(close < lower_band.shift(1))] = -1
        
        return signals
