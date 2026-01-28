"""Squeeze and Additional Momentum Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class PsychologicalLine(Strategy):
    """Psychological Line Indicator"""
    def __init__(self, params: Dict):
        super().__init__("PsychologicalLine", params)
        self.period = params.get("period", 12)
        self.rules = [{"type": "entry_long", "condition": "PL < 25"}, {"type": "entry_short", "condition": "PL > 75"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        up_days = (price > price.shift(1)).astype(int)
        pl = 100 * up_days.rolling(self.period).sum() / self.period
        signals[pl < 25], signals[pl > 75] = 1, -1
        return signals

class BalanceOfPower(Strategy):
    """Balance of Power"""
    def __init__(self, params: Dict):
        super().__init__("BalanceOfPower", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "BOP > 0"}, {"type": "entry_short", "condition": "BOP < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            close, open_p, high, low = df.get("close", df.get("mid_price")), df["open"], df["high"], df["low"]
            bop = (close - open_p) / (high - low + EPSILON)
            bop_sma = bop.rolling(self.period).mean()
            signals[(bop_sma > 0) & (bop_sma.shift(1) <= 0)], signals[(bop_sma < 0) & (bop_sma.shift(1) >= 0)] = 1, -1
        return signals

class SqueezeMomentum(Strategy):
    """Squeeze Momentum Indicator"""
    def __init__(self, params: Dict):
        super().__init__("SqueezeMomentum", params)
        self.bb_period, self.kc_period, self.mom_period = params.get("bb_period", 20), params.get("kc_period", 20), params.get("mom_period", 12)
        self.rules = [{"type": "entry_long", "condition": "squeeze fired and momentum positive"}, {"type": "entry_short", "condition": "squeeze fired and momentum negative"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        bb_std = price.rolling(self.bb_period).std()
        if "high" in df.columns:
            tr = (df["high"] - df["low"]).rolling(self.kc_period).mean()
            squeeze_on = bb_std < tr
            signals[squeeze_on & (price > price.rolling(self.mom_period).mean())], signals[squeeze_on & (price < price.rolling(self.mom_period).mean())] = 1, -1
        return signals

class AbsoluteStrength(Strategy):
    """Absolute Strength Histogram"""
    def __init__(self, params: Dict):
        super().__init__("AbsoluteStrength", params)
        self.period = params.get("period", 9)
        self.rules = [{"type": "entry_long", "condition": "ASH > 0"}, {"type": "entry_short", "condition": "ASH < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        delta = price.diff()
        gains, losses = delta.where(delta > 0, 0), -delta.where(delta < 0, 0)
        avg_gain, avg_loss = gains.ewm(span=self.period).mean(), losses.ewm(span=self.period).mean()
        ash = avg_gain - avg_loss
        signals[(ash > 0) & (ash.shift(1) <= 0)], signals[(ash < 0) & (ash.shift(1) >= 0)] = 1, -1
        return signals

class DoubleSmoothedStoch(Strategy):
    """Double Smoothed Stochastic"""
    def __init__(self, params: Dict):
        super().__init__("DoubleSmoothedStoch", params)
        self.period = params.get("period", 10)
        self.rules = [{"type": "entry_long", "condition": "DSS < 20"}, {"type": "entry_short", "condition": "DSS > 80"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            price, high, low = df.get("close", df.get("mid_price")), df["high"], df["low"]
            ll, hh = low.rolling(self.period).min(), high.rolling(self.period).max()
            k = 100 * (price - ll) / (hh - ll + EPSILON)
            dss = k.ewm(span=3).mean().ewm(span=3).mean()
            signals[dss < 20], signals[dss > 80] = 1, -1
        return signals

class MomentumDivergence(Strategy):
    """Momentum Divergence Strategy"""
    def __init__(self, params: Dict):
        super().__init__("MomentumDivergence", params)
        self.period, self.lookback = params.get("period", 10), params.get("lookback", 5)
        self.rules = [{"type": "entry_long", "condition": "bullish momentum divergence"}, {"type": "entry_short", "condition": "bearish momentum divergence"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        mom = price.diff(self.period)
        price_low, mom_low = price.rolling(self.lookback).min(), mom.rolling(self.lookback).min()
        signals[(price == price_low) & (mom > mom.shift(self.lookback))], signals[(price == price.rolling(self.lookback).max()) & (mom < mom.shift(self.lookback))] = 1, -1
        return signals
