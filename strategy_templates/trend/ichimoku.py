"""Ichimoku Cloud Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy


class IchimokuCloud(Strategy):
    """
    Ichimoku Cloud Strategy
    
    Logic: Buy when price above cloud and tenkan crosses kijun, sell when price below cloud
    Best for: Trending markets with momentum confirmation
    """
    
    def __init__(self, params: Dict):
        super().__init__("IchimokuCloud", params)
        self.tenkan_period = params.get("tenkan_period", 9)
        self.kijun_period = params.get("kijun_period", 26)
        self.senkou_b_period = params.get("senkou_b_period", 52)
        
        self.rules = [
            {"type": "entry_long", "condition": "price > cloud and tenkan > kijun"},
            {"type": "entry_short", "condition": "price < cloud and tenkan < kijun"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            
            # Tenkan-sen
            tenkan = (high.rolling(self.tenkan_period).max() + low.rolling(self.tenkan_period).min()) / 2
            
            # Kijun-sen
            kijun = (high.rolling(self.kijun_period).max() + low.rolling(self.kijun_period).min()) / 2
            
            # Senkou Span A
            senkou_a = ((tenkan + kijun) / 2).shift(self.kijun_period)
            
            # Senkou Span B
            senkou_b = ((high.rolling(self.senkou_b_period).max() + 
                        low.rolling(self.senkou_b_period).min()) / 2).shift(self.kijun_period)
            
            # Cloud
            cloud_top = pd.concat([senkou_a, senkou_b], axis=1).max(axis=1)
            cloud_bottom = pd.concat([senkou_a, senkou_b], axis=1).min(axis=1)
            
            signals[(close > cloud_top) & (tenkan > kijun)] = 1
            signals[(close < cloud_bottom) & (tenkan < kijun)] = -1
        
        return signals


class IchimokuTKCross(Strategy):
    """
    Ichimoku Tenkan-Kijun Cross
    
    Logic: Buy when tenkan crosses above kijun, sell when crosses below
    Best for: Trend changes
    """
    
    def __init__(self, params: Dict):
        super().__init__("IchimokuTKCross", params)
        self.tenkan_period = params.get("tenkan_period", 9)
        self.kijun_period = params.get("kijun_period", 26)
        
        self.rules = [
            {"type": "entry_long", "condition": "tenkan crosses above kijun"},
            {"type": "entry_short", "condition": "tenkan crosses below kijun"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            
            tenkan = (high.rolling(self.tenkan_period).max() + low.rolling(self.tenkan_period).min()) / 2
            kijun = (high.rolling(self.kijun_period).max() + low.rolling(self.kijun_period).min()) / 2
            
            signals[(tenkan > kijun) & (tenkan.shift(1) <= kijun.shift(1))] = 1
            signals[(tenkan < kijun) & (tenkan.shift(1) >= kijun.shift(1))] = -1
        
        return signals
