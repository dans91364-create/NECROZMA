"""SuperTrend Strategy"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class SuperTrend(Strategy):
    """
    SuperTrend Strategy
    
    Logic: Buy when price crosses above SuperTrend, sell when crosses below
    Best for: Strong trending markets with volatility
    """
    
    def __init__(self, params: Dict):
        super().__init__("SuperTrend", params)
        self.period = params.get("period", 10)
        self.multiplier = params.get("multiplier", 3.0)
        
        self.rules = [
            {"type": "entry_long", "condition": "price crosses above SuperTrend line"},
            {"type": "entry_short", "condition": "price crosses below SuperTrend line"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # ATR calculation
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            
            # Basic bands
            hl_avg = (high + low) / 2
            upper_band = hl_avg + self.multiplier * atr
            lower_band = hl_avg - self.multiplier * atr
            
            # SuperTrend
            supertrend = pd.Series(index=df.index, dtype=float)
            direction = pd.Series(1, index=df.index)
            
            for i in range(self.period, len(df)):
                if close.iloc[i] <= upper_band.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1
                elif close.iloc[i] >= lower_band.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    direction.iloc[i] = direction.iloc[i-1]
            
            signals[(direction == 1) & (direction.shift(1) == -1)] = 1
            signals[(direction == -1) & (direction.shift(1) == 1)] = -1
        
        return signals
