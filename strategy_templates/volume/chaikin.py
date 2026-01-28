"""Chaikin Money Flow Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class ChaikinMoneyFlow(Strategy):
    def __init__(self, params: Dict):
        super().__init__("ChaikinMoneyFlow", params)
        self.period, self.threshold = params.get("period", 20), params.get("threshold", 0)
        self.rules = [{"type": "entry_long", "condition": "CMF > 0"}, {"type": "entry_short", "condition": "CMF < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            close = df.get("close", df.get("mid_price"))
            clv = ((close - df["low"]) - (df["high"] - close)) / (df["high"] - df["low"] + EPSILON)
            cmf = (clv * df["volume"]).rolling(self.period).sum() / (df["volume"].rolling(self.period).sum() + EPSILON)
            signals[(cmf > self.threshold) & (cmf.shift(1) <= self.threshold)], signals[(cmf < -self.threshold) & (cmf.shift(1) >= -self.threshold)] = 1, -1
        return signals
class CMFDivergence(Strategy):
    def __init__(self, params: Dict):
        super().__init__("CMFDivergence", params)
        self.period, self.lookback = params.get("period", 20), params.get("lookback", 5)
        self.rules = [{"type": "entry_long", "condition": "bullish CMF divergence"}, {"type": "entry_short", "condition": "bearish CMF divergence"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            price, close = df.get("mid_price", df.get("close", df.get("Close"))), df.get("close", df.get("mid_price"))
            clv = ((close - df["low"]) - (df["high"] - close)) / (df["high"] - df["low"] + EPSILON)
            cmf = (clv * df["volume"]).rolling(self.period).sum() / (df["volume"].rolling(self.period).sum() + EPSILON)
            price_low = price.rolling(self.lookback).min()
            signals[(price == price_low) & (cmf > cmf.shift(self.lookback))], signals[(price == price.rolling(self.lookback).max()) & (cmf < cmf.shift(self.lookback))] = 1, -1
        return signals
