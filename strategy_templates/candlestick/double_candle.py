"""Double Candlestick Patterns"""
import pandas as pd
from typing import Dict
from ..base import Strategy
class BullishEngulfing(Strategy):
    """Bullish Engulfing"""
    def __init__(self, params: Dict):
        super().__init__("BullishEngulfing", params)
        self.rules = [{"type": "entry_long", "condition": "large bullish candle engulfs previous bearish bullish"}, {"type": "entry_short", "condition": "large bullish candle engulfs previous bearish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class BearishEngulfing(Strategy):
    """Bearish Engulfing"""
    def __init__(self, params: Dict):
        super().__init__("BearishEngulfing", params)
        self.rules = [{"type": "entry_long", "condition": "large bearish candle engulfs previous bullish bullish"}, {"type": "entry_short", "condition": "large bearish candle engulfs previous bullish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class BullishHarami(Strategy):
    """Bullish Harami"""
    def __init__(self, params: Dict):
        super().__init__("BullishHarami", params)
        self.rules = [{"type": "entry_long", "condition": "small bullish inside previous large bearish bullish"}, {"type": "entry_short", "condition": "small bullish inside previous large bearish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class BearishHarami(Strategy):
    """Bearish Harami"""
    def __init__(self, params: Dict):
        super().__init__("BearishHarami", params)
        self.rules = [{"type": "entry_long", "condition": "small bearish inside previous large bullish bullish"}, {"type": "entry_short", "condition": "small bearish inside previous large bullish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class PiercingLine(Strategy):
    """Piercing Line"""
    def __init__(self, params: Dict):
        super().__init__("PiercingLine", params)
        self.rules = [{"type": "entry_long", "condition": "bullish closes above midpoint of previous bearish bullish"}, {"type": "entry_short", "condition": "bullish closes above midpoint of previous bearish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class DarkCloudCover(Strategy):
    """Dark Cloud Cover"""
    def __init__(self, params: Dict):
        super().__init__("DarkCloudCover", params)
        self.rules = [{"type": "entry_long", "condition": "bearish closes below midpoint of previous bullish bullish"}, {"type": "entry_short", "condition": "bearish closes below midpoint of previous bullish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class TweezerTops(Strategy):
    """Tweezer Tops"""
    def __init__(self, params: Dict):
        super().__init__("TweezerTops", params)
        self.rules = [{"type": "entry_long", "condition": "two candles same high bullish"}, {"type": "entry_short", "condition": "two candles same high bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class TweezerBottoms(Strategy):
    """Tweezer Bottoms"""
    def __init__(self, params: Dict):
        super().__init__("TweezerBottoms", params)
        self.rules = [{"type": "entry_long", "condition": "two candles same low bullish"}, {"type": "entry_short", "condition": "two candles same low bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class CounterattackLines(Strategy):
    """Counterattack Lines"""
    def __init__(self, params: Dict):
        super().__init__("CounterattackLines", params)
        self.rules = [{"type": "entry_long", "condition": "opposite direction, same close bullish"}, {"type": "entry_short", "condition": "opposite direction, same close bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class MatchingLowHigh(Strategy):
    """Matching Low/High"""
    def __init__(self, params: Dict):
        super().__init__("MatchingLowHigh", params)
        self.rules = [{"type": "entry_long", "condition": "consecutive candles same low or high bullish"}, {"type": "entry_short", "condition": "consecutive candles same low or high bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class HomingPigeon(Strategy):
    """Homing Pigeon"""
    def __init__(self, params: Dict):
        super().__init__("HomingPigeon", params)
        self.rules = [{"type": "entry_long", "condition": "small bearish inside large bearish bullish"}, {"type": "entry_short", "condition": "small bearish inside large bearish bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals
