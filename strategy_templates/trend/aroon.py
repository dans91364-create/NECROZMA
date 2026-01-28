"""Aroon Indicator Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy


class AroonCrossover(Strategy):
    """
    Aroon Crossover Strategy
    
    Logic: Buy when Aroon Up crosses above Aroon Down, sell when crosses below
    Best for: Detecting trend changes
    """
    
    def __init__(self, params: Dict):
        super().__init__("AroonCrossover", params)
        self.period = params.get("period", 25)
        
        self.rules = [
            {"type": "entry_long", "condition": "Aroon Up crosses above Aroon Down"},
            {"type": "entry_short", "condition": "Aroon Down crosses above Aroon Up"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            
            # Aroon Up: periods since highest high
            aroon_up = high.rolling(self.period + 1).apply(
                lambda x: (self.period - (self.period - x.argmax())) / self.period * 100, raw=False
            )
            
            # Aroon Down: periods since lowest low
            aroon_down = low.rolling(self.period + 1).apply(
                lambda x: (self.period - (self.period - x.argmin())) / self.period * 100, raw=False
            )
            
            signals[(aroon_up > aroon_down) & (aroon_up.shift(1) <= aroon_down.shift(1))] = 1
            signals[(aroon_down > aroon_up) & (aroon_down.shift(1) <= aroon_up.shift(1))] = -1
        
        return signals
