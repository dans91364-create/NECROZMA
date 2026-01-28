"""Keltner Channel Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON


class KeltnerBreakout(Strategy):
    """
    Keltner Channel Breakout
    
    Logic: Buy when price breaks above upper Keltner, sell when breaks below lower Keltner
    Best for: Volatile breakout moves
    """
    
    def __init__(self, params: Dict):
        super().__init__("KeltnerBreakout", params)
        self.ema_period = params.get("ema_period", 20)
        self.atr_period = params.get("atr_period", 10)
        self.multiplier = params.get("multiplier", 2.0)
        
        self.rules = [
            {"type": "entry_long", "condition": "price breaks above upper Keltner channel"},
            {"type": "entry_short", "condition": "price breaks below lower Keltner channel"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # EMA of close
            ema = close.ewm(span=self.ema_period, adjust=False).mean()
            
            # ATR
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(self.atr_period).mean()
            
            # Keltner Channels
            upper_band = ema + self.multiplier * atr
            lower_band = ema - self.multiplier * atr
            
            signals[(close > upper_band)] = 1
            signals[(close < lower_band)] = -1
        
        return signals
