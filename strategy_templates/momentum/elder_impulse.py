"""Elder Impulse System"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class ElderImpulse(Strategy):
    """Elder Impulse System"""
    def __init__(self, params: Dict):
        super().__init__("ElderImpulse", params)
        self.ema_period = params.get("ema_period", 13)
        self.macd_fast = params.get("macd_fast", 12)
        self.macd_slow = params.get("macd_slow", 26)
        self.rules = [{"type": "entry_long", "condition": "EMA up and MACD histogram up (green bar)"},
                     {"type": "entry_short", "condition": "EMA down and MACD histogram down (red bar)"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        ema = price.ewm(span=self.ema_period, adjust=False).mean()
        fast_ema = price.ewm(span=self.macd_fast, adjust=False).mean()
        slow_ema = price.ewm(span=self.macd_slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        ema_up = ema > ema.shift(1)
        macd_up = macd > macd.shift(1)
        signals[ema_up & macd_up] = 1
        signals[~ema_up & ~macd_up] = -1
        return signals

class ElderRay(Strategy):
    """Elder Ray Index"""
    def __init__(self, params: Dict):
        super().__init__("ElderRay", params)
        self.ema_period = params.get("ema_period", 13)
        self.rules = [{"type": "entry_long", "condition": "bull power positive and bear power rising"},
                     {"type": "entry_short", "condition": "bear power negative and bull power falling"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            close = df.get("close", df.get("mid_price"))
            ema = close.ewm(span=self.ema_period, adjust=False).mean()
            bull_power = high - ema
            bear_power = low - ema
            signals[(bull_power > 0) & (bear_power > bear_power.shift(1))] = 1
            signals[(bear_power < 0) & (bull_power < bull_power.shift(1))] = -1
        return signals
