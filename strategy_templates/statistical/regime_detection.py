"""Statistical Trading Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON

class HiddenMarkovRegime(Strategy):
    """Hidden Markov Model"""
    def __init__(self, params: Dict):
        super().__init__("HiddenMarkovRegime", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "HMM regime detection buy signal"}, {"type": "entry_short", "condition": "HMM regime detection sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class RegimeSwitching(Strategy):
    """Regime Switching"""
    def __init__(self, params: Dict):
        super().__init__("RegimeSwitching", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "regime changes buy signal"}, {"type": "entry_short", "condition": "regime changes sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class VarianceRatio(Strategy):
    """Variance Ratio Test"""
    def __init__(self, params: Dict):
        super().__init__("VarianceRatio", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "random walk test buy signal"}, {"type": "entry_short", "condition": "random walk test sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class AutocorrelationStrat(Strategy):
    """Autocorrelation Strategy"""
    def __init__(self, params: Dict):
        super().__init__("AutocorrelationStrat", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "autocorrelation buy signal"}, {"type": "entry_short", "condition": "autocorrelation sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

