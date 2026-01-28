"""Bollinger Bands Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON


class BollingerBounce(Strategy):
    """Bollinger Bands Bounce - Buy at lower band, sell at upper band"""
    def __init__(self, params: Dict):
        super().__init__("BollingerBounce", params)
        self.period = params.get("period", 20)
        self.std_dev = params.get("std_dev", 2.0)
        self.rules = [
            {"type": "entry_long", "condition": "price touches lower Bollinger Band"},
            {"type": "entry_short", "condition": "price touches upper Bollinger Band"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        sma = price.rolling(self.period).mean()
        std = price.rolling(self.period).std()
        upper = sma + self.std_dev * std
        lower = sma - self.std_dev * std
        signals[price <= lower] = 1
        signals[price >= upper] = -1
        return signals


class BollingerSqueeze(Strategy):
    """Bollinger Squeeze - Trade breakouts after low volatility"""
    def __init__(self, params: Dict):
        super().__init__("BollingerSqueeze", params)
        self.period = params.get("period", 20)
        self.std_dev = params.get("std_dev", 2.0)
        self.squeeze_threshold = params.get("squeeze_threshold", 0.02)
        self.rules = [
            {"type": "entry_long", "condition": "bandwidth low then price breaks up"},
            {"type": "entry_short", "condition": "bandwidth low then price breaks down"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        sma = price.rolling(self.period).mean()
        std = price.rolling(self.period).std()
        upper = sma + self.std_dev * std
        lower = sma - self.std_dev * std
        bandwidth = (upper - lower) / (sma + EPSILON)
        squeeze = bandwidth < self.squeeze_threshold
        signals[(price > sma) & squeeze.shift(1)] = 1
        signals[(price < sma) & squeeze.shift(1)] = -1
        return signals


class BollingerBreakout(Strategy):
    """Bollinger Breakout - Trade strong moves beyond bands"""
    def __init__(self, params: Dict):
        super().__init__("BollingerBreakout", params)
        self.period = params.get("period", 20)
        self.std_dev = params.get("std_dev", 2.0)
        self.rules = [
            {"type": "entry_long", "condition": "price breaks above upper band"},
            {"type": "entry_short", "condition": "price breaks below lower band"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        sma = price.rolling(self.period).mean()
        std = price.rolling(self.period).std()
        upper = sma + self.std_dev * std
        lower = sma - self.std_dev * std
        signals[(price > upper) & (price.shift(1) <= upper.shift(1))] = 1
        signals[(price < lower) & (price.shift(1) >= lower.shift(1))] = -1
        return signals


class BollingerPercentB(Strategy):
    """Bollinger %B - Position within bands"""
    def __init__(self, params: Dict):
        super().__init__("BollingerPercentB", params)
        self.period = params.get("period", 20)
        self.std_dev = params.get("std_dev", 2.0)
        self.oversold = params.get("oversold", 0.2)
        self.overbought = params.get("overbought", 0.8)
        self.rules = [
            {"type": "entry_long", "condition": "%B crosses above 0.2"},
            {"type": "entry_short", "condition": "%B crosses above 0.8"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        sma = price.rolling(self.period).mean()
        std = price.rolling(self.period).std()
        upper = sma + self.std_dev * std
        lower = sma - self.std_dev * std
        percent_b = (price - lower) / ((upper - lower) + EPSILON)
        signals[(percent_b > self.oversold) & (percent_b.shift(1) <= self.oversold)] = 1
        signals[(percent_b > self.overbought) & (percent_b.shift(1) <= self.overbought)] = -1
        return signals
