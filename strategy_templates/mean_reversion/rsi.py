"""RSI-based Mean Reversion Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON


class RSIClassic(Strategy):
    """
    Classic RSI Strategy
    
    Logic: Buy when RSI < oversold, sell when RSI > overbought
    Best for: Range-bound markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("RSIClassic", params)
        self.period = params.get("period", 14)
        self.oversold = params.get("oversold", 30)
        self.overbought = params.get("overbought", 70)
        
        self.rules = [
            {"type": "entry_long", "condition": f"RSI < {self.oversold}"},
            {"type": "entry_short", "condition": f"RSI > {self.overbought}"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        delta = price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()
        
        rs = gain / (loss + EPSILON)
        rsi = 100 - (100 / (1 + rs))
        
        signals[rsi < self.oversold] = 1
        signals[rsi > self.overbought] = -1
        
        return signals


class RSIDivergence(Strategy):
    """
    RSI Divergence Strategy
    
    Logic: Buy on bullish divergence, sell on bearish divergence
    Best for: Reversal detection
    """
    
    def __init__(self, params: Dict):
        super().__init__("RSIDivergence", params)
        self.period = params.get("period", 14)
        self.lookback = params.get("lookback", 5)
        
        self.rules = [
            {"type": "entry_long", "condition": "bullish divergence (price lower low, RSI higher low)"},
            {"type": "entry_short", "condition": "bearish divergence (price higher high, RSI lower high)"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        delta = price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()
        rs = gain / (loss + EPSILON)
        rsi = 100 - (100 / (1 + rs))
        
        price_low = price.rolling(self.lookback).min()
        price_high = price.rolling(self.lookback).max()
        rsi_low = rsi.rolling(self.lookback).min()
        rsi_high = rsi.rolling(self.lookback).max()
        
        bullish_div = (price == price_low) & (rsi > rsi.shift(self.lookback))
        bearish_div = (price == price_high) & (rsi < rsi.shift(self.lookback))
        
        signals[bullish_div] = 1
        signals[bearish_div] = -1
        
        return signals


class ConnorsRSI(Strategy):
    """
    Connors RSI Strategy
    
    Logic: Composite of RSI, streak RSI, and rank
    Best for: Short-term mean reversion
    """
    
    def __init__(self, params: Dict):
        super().__init__("ConnorsRSI", params)
        self.rsi_period = params.get("rsi_period", 3)
        self.streak_period = params.get("streak_period", 2)
        self.rank_period = params.get("rank_period", 100)
        self.oversold = params.get("oversold", 10)
        self.overbought = params.get("overbought", 90)
        
        self.rules = [
            {"type": "entry_long", "condition": f"ConnorsRSI < {self.oversold}"},
            {"type": "entry_short", "condition": f"ConnorsRSI > {self.overbought}"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        # Standard RSI
        delta = price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / (loss + EPSILON)
        rsi = 100 - (100 / (1 + rs))
        
        # Streak RSI (simplified)
        streak = pd.Series(0, index=df.index)
        for i in range(1, len(price)):
            if price.iloc[i] > price.iloc[i-1]:
                streak.iloc[i] = max(streak.iloc[i-1] + 1, 1)
            elif price.iloc[i] < price.iloc[i-1]:
                streak.iloc[i] = min(streak.iloc[i-1] - 1, -1)
        
        streak_gain = (streak.where(streak > 0, 0)).rolling(self.streak_period).mean()
        streak_loss = (-streak.where(streak < 0, 0)).rolling(self.streak_period).mean()
        streak_rs = streak_gain / (streak_loss + EPSILON)
        streak_rsi = 100 - (100 / (1 + streak_rs))
        
        # Percent rank
        pct_rank = price.rolling(self.rank_period).apply(
            lambda x: (x < x.iloc[-1]).sum() / len(x) * 100 if len(x) > 0 else 50, raw=False
        )
        
        # Connors RSI
        crsi = (rsi + streak_rsi + pct_rank) / 3
        
        signals[crsi < self.oversold] = 1
        signals[crsi > self.overbought] = -1
        
        return signals
