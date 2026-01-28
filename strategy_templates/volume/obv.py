"""On-Balance Volume Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy
class OBVStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("OBVStrategy", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "OBV > SMA"}, {"type": "entry_short", "condition": "OBV < SMA"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            obv = (df["volume"] * ((price > price.shift(1)).astype(int) - (price < price.shift(1)).astype(int))).cumsum()
            obv_sma = obv.rolling(self.period).mean()
            signals[(obv > obv_sma) & (obv.shift(1) <= obv_sma.shift(1))], signals[(obv < obv_sma) & (obv.shift(1) >= obv_sma.shift(1))] = 1, -1
        return signals
class OBVDivergence(Strategy):
    def __init__(self, params: Dict):
        super().__init__("OBVDivergence", params)
        self.lookback = params.get("lookback", 5)
        self.rules = [{"type": "entry_long", "condition": "bullish OBV divergence"}, {"type": "entry_short", "condition": "bearish OBV divergence"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            obv = (df["volume"] * ((price > price.shift(1)).astype(int) - (price < price.shift(1)).astype(int))).cumsum()
            price_low = price.rolling(self.lookback).min()
            signals[(price == price_low) & (obv > obv.shift(self.lookback))], signals[(price == price.rolling(self.lookback).max()) & (obv < obv.shift(self.lookback))] = 1, -1
        return signals
