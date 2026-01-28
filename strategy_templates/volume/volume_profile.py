"""Volume Profile Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class VolumePriceTrend(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolumePriceTrend", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "VPT rising"}, {"type": "entry_short", "condition": "VPT falling"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            vpt = (df["volume"] * price.pct_change()).cumsum()
            vpt_sma = vpt.rolling(self.period).mean()
            signals[(vpt > vpt_sma) & (vpt.shift(1) <= vpt_sma.shift(1))], signals[(vpt < vpt_sma) & (vpt.shift(1) >= vpt_sma.shift(1))] = 1, -1
        return signals
class NegativeVolIndex(Strategy):
    def __init__(self, params: Dict):
        super().__init__("NegativeVolIndex", params)
        self.period = params.get("period", 255)
        self.rules = [{"type": "entry_long", "condition": "NVI crosses above EMA"}, {"type": "entry_short", "condition": "NVI crosses below EMA"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            nvi = pd.Series(1000, index=df.index)
            for i in range(1, len(df)):
                if df["volume"].iloc[i] < df["volume"].iloc[i-1]:
                    nvi.iloc[i] = nvi.iloc[i-1] + (price.iloc[i] - price.iloc[i-1]) / price.iloc[i-1] * nvi.iloc[i-1]
                else:
                    nvi.iloc[i] = nvi.iloc[i-1]
            nvi_ema = nvi.ewm(span=self.period).mean()
            signals[(nvi > nvi_ema) & (nvi.shift(1) <= nvi_ema.shift(1))], signals[(nvi < nvi_ema) & (nvi.shift(1) >= nvi_ema.shift(1))] = 1, -1
        return signals
class PositiveVolIndex(Strategy):
    def __init__(self, params: Dict):
        super().__init__("PositiveVolIndex", params)
        self.period = params.get("period", 255)
        self.rules = [{"type": "entry_long", "condition": "PVI crosses above EMA"}, {"type": "entry_short", "condition": "PVI crosses below EMA"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            pvi = pd.Series(1000, index=df.index)
            for i in range(1, len(df)):
                if df["volume"].iloc[i] > df["volume"].iloc[i-1]:
                    pvi.iloc[i] = pvi.iloc[i-1] + (price.iloc[i] - price.iloc[i-1]) / price.iloc[i-1] * pvi.iloc[i-1]
                else:
                    pvi.iloc[i] = pvi.iloc[i-1]
            pvi_ema = pvi.ewm(span=self.period).mean()
            signals[(pvi > pvi_ema) & (pvi.shift(1) <= pvi_ema.shift(1))], signals[(pvi < pvi_ema) & (pvi.shift(1) >= pvi_ema.shift(1))] = 1, -1
        return signals
class VolumeOscillator(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolumeOscillator", params)
        self.fast, self.slow = params.get("fast", 5), params.get("slow", 10)
        self.rules = [{"type": "entry_long", "condition": "VO > 0"}, {"type": "entry_short", "condition": "VO < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "volume" in df.columns:
            vo = df["volume"].rolling(self.fast).mean() - df["volume"].rolling(self.slow).mean()
            signals[(vo > 0) & (vo.shift(1) <= 0)], signals[(vo < 0) & (vo.shift(1) >= 0)] = 1, -1
        return signals
class VolumeROC(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolumeROC", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "volume ROC increasing"}, {"type": "entry_short", "condition": "volume ROC decreasing"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "volume" in df.columns:
            vroc = 100 * df["volume"].pct_change(self.period)
            signals[vroc > 0], signals[vroc < 0] = 1, -1
        return signals
class DemandIndex(Strategy):
    def __init__(self, params: Dict):
        super().__init__("DemandIndex", params)
        self.rules = [{"type": "entry_long", "condition": "demand index positive"}, {"type": "entry_short", "condition": "demand index negative"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            price = df.get("close", df.get("mid_price"))
            bp = price - df["low"]
            sp = df["high"] - price
            di = bp / (sp + EPSILON) * df["volume"]
            signals[(di > di.shift(1))], signals[(di < di.shift(1))] = 1, -1
        return signals
class MarketFacilitation(Strategy):
    def __init__(self, params: Dict):
        super().__init__("MarketFacilitation", params)
        self.rules = [{"type": "entry_long", "condition": "BW and volume both increase"}, {"type": "entry_short", "condition": "BW and volume both decrease"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            bw = (df["high"] - df["low"]) / (df["volume"] + EPSILON)
            signals[(bw > bw.shift(1)) & (df["volume"] > df["volume"].shift(1))], signals[(bw < bw.shift(1)) & (df["volume"] < df["volume"].shift(1))] = 1, -1
        return signals
class VolumeSpike(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VolumeSpike", params)
        self.period, self.mult = params.get("period", 20), params.get("multiplier", 2.0)
        self.rules = [{"type": "entry_long", "condition": "volume spike with price up"}, {"type": "entry_short", "condition": "volume spike with price down"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            avg_vol = df["volume"].rolling(self.period).mean()
            spike = df["volume"] > avg_vol * self.mult
            signals[spike & (price > price.shift(1))], signals[spike & (price < price.shift(1))] = 1, -1
        return signals
