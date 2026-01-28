"""Vortex Indicator Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON


class VortexCrossover(Strategy):
    """
    Vortex Indicator Strategy
    
    Logic: Buy when VI+ crosses above VI-, sell when VI- crosses above VI+
    Best for: Trend reversal identification
    """
    
    def __init__(self, params: Dict):
        super().__init__("VortexCrossover", params)
        self.period = params.get("period", 14)
        
        self.rules = [
            {"type": "entry_long", "condition": "VI+ crosses above VI-"},
            {"type": "entry_short", "condition": "VI- crosses above VI+"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # Vortex Movement
            vm_plus = abs(high - low.shift(1))
            vm_minus = abs(low - high.shift(1))
            
            # True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Vortex Indicators
            vi_plus = vm_plus.rolling(self.period).sum() / (tr.rolling(self.period).sum() + EPSILON)
            vi_minus = vm_minus.rolling(self.period).sum() / (tr.rolling(self.period).sum() + EPSILON)
            
            signals[(vi_plus > vi_minus) & (vi_plus.shift(1) <= vi_minus.shift(1))] = 1
            signals[(vi_minus > vi_plus) & (vi_minus.shift(1) <= vi_plus.shift(1))] = -1
        
        return signals
