"""ADX and DMI Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class ADXTrend(Strategy):
    """
    ADX Trend Strategy
    
    Logic: Buy when ADX > threshold and +DI > -DI, sell when ADX > threshold and -DI > +DI
    Best for: Strong trending markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("ADXTrend", params)
        self.period = params.get("period", 14)
        self.threshold = params.get("threshold", 25)
        
        self.rules = [
            {"type": "entry_long", "condition": f"ADX > {self.threshold} and +DI > -DI"},
            {"type": "entry_short", "condition": f"ADX > {self.threshold} and -DI > +DI"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            
            # Directional Movement
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = pd.Series(0, index=df.index)
            minus_dm = pd.Series(0, index=df.index)
            
            plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
            minus_dm[(down_move > up_move) & (down_move > 0)] = down_move
            
            plus_di = 100 * (plus_dm.rolling(self.period).mean() / (atr + EPSILON))
            minus_di = 100 * (minus_dm.rolling(self.period).mean() / (atr + EPSILON))
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + EPSILON)
            adx = dx.rolling(self.period).mean()
            
            signals[(adx > self.threshold) & (plus_di > minus_di)] = 1
            signals[(adx > self.threshold) & (minus_di > plus_di)] = -1
        
        return signals


class DMICrossover(Strategy):
    """
    DMI Crossover Strategy
    
    Logic: Buy when +DI crosses above -DI, sell when -DI crosses above +DI
    Best for: Trend direction changes
    """
    
    def __init__(self, params: Dict):
        super().__init__("DMICrossover", params)
        self.period = params.get("period", 14)
        
        self.rules = [
            {"type": "entry_long", "condition": "+DI crosses above -DI"},
            {"type": "entry_short", "condition": "-DI crosses above +DI"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = pd.Series(0, index=df.index)
            minus_dm = pd.Series(0, index=df.index)
            
            plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
            minus_dm[(down_move > up_move) & (down_move > 0)] = down_move
            
            plus_di = 100 * (plus_dm.rolling(self.period).mean() / (atr + EPSILON))
            minus_di = 100 * (minus_dm.rolling(self.period).mean() / (atr + EPSILON))
            
            signals[(plus_di > minus_di) & (plus_di.shift(1) <= minus_di.shift(1))] = 1
            signals[(minus_di > plus_di) & (minus_di.shift(1) <= plus_di.shift(1))] = -1
        
        return signals
