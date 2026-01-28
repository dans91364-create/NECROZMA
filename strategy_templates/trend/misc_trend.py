"""Miscellaneous Trend Indicators"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class TRIXStrategy(Strategy):
    """
    TRIX Oscillator Strategy
    
    Logic: Buy when TRIX crosses above signal, sell when crosses below
    Best for: Filtering out market noise
    """
    
    def __init__(self, params: Dict):
        super().__init__("TRIXStrategy", params)
        self.period = params.get("period", 15)
        self.signal_period = params.get("signal_period", 9)
        
        self.rules = [
            {"type": "entry_long", "condition": "TRIX crosses above signal line"},
            {"type": "entry_short", "condition": "TRIX crosses below signal line"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # Triple EMA
        ema1 = price.ewm(span=self.period, adjust=False).mean()
        ema2 = ema1.ewm(span=self.period, adjust=False).mean()
        ema3 = ema2.ewm(span=self.period, adjust=False).mean()
        
        # TRIX: 1-period percent change of triple EMA
        trix = 100 * ema3.pct_change()
        signal = trix.ewm(span=self.signal_period, adjust=False).mean()
        
        signals[(trix > signal) & (trix.shift(1) <= signal.shift(1))] = 1
        signals[(trix < signal) & (trix.shift(1) >= signal.shift(1))] = -1
        
        return signals


class KSTStrategy(Strategy):
    """
    Know Sure Thing (KST) Strategy
    
    Logic: Buy when KST crosses above signal, sell when crosses below
    Best for: Long-term trend identification
    """
    
    def __init__(self, params: Dict):
        super().__init__("KSTStrategy", params)
        self.signal_period = params.get("signal_period", 9)
        
        self.rules = [
            {"type": "entry_long", "condition": "KST crosses above signal line"},
            {"type": "entry_short", "condition": "KST crosses below signal line"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # ROC for different periods
        roc1 = price.pct_change(10) * 100
        roc2 = price.pct_change(15) * 100
        roc3 = price.pct_change(20) * 100
        roc4 = price.pct_change(30) * 100
        
        # Smooth ROCs
        rocma1 = roc1.rolling(10).mean()
        rocma2 = roc2.rolling(10).mean()
        rocma3 = roc3.rolling(10).mean()
        rocma4 = roc4.rolling(15).mean()
        
        # KST
        kst = rocma1 + 2 * rocma2 + 3 * rocma3 + 4 * rocma4
        signal = kst.rolling(self.signal_period).mean()
        
        signals[(kst > signal) & (kst.shift(1) <= signal.shift(1))] = 1
        signals[(kst < signal) & (kst.shift(1) >= signal.shift(1))] = -1
        
        return signals


class CoppockCurve(Strategy):
    """
    Coppock Curve Strategy
    
    Logic: Buy when Coppock turns positive, sell when turns negative
    Best for: Long-term trend changes
    """
    
    def __init__(self, params: Dict):
        super().__init__("CoppockCurve", params)
        self.short_roc = params.get("short_roc", 11)
        self.long_roc = params.get("long_roc", 14)
        self.wma_period = params.get("wma_period", 10)
        
        self.rules = [
            {"type": "entry_long", "condition": "Coppock curve crosses above zero"},
            {"type": "entry_short", "condition": "Coppock curve crosses below zero"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # Sum of ROCs
        roc_sum = price.pct_change(self.short_roc) + price.pct_change(self.long_roc)
        
        # WMA of ROC sum
        weights = np.arange(1, self.wma_period + 1)
        coppock = roc_sum.rolling(self.wma_period).apply(
            lambda x: np.dot(x, weights) / weights.sum() if len(x) == self.wma_period else np.nan,
            raw=True
        )
        
        signals[(coppock > 0) & (coppock.shift(1) <= 0)] = 1
        signals[(coppock < 0) & (coppock.shift(1) >= 0)] = -1
        
        return signals


class SchaffTrendCycle(Strategy):
    """
    Schaff Trend Cycle Strategy
    
    Logic: Buy when STC crosses above 25, sell when crosses above 75
    Best for: Early trend detection
    """
    
    def __init__(self, params: Dict):
        super().__init__("SchaffTrendCycle", params)
        self.fast_period = params.get("fast_period", 23)
        self.slow_period = params.get("slow_period", 50)
        self.cycle_period = params.get("cycle_period", 10)
        
        self.rules = [
            {"type": "entry_long", "condition": "STC crosses above 25"},
            {"type": "entry_short", "condition": "STC crosses above 75"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # MACD
        fast_ema = price.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = price.ewm(span=self.slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        
        # Stochastic of MACD
        lowest_low = macd.rolling(self.cycle_period).min()
        highest_high = macd.rolling(self.cycle_period).max()
        stoch = 100 * (macd - lowest_low) / ((highest_high - lowest_low) + EPSILON)
        
        # Double smoothed
        stc = stoch.ewm(span=3, adjust=False).mean()
        stc = stc.ewm(span=3, adjust=False).mean()
        
        signals[(stc > 25) & (stc.shift(1) <= 25)] = 1
        signals[(stc > 75) & (stc.shift(1) <= 75)] = -1
        
        return signals
