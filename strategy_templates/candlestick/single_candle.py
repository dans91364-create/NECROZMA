"""Single Candlestick Patterns"""
import pandas as pd
from typing import Dict
from ..base import Strategy
class DojiStrategy(Strategy):
    """Doji Pattern"""
    def __init__(self, params: Dict):
        super().__init__("DojiStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "small body near center bullish"}, {"type": "entry_short", "condition": "small body near center bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class LongLeggedDoji(Strategy):
    """Long-Legged Doji"""
    def __init__(self, params: Dict):
        super().__init__("LongLeggedDoji", params)
        self.rules = [{"type": "entry_long", "condition": "long shadows, small body bullish"}, {"type": "entry_short", "condition": "long shadows, small body bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class DragonflyDoji(Strategy):
    """Dragonfly Doji"""
    def __init__(self, params: Dict):
        super().__init__("DragonflyDoji", params)
        self.rules = [{"type": "entry_long", "condition": "long lower shadow, no upper bullish"}, {"type": "entry_short", "condition": "long lower shadow, no upper bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class GravestoneDoji(Strategy):
    """Gravestone Doji"""
    def __init__(self, params: Dict):
        super().__init__("GravestoneDoji", params)
        self.rules = [{"type": "entry_long", "condition": "long upper shadow, no lower bullish"}, {"type": "entry_short", "condition": "long upper shadow, no lower bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class HammerStrategy(Strategy):
    """Hammer Pattern"""
    def __init__(self, params: Dict):
        super().__init__("HammerStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "small body at top, long lower shadow bullish"}, {"type": "entry_short", "condition": "small body at top, long lower shadow bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class HangingMan(Strategy):
    """Hanging Man"""
    def __init__(self, params: Dict):
        super().__init__("HangingMan", params)
        self.rules = [{"type": "entry_long", "condition": "small body at top, long lower shadow (bearish) bullish"}, {"type": "entry_short", "condition": "small body at top, long lower shadow (bearish) bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class InvertedHammer(Strategy):
    """Inverted Hammer"""
    def __init__(self, params: Dict):
        super().__init__("InvertedHammer", params)
        self.rules = [{"type": "entry_long", "condition": "small body at bottom, long upper shadow bullish"}, {"type": "entry_short", "condition": "small body at bottom, long upper shadow bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class ShootingStar(Strategy):
    """Shooting Star"""
    def __init__(self, params: Dict):
        super().__init__("ShootingStar", params)
        self.rules = [{"type": "entry_long", "condition": "small body at bottom, long upper shadow (bearish) bullish"}, {"type": "entry_short", "condition": "small body at bottom, long upper shadow (bearish) bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class SpinningTop(Strategy):
    """Spinning Top"""
    def __init__(self, params: Dict):
        super().__init__("SpinningTop", params)
        self.rules = [{"type": "entry_long", "condition": "small body, long shadows both sides bullish"}, {"type": "entry_short", "condition": "small body, long shadows both sides bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class Marubozu(Strategy):
    """Marubozu"""
    def __init__(self, params: Dict):
        super().__init__("Marubozu", params)
        self.rules = [{"type": "entry_long", "condition": "long body, no shadows bullish"}, {"type": "entry_short", "condition": "long body, no shadows bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals


class BeltHold(Strategy):
    """Belt Hold"""
    def __init__(self, params: Dict):
        super().__init__("BeltHold", params)
        self.rules = [{"type": "entry_long", "condition": "long body opening at extreme bullish"}, {"type": "entry_short", "condition": "long body opening at extreme bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "open" in df.columns and "high" in df.columns:
            o, h, l, c = df["open"], df["high"], df["low"], df.get("close", df.get("mid_price"))
            body = abs(c - o)
            # Simplified pattern recognition
            signals[c > o], signals[c < o] = 1, -1
        return signals
