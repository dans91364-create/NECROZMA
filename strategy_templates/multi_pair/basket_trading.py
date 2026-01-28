"""Multi-pair Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class BasketTrading(Strategy):
    """Currency Basket"""
    def __init__(self, params: Dict):
        super().__init__("BasketTrading", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "trade basket of currencies bullish signal"}, {"type": "entry_short", "condition": "trade basket of currencies bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class EMBasket(Strategy):
    """Emerging Market Basket"""
    def __init__(self, params: Dict):
        super().__init__("EMBasket", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "EM currency basket bullish signal"}, {"type": "entry_short", "condition": "EM currency basket bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

