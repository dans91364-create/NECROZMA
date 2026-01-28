"""Miscellaneous Oscillators"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class CMOStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("CMOStrategy", params)
        self.period, self.oversold, self.overbought = params.get("period", 14), params.get("oversold", -50), params.get("overbought", 50)
        self.rules = [{"type": "entry_long", "condition": "CMO < -50"}, {"type": "entry_short", "condition": "CMO > 50"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        delta, up, down = price.diff(), price.diff().where(lambda x: x > 0, 0), -price.diff().where(lambda x: x < 0, 0)
        cmo = 100 * (up.rolling(self.period).sum() - down.rolling(self.period).sum()) / (up.rolling(self.period).sum() + down.rolling(self.period).sum() + EPSILON)
        signals[cmo < self.oversold], signals[cmo > self.overbought] = 1, -1
        return signals

class RVIStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("RVIStrategy", params)
        self.period = params.get("period", 10)
        self.rules = [{"type": "entry_long", "condition": "RVI crosses above signal"}, {"type": "entry_short", "condition": "RVI crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            close, open_p = df.get("close", df.get("mid_price")), df["open"]
            numerator, denominator = (close - open_p).rolling(self.period).mean(), (df["high"] - df["low"]).rolling(self.period).mean()
            rvi, signal = numerator / (denominator + EPSILON), numerator.rolling(4).mean() / (denominator.rolling(4).mean() + EPSILON)
            signals[(rvi > signal) & (rvi.shift(1) <= signal.shift(1))], signals[(rvi < signal) & (rvi.shift(1) >= signal.shift(1))] = 1, -1
        return signals

class IntradayMomentum(Strategy):
    def __init__(self, params: Dict):
        super().__init__("IntradayMomentum", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "IMI < 30"}, {"type": "entry_short", "condition": "IMI > 70"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns:
            close, open_p = df.get("close", df.get("mid_price")), df["open"]
            gains, losses = (close - open_p).where(lambda x: x > 0, 0), -(close - open_p).where(lambda x: x < 0, 0)
            imi = 100 * gains.rolling(self.period).sum() / (gains.rolling(self.period).sum() + losses.rolling(self.period).sum() + EPSILON)
            signals[imi < 30], signals[imi > 70] = 1, -1
        return signals

class MFIStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("MFIStrategy", params)
        self.period, self.oversold, self.overbought = params.get("period", 14), params.get("oversold", 20), params.get("overbought", 80)
        self.rules = [{"type": "entry_long", "condition": "MFI < 20"}, {"type": "entry_short", "condition": "MFI > 80"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            tp = (df["high"] + df["low"] + df.get("close", df.get("mid_price"))) / 3
            mf, pmf, nmf = tp * df["volume"], (mf.where(tp > tp.shift(1), 0)).rolling(self.period).sum(), (mf.where(tp < tp.shift(1), 0)).rolling(self.period).sum()
            mfi = 100 - 100 / (1 + pmf / (nmf + EPSILON))
            signals[mfi < self.oversold], signals[mfi > self.overbought] = 1, -1
        return signals

class ForceIndexOsc(Strategy):
    def __init__(self, params: Dict):
        super().__init__("ForceIndexOsc", params)
        self.period = params.get("period", 13)
        self.rules = [{"type": "entry_long", "condition": "Force Index > 0"}, {"type": "entry_short", "condition": "Force Index < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        volume, fi = df.get("volume", pd.Series(1, index=df.index)), (price.diff() * volume).ewm(span=self.period).mean()
        signals[(fi > 0) & (fi.shift(1) <= 0)], signals[(fi < 0) & (fi.shift(1) >= 0)] = 1, -1
        return signals

class TSIStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("TSIStrategy", params)
        self.long_period, self.short_period, self.signal = params.get("long_period", 25), params.get("short_period", 13), params.get("signal_period", 7)
        self.rules = [{"type": "entry_long", "condition": "TSI crosses above signal"}, {"type": "entry_short", "condition": "TSI crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price, momentum = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close"))), price.diff()
        double_smoothed_pc = momentum.ewm(span=self.long_period).mean().ewm(span=self.short_period).mean()
        double_smoothed_apc = momentum.abs().ewm(span=self.long_period).mean().ewm(span=self.short_period).mean()
        tsi, sig = 100 * double_smoothed_pc / (double_smoothed_apc + EPSILON), (100 * double_smoothed_pc / (double_smoothed_apc + EPSILON)).ewm(span=self.signal).mean()
        signals[(tsi > sig) & (tsi.shift(1) <= sig.shift(1))], signals[(tsi < sig) & (tsi.shift(1) >= sig.shift(1))] = 1, -1
        return signals

class SMIStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("SMIStrategy", params)
        self.period, self.oversold, self.overbought = params.get("period", 13), -40, 40
        self.rules = [{"type": "entry_long", "condition": "SMI < -40"}, {"type": "entry_short", "condition": "SMI > 40"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            high, low, close = df["high"], df["low"], df.get("close", df.get("mid_price"))
            ll, hh = low.rolling(self.period).min(), high.rolling(self.period).max()
            diff, rdiff = close - (hh + ll) / 2, hh - ll
            smi = 100 * diff.ewm(span=3).mean().ewm(span=3).mean() / (rdiff.ewm(span=3).mean().ewm(span=3).mean() / 2 + EPSILON)
            signals[smi < -40], signals[smi > 40] = 1, -1
        return signals

class PPOStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("PPOStrategy", params)
        self.fast, self.slow, self.signal = params.get("fast", 12), params.get("slow", 26), params.get("signal", 9)
        self.rules = [{"type": "entry_long", "condition": "PPO crosses above signal"}, {"type": "entry_short", "condition": "PPO crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        ema_fast, ema_slow = price.ewm(span=self.fast).mean(), price.ewm(span=self.slow).mean()
        ppo, sig = 100 * (ema_fast - ema_slow) / (ema_slow + EPSILON), (100 * (ema_fast - ema_slow) / (ema_slow + EPSILON)).ewm(span=self.signal).mean()
        signals[(ppo > sig) & (ppo.shift(1) <= sig.shift(1))], signals[(ppo < sig) & (ppo.shift(1) >= sig.shift(1))] = 1, -1
        return signals

class AwesomeOscillator(Strategy):
    def __init__(self, params: Dict):
        super().__init__("AwesomeOscillator", params)
        self.fast, self.slow = params.get("fast", 5), params.get("slow", 34)
        self.rules = [{"type": "entry_long", "condition": "AO crosses above zero"}, {"type": "entry_short", "condition": "AO crosses below zero"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            median = (df["high"] + df["low"]) / 2
            ao = median.rolling(self.fast).mean() - median.rolling(self.slow).mean()
            signals[(ao > 0) & (ao.shift(1) <= 0)], signals[(ao < 0) & (ao.shift(1) >= 0)] = 1, -1
        return signals

class AcceleratorOsc(Strategy):
    def __init__(self, params: Dict):
        super().__init__("AcceleratorOsc", params)
        self.fast, self.slow = params.get("fast", 5), params.get("slow", 34)
        self.rules = [{"type": "entry_long", "condition": "AC turns green"}, {"type": "entry_short", "condition": "AC turns red"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            median = (df["high"] + df["low"]) / 2
            ao = median.rolling(self.fast).mean() - median.rolling(self.slow).mean()
            ac = ao - ao.rolling(5).mean()
            signals[(ac > ac.shift(1)) & (ac.shift(1) <= ac.shift(2))], signals[(ac < ac.shift(1)) & (ac.shift(1) >= ac.shift(2))] = 1, -1
        return signals

class ChaikinOscillator(Strategy):
    def __init__(self, params: Dict):
        super().__init__("ChaikinOscillator", params)
        self.fast, self.slow = params.get("fast", 3), params.get("slow", 10)
        self.rules = [{"type": "entry_long", "condition": "Chaikin crosses above zero"}, {"type": "entry_short", "condition": "Chaikin crosses below zero"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            clv = ((df.get("close", df.get("mid_price")) - df["low"]) - (df["high"] - df.get("close", df.get("mid_price")))) / (df["high"] - df["low"] + EPSILON)
            ad = (clv * df["volume"]).cumsum()
            co = ad.ewm(span=self.fast).mean() - ad.ewm(span=self.slow).mean()
            signals[(co > 0) & (co.shift(1) <= 0)], signals[(co < 0) & (co.shift(1) >= 0)] = 1, -1
        return signals

class FisherTransform(Strategy):
    def __init__(self, params: Dict):
        super().__init__("FisherTransform", params)
        self.period = params.get("period", 10)
        self.rules = [{"type": "entry_long", "condition": "Fisher crosses above signal"}, {"type": "entry_short", "condition": "Fisher crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            median = (df["high"] + df["low"]) / 2
            ll, hh = median.rolling(self.period).min(), median.rolling(self.period).max()
            value = 0.5 * 2 * ((median - ll) / (hh - ll + EPSILON) - 0.5).clip(-0.999, 0.999)
            fisher = pd.Series(index=df.index, dtype=float)
            fisher.iloc[0] = 0
            for i in range(1, len(df)): fisher.iloc[i] = 0.5 * fisher.iloc[i-1] + 0.5 * ((1 + value.iloc[i]) / (1 - value.iloc[i] + EPSILON)).apply(lambda x: 0.5 * pd.np.log(x) if x > 0 else 0)
            signals[(fisher > fisher.shift(1)) & (fisher.shift(1) <= fisher.shift(2))], signals[(fisher < fisher.shift(1)) & (fisher.shift(1) >= fisher.shift(2))] = 1, -1
        return signals
