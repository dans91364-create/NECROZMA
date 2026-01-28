"""Accumulation/Distribution Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class AccumDistribution(Strategy):
    def __init__(self, params: Dict):
        super().__init__("AccumDistribution", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "A/D rising"}, {"type": "entry_short", "condition": "A/D falling"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            close = df.get("close", df.get("mid_price"))
            clv = ((close - df["low"]) - (df["high"] - close)) / (df["high"] - df["low"] + EPSILON)
            ad = (clv * df["volume"]).cumsum()
            ad_sma = ad.rolling(self.period).mean()
            signals[(ad > ad_sma) & (ad.shift(1) <= ad_sma.shift(1))], signals[(ad < ad_sma) & (ad.shift(1) >= ad_sma.shift(1))] = 1, -1
        return signals
class AccumDistDivergence(Strategy):
    def __init__(self, params: Dict):
        super().__init__("AccumDistDivergence", params)
        self.lookback = params.get("lookback", 5)
        self.rules = [{"type": "entry_long", "condition": "bullish A/D divergence"}, {"type": "entry_short", "condition": "bearish A/D divergence"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            price, close = df.get("mid_price", df.get("close", df.get("Close"))), df.get("close", df.get("mid_price"))
            clv = ((close - df["low"]) - (df["high"] - close)) / (df["high"] - df["low"] + EPSILON)
            ad = (clv * df["volume"]).cumsum()
            price_low = price.rolling(self.lookback).min()
            signals[(price == price_low) & (ad > ad.shift(self.lookback))], signals[(price == price.rolling(self.lookback).max()) & (ad < ad.shift(self.lookback))] = 1, -1
        return signals
