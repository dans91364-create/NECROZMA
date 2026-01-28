"""Parabolic SAR Strategy"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy


class ParabolicSAR(Strategy):
    """
    Parabolic SAR Strategy
    
    Logic: Buy when price crosses above SAR, sell when price crosses below SAR
    Best for: Trending markets, trailing stop system
    """
    
    def __init__(self, params: Dict):
        super().__init__("ParabolicSAR", params)
        self.af_start = params.get("af_start", 0.02)
        self.af_increment = params.get("af_increment", 0.02)
        self.af_max = params.get("af_max", 0.2)
        
        self.rules = [
            {"type": "entry_long", "condition": "price crosses above SAR"},
            {"type": "entry_short", "condition": "price crosses below SAR"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # Simplified SAR calculation
            sar = pd.Series(index=df.index, dtype=float)
            trend = pd.Series(1, index=df.index)  # 1 for up, -1 for down
            af = self.af_start
            ep = high.iloc[0]
            
            sar.iloc[0] = low.iloc[0]
            
            for i in range(1, len(df)):
                if trend.iloc[i-1] == 1:
                    sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                    
                    if low.iloc[i] < sar.iloc[i]:
                        trend.iloc[i] = -1
                        sar.iloc[i] = ep
                        ep = low.iloc[i]
                        af = self.af_start
                    else:
                        trend.iloc[i] = 1
                        if high.iloc[i] > ep:
                            ep = high.iloc[i]
                            af = min(af + self.af_increment, self.af_max)
                else:
                    sar.iloc[i] = sar.iloc[i-1] - af * (sar.iloc[i-1] - ep)
                    
                    if high.iloc[i] > sar.iloc[i]:
                        trend.iloc[i] = 1
                        sar.iloc[i] = ep
                        ep = high.iloc[i]
                        af = self.af_start
                    else:
                        trend.iloc[i] = -1
                        if low.iloc[i] < ep:
                            ep = low.iloc[i]
                            af = min(af + self.af_increment, self.af_max)
            
            signals[(close > sar) & (close.shift(1) <= sar.shift(1))] = 1
            signals[(close < sar) & (close.shift(1) >= sar.shift(1))] = -1
        
        return signals
