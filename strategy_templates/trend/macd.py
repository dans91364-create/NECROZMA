"""MACD Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class MACDClassic(Strategy):
    """
    Classic MACD Strategy
    
    Logic: Buy when MACD crosses above signal line, sell when crosses below
    Best for: Trending markets with momentum
    """
    
    def __init__(self, params: Dict):
        super().__init__("MACDClassic", params)
        self.fast_period = params.get("fast_period", 12)
        self.slow_period = params.get("slow_period", 26)
        self.signal_period = params.get("signal_period", 9)
        
        self.rules = [
            {"type": "entry_long", "condition": "MACD crosses above signal line"},
            {"type": "entry_short", "condition": "MACD crosses below signal line"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        fast_ema = price.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = price.ewm(span=self.slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        
        signals[(macd > signal) & (macd.shift(1) <= signal.shift(1))] = 1
        signals[(macd < signal) & (macd.shift(1) >= signal.shift(1))] = -1
        
        return signals


class MACDHistogram(Strategy):
    """
    MACD Histogram Strategy
    
    Logic: Buy when histogram turns positive, sell when turns negative
    Best for: Early trend detection
    """
    
    def __init__(self, params: Dict):
        super().__init__("MACDHistogram", params)
        self.fast_period = params.get("fast_period", 12)
        self.slow_period = params.get("slow_period", 26)
        self.signal_period = params.get("signal_period", 9)
        
        self.rules = [
            {"type": "entry_long", "condition": "histogram crosses above zero"},
            {"type": "entry_short", "condition": "histogram crosses below zero"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        fast_ema = price.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = price.ewm(span=self.slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd - signal
        
        signals[(histogram > 0) & (histogram.shift(1) <= 0)] = 1
        signals[(histogram < 0) & (histogram.shift(1) >= 0)] = -1
        
        return signals


class MACDDivergence(Strategy):
    """
    MACD Divergence Strategy
    
    Logic: Buy on bullish divergence, sell on bearish divergence
    Best for: Reversal detection in trending markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("MACDDivergence", params)
        self.fast_period = params.get("fast_period", 12)
        self.slow_period = params.get("slow_period", 26)
        self.signal_period = params.get("signal_period", 9)
        self.lookback = params.get("lookback", 5)
        
        self.rules = [
            {"type": "entry_long", "condition": "bullish divergence (price lower low, MACD higher low)"},
            {"type": "entry_short", "condition": "bearish divergence (price higher high, MACD lower high)"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        fast_ema = price.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = price.ewm(span=self.slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        
        price_low = price.rolling(self.lookback).min()
        price_high = price.rolling(self.lookback).max()
        macd_low = macd.rolling(self.lookback).min()
        macd_high = macd.rolling(self.lookback).max()
        
        # Bullish divergence: price making lower lows, MACD making higher lows
        bullish_div = (price == price_low) & (macd > macd.shift(self.lookback))
        # Bearish divergence: price making higher highs, MACD making lower highs
        bearish_div = (price == price_high) & (macd < macd.shift(self.lookback))
        
        signals[bullish_div] = 1
        signals[bearish_div] = -1
        
        return signals
