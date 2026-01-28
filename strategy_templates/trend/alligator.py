"""Williams Alligator and Gator Oscillator"""
import pandas as pd
from typing import Dict
from ..base import Strategy


class AlligatorStrategy(Strategy):
    """
    Williams Alligator Strategy
    
    Logic: Buy when all lines aligned bullish, sell when aligned bearish
    Best for: Trending markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("AlligatorStrategy", params)
        self.jaw_period = params.get("jaw_period", 13)
        self.teeth_period = params.get("teeth_period", 8)
        self.lips_period = params.get("lips_period", 5)
        
        self.rules = [
            {"type": "entry_long", "condition": "lips > teeth > jaw (bullish alignment)"},
            {"type": "entry_short", "condition": "lips < teeth < jaw (bearish alignment)"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # Calculate median price
        if "high" in df.columns and "low" in df.columns:
            median = (df["high"] + df["low"]) / 2
        else:
            median = price
        
        # Alligator lines (SMMA approximation with EMA)
        jaw = median.ewm(span=self.jaw_period, adjust=False).mean().shift(8)
        teeth = median.ewm(span=self.teeth_period, adjust=False).mean().shift(5)
        lips = median.ewm(span=self.lips_period, adjust=False).mean().shift(3)
        
        # Bullish: lips > teeth > jaw
        bullish = (lips > teeth) & (teeth > jaw)
        # Bearish: lips < teeth < jaw
        bearish = (lips < teeth) & (teeth < jaw)
        
        signals[bullish & ~bullish.shift(1).fillna(False)] = 1
        signals[bearish & ~bearish.shift(1).fillna(False)] = -1
        
        return signals


class GatorOscillator(Strategy):
    """
    Gator Oscillator Strategy
    
    Logic: Trade when gator wakes up (bars expand)
    Best for: Trend strength confirmation
    """
    
    def __init__(self, params: Dict):
        super().__init__("GatorOscillator", params)
        self.jaw_period = params.get("jaw_period", 13)
        self.teeth_period = params.get("teeth_period", 8)
        self.lips_period = params.get("lips_period", 5)
        
        self.rules = [
            {"type": "entry_long", "condition": "gator waking up (bars expanding) with bullish trend"},
            {"type": "entry_short", "condition": "gator waking up (bars expanding) with bearish trend"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        if "high" in df.columns and "low" in df.columns:
            median = (df["high"] + df["low"]) / 2
        else:
            median = price
        
        jaw = median.ewm(span=self.jaw_period, adjust=False).mean().shift(8)
        teeth = median.ewm(span=self.teeth_period, adjust=False).mean().shift(5)
        lips = median.ewm(span=self.lips_period, adjust=False).mean().shift(3)
        
        # Gator oscillator
        upper_bar = abs(jaw - teeth)
        lower_bar = abs(teeth - lips)
        
        # Gator waking: both bars expanding
        upper_expanding = upper_bar > upper_bar.shift(1)
        lower_expanding = lower_bar > lower_bar.shift(1)
        waking = upper_expanding & lower_expanding
        
        # Determine direction
        bullish = (lips > teeth) & (teeth > jaw)
        
        signals[waking & bullish] = 1
        signals[waking & ~bullish] = -1
        
        return signals
