"""Volatility Breakout Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class StdDevBreakout(Strategy):
    def __init__(self, params: Dict):
        super().__init__("StdDevBreakout", params)
        self.period, self.threshold = params.get("period", 20), params.get("threshold", 2.0)
        self.rules = [{"type": "entry_long", "condition": "move > threshold * std dev"}, {"type": "entry_short", "condition": "move < -threshold * std dev"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        std = price.rolling(self.period).std()
        move = price.diff()
        signals[move > self.threshold * std], signals[move < -self.threshold * std] = 1, -1
        return signals
class HistoricalVolBreak(Strategy):
    def __init__(self, params: Dict):
        super().__init__("HistoricalVolBreak", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "vol breakout upward"}, {"type": "entry_short", "condition": "vol breakout downward"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        hvol = price.pct_change().rolling(self.period).std()
        signals[hvol > hvol.rolling(self.period).mean() * 1.5], signals[hvol < hvol.rolling(self.period).mean() * 0.7] = 1, -1
        return signals
class ChaikinVolatility(Strategy):
    def __init__(self, params: Dict):
        super().__init__("ChaikinVolatility", params)
        self.period, self.roc_period = params.get("period", 10), params.get("roc_period", 10)
        self.rules = [{"type": "entry_long", "condition": "volatility increasing"}, {"type": "entry_short", "condition": "volatility decreasing"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            hl_ema = (df["high"] - df["low"]).ewm(span=self.period).mean()
            cv = 100 * hl_ema.pct_change(self.roc_period)
            signals[cv > 0], signals[cv < 0] = 1, -1
        return signals
class UlcerIndex(Strategy):
    def __init__(self, params: Dict):
        super().__init__("UlcerIndex", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "ulcer index low"}, {"type": "entry_short", "condition": "ulcer index high"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        dd = 100 * (price - price.rolling(self.period).max()) / (price.rolling(self.period).max() + EPSILON)
        ui = (dd ** 2).rolling(self.period).mean() ** 0.5
        signals[ui < ui.rolling(self.period).mean() * 0.8], signals[ui > ui.rolling(self.period).mean() * 1.2] = 1, -1
        return signals
class VolatilityRatio(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolatilityRatio", params)
        self.short_period, self.long_period = params.get("short_period", 5), params.get("long_period", 20)
        self.rules = [{"type": "entry_long", "condition": "vol ratio increasing"}, {"type": "entry_short", "condition": "vol ratio decreasing"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        short_vol, long_vol = price.pct_change().rolling(self.short_period).std(), price.pct_change().rolling(self.long_period).std()
        vr = short_vol / (long_vol + EPSILON)
        signals[vr > 1.2], signals[vr < 0.8] = 1, -1
        return signals
class NATRStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("NATRStrategy", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "NATR expansion"}, {"type": "entry_short", "condition": "NATR contraction"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            price = df.get("close", df.get("mid_price"))
            tr = pd.concat([df["high"] - df["low"], abs(df["high"] - price.shift(1)), abs(df["low"] - price.shift(1))], axis=1).max(axis=1)
            natr = 100 * tr.rolling(self.period).mean() / (price + EPSILON)
            signals[natr > natr.rolling(self.period).mean()], signals[natr < natr.rolling(self.period).mean()] = 1, -1
        return signals
class RangeExpansion(Strategy):
    def __init__(self, params: Dict):
        super().__init__("RangeExpansion", params)
        self.period = params.get("period", 7)
        self.rules = [{"type": "entry_long", "condition": "range expands upward"}, {"type": "entry_short", "condition": "range expands downward"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            range_val, avg_range = df["high"] - df["low"], (df["high"] - df["low"]).rolling(self.period).mean()
            expansion = range_val > avg_range * 1.5
            price = df.get("close", df.get("mid_price"))
            signals[expansion & (price > price.shift(1))], signals[expansion & (price < price.shift(1))] = 1, -1
        return signals
class VolatilityContraction(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolatilityContraction", params)
        self.period = params.get("period", 10)
        self.rules = [{"type": "entry_long", "condition": "contraction then upside break"}, {"type": "entry_short", "condition": "contraction then downside break"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        vol, avg_vol = price.pct_change().rolling(self.period).std(), price.pct_change().rolling(self.period * 2).std().rolling(self.period).mean()
        contraction = vol < avg_vol * 0.5
        signals[contraction.shift(1) & (price > price.shift(1))], signals[contraction.shift(1) & (price < price.shift(1))] = 1, -1
        return signals
