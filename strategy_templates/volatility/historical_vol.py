"""Historical Volatility Estimators"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON
class GarmanKlass(Strategy):
    def __init__(self, params: Dict):
        super().__init__("GarmanKlass", params)
        self.period, self.threshold = params.get("period", 20), params.get("threshold", 0.02)
        self.rules = [{"type": "entry_long", "condition": "GK vol spike"}, {"type": "entry_short", "condition": "GK vol low"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "open" in df.columns:
            hl = np.log(df["high"] / df["low"])
            co = np.log(df.get("close", df.get("mid_price")) / df["open"])
            gk_vol = np.sqrt((0.5 * hl ** 2 - (2 * np.log(2) - 1) * co ** 2).rolling(self.period).mean())
            signals[gk_vol > gk_vol.rolling(self.period).mean() * 1.5], signals[gk_vol < gk_vol.rolling(self.period).mean() * 0.7] = 1, -1
        return signals
class ParkinsonVol(Strategy):
    def __init__(self, params: Dict):
        super().__init__("ParkinsonVol", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "Parkinson vol spike"}, {"type": "entry_short", "condition": "vol compression"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            hl = np.log(df["high"] / (df["low"] + EPSILON))
            park_vol = np.sqrt((hl ** 2 / (4 * np.log(2))).rolling(self.period).mean())
            signals[park_vol > park_vol.rolling(self.period).mean() * 1.5], signals[park_vol < park_vol.rolling(self.period).mean() * 0.7] = 1, -1
        return signals
class YangZhangVol(Strategy):
    def __init__(self, params: Dict):
        super().__init__("YangZhangVol", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "YZ vol expansion"}, {"type": "entry_short", "condition": "vol contraction"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            co = np.log(df.get("close", df.get("mid_price")) / df["open"])
            yz_vol = co.rolling(self.period).std()
            signals[yz_vol > yz_vol.rolling(self.period).mean()], signals[yz_vol < yz_vol.rolling(self.period).mean() * 0.8] = 1, -1
        return signals
