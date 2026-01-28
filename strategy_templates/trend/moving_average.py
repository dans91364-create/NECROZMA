"""Moving Average Crossover Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class SMAStrategy(Strategy):
    """
    Simple Moving Average Crossover
    
    Logic: Buy when fast SMA crosses above slow SMA, sell when crosses below
    Best for: Trending markets with clear directional moves
    """
    
    def __init__(self, params: Dict):
        super().__init__("SMA", params)
        self.fast_period = params.get("fast_period", 10)
        self.slow_period = params.get("slow_period", 20)
        
        self.rules = [
            {"type": "entry_long", "condition": f"SMA({self.fast_period}) crosses above SMA({self.slow_period})"},
            {"type": "entry_short", "condition": f"SMA({self.fast_period}) crosses below SMA({self.slow_period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        fast_sma = price.rolling(self.fast_period).mean()
        slow_sma = price.rolling(self.slow_period).mean()
        
        signals[(fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))] = 1
        signals[(fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))] = -1
        
        return signals


class EMAStrategy(Strategy):
    """
    Exponential Moving Average Crossover
    
    Logic: Buy when fast EMA crosses above slow EMA, sell when crosses below
    Best for: Trending markets, more responsive than SMA
    """
    
    def __init__(self, params: Dict):
        super().__init__("EMA", params)
        self.fast_period = params.get("fast_period", 9)
        self.slow_period = params.get("slow_period", 21)
        
        self.rules = [
            {"type": "entry_long", "condition": f"EMA({self.fast_period}) crosses above EMA({self.slow_period})"},
            {"type": "entry_short", "condition": f"EMA({self.fast_period}) crosses below EMA({self.slow_period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        fast_ema = price.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = price.ewm(span=self.slow_period, adjust=False).mean()
        
        signals[(fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))] = 1
        signals[(fast_ema < slow_ema) & (fast_ema.shift(1) >= slow_ema.shift(1))] = -1
        
        return signals


class WMAStrategy(Strategy):
    """
    Weighted Moving Average Crossover
    
    Logic: Buy when fast WMA crosses above slow WMA, sell when crosses below
    Best for: Trending markets, gives more weight to recent prices
    """
    
    def __init__(self, params: Dict):
        super().__init__("WMA", params)
        self.fast_period = params.get("fast_period", 10)
        self.slow_period = params.get("slow_period", 20)
        
        self.rules = [
            {"type": "entry_long", "condition": f"WMA({self.fast_period}) crosses above WMA({self.slow_period})"},
            {"type": "entry_short", "condition": f"WMA({self.fast_period}) crosses below WMA({self.slow_period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        def wma(series, period):
            weights = np.arange(1, period + 1)
            return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
        
        fast_wma = wma(price, self.fast_period)
        slow_wma = wma(price, self.slow_period)
        
        signals[(fast_wma > slow_wma) & (fast_wma.shift(1) <= slow_wma.shift(1))] = 1
        signals[(fast_wma < slow_wma) & (fast_wma.shift(1) >= slow_wma.shift(1))] = -1
        
        return signals


class DEMAStrategy(Strategy):
    """
    Double Exponential Moving Average
    
    Logic: Buy when price crosses above DEMA, sell when crosses below
    Best for: Trending markets, reduces lag
    """
    
    def __init__(self, params: Dict):
        super().__init__("DEMA", params)
        self.period = params.get("period", 20)
        
        self.rules = [
            {"type": "entry_long", "condition": f"price crosses above DEMA({self.period})"},
            {"type": "entry_short", "condition": f"price crosses below DEMA({self.period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        ema1 = price.ewm(span=self.period, adjust=False).mean()
        ema2 = ema1.ewm(span=self.period, adjust=False).mean()
        dema = 2 * ema1 - ema2
        
        signals[(price > dema) & (price.shift(1) <= dema.shift(1))] = 1
        signals[(price < dema) & (price.shift(1) >= dema.shift(1))] = -1
        
        return signals


class TEMAStrategy(Strategy):
    """
    Triple Exponential Moving Average
    
    Logic: Buy when price crosses above TEMA, sell when crosses below
    Best for: Trending markets, further reduces lag
    """
    
    def __init__(self, params: Dict):
        super().__init__("TEMA", params)
        self.period = params.get("period", 20)
        
        self.rules = [
            {"type": "entry_long", "condition": f"price crosses above TEMA({self.period})"},
            {"type": "entry_short", "condition": f"price crosses below TEMA({self.period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        ema1 = price.ewm(span=self.period, adjust=False).mean()
        ema2 = ema1.ewm(span=self.period, adjust=False).mean()
        ema3 = ema2.ewm(span=self.period, adjust=False).mean()
        tema = 3 * ema1 - 3 * ema2 + ema3
        
        signals[(price > tema) & (price.shift(1) <= tema.shift(1))] = 1
        signals[(price < tema) & (price.shift(1) >= tema.shift(1))] = -1
        
        return signals


class KAMAStrategy(Strategy):
    """
    Kaufman Adaptive Moving Average
    
    Logic: Buy when price crosses above KAMA, sell when crosses below
    Best for: All market conditions, adapts to volatility
    """
    
    def __init__(self, params: Dict):
        super().__init__("KAMA", params)
        self.period = params.get("period", 10)
        self.fast_sc = params.get("fast_sc", 2)
        self.slow_sc = params.get("slow_sc", 30)
        
        self.rules = [
            {"type": "entry_long", "condition": f"price crosses above KAMA({self.period})"},
            {"type": "entry_short", "condition": f"price crosses below KAMA({self.period})"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        change = abs(price - price.shift(self.period))
        volatility = price.diff().abs().rolling(self.period).sum()
        er = change / (volatility + EPSILON)
        
        fast_alpha = 2 / (self.fast_sc + 1)
        slow_alpha = 2 / (self.slow_sc + 1)
        sc = (er * (fast_alpha - slow_alpha) + slow_alpha) ** 2
        
        kama = pd.Series(index=price.index, dtype=float)
        kama.iloc[0] = price.iloc[0]
        for i in range(1, len(price)):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (price.iloc[i] - kama.iloc[i-1])
        
        signals[(price > kama) & (price.shift(1) <= kama.shift(1))] = 1
        signals[(price < kama) & (price.shift(1) >= kama.shift(1))] = -1
        
        return signals
