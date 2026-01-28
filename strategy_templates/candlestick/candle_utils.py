"""Candlestick Pattern Utilities"""
import pandas as pd

def is_doji(open_price, close, threshold=0.1):
    """Check if candle is a doji"""
    return abs(close - open_price) / (abs(close) + 1e-10) < threshold

def is_engulfing(o1, c1, o2, c2):
    """Check if second candle engulfs first"""
    return (c2 > o2 and c2 > o1 and o2 < c1) or (c2 < o2 and c2 < o1 and o2 > c1)
