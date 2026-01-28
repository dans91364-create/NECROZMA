"""Stochastic Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


"""Stochastic Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class StochasticFast(Strategy):
    """
    Fast Stochastic Oscillator
    
    Logic: Buy when %K crosses above %D in oversold, sell in overbought
    Best for: Volatile ranging markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("StochasticFast", params)
        self.k_period = params.get("k_period", 14)
        self.d_period = params.get("d_period", 3)
        self.oversold = params.get("oversold", 20)
        self.overbought = params.get("overbought", 80)
        
        self.rules = [
            {"type": "entry_long", "condition": "Fast %K crosses above %D below 20"},
            {"type": "entry_short", "condition": "Fast %K crosses below %D above 80"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            lowest_low = low.rolling(self.k_period).min()
            highest_high = high.rolling(self.k_period).max()
            k = 100 * (price - lowest_low) / ((highest_high - lowest_low) + EPSILON)
            d = k.rolling(self.d_period).mean()
            
            buy = (k > d) & (k.shift(1) <= d.shift(1)) & (k < self.oversold)
            sell = (k < d) & (k.shift(1) >= d.shift(1)) & (k > self.overbought)
            signals[buy] = 1
            signals[sell] = -1
        
        return signals


"""Stochastic Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class StochasticSlow(Strategy):
    """
    Slow Stochastic Oscillator
    
    Logic: Smoothed version for clearer signals
    Best for: Less noisy ranging markets
    """
    
    def __init__(self, params: Dict):
        super().__init__("StochasticSlow", params)
        self.k_period = params.get("k_period", 14)
        self.k_smooth = params.get("k_smooth", 3)
        self.d_period = params.get("d_period", 3)
        self.oversold = params.get("oversold", 20)
        self.overbought = params.get("overbought", 80)
        
        self.rules = [
            {"type": "entry_long", "condition": "Slow %K crosses above %D below 20"},
            {"type": "entry_short", "condition": "Slow %K crosses below %D above 80"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            lowest_low = low.rolling(self.k_period).min()
            highest_high = high.rolling(self.k_period).max()
            k_fast = 100 * (price - lowest_low) / ((highest_high - lowest_low) + EPSILON)
            k = k_fast.rolling(self.k_smooth).mean()
            d = k.rolling(self.d_period).mean()
            
            buy = (k > d) & (k.shift(1) <= d.shift(1)) & (k < self.oversold)
            sell = (k < d) & (k.shift(1) >= d.shift(1)) & (k > self.overbought)
            signals[buy] = 1
            signals[sell] = -1
        
        return signals


"""Stochastic Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class StochasticFull(Strategy):
    """
    Full Stochastic Oscillator
    
    Logic: Fully customizable stochastic
    Best for: Advanced mean reversion
    """
    
    def __init__(self, params: Dict):
        super().__init__("StochasticFull", params)
        self.k_period = params.get("k_period", 14)
        self.k_smooth = params.get("k_smooth", 3)
        self.d_period = params.get("d_period", 3)
        self.oversold = params.get("oversold", 20)
        self.overbought = params.get("overbought", 80)
        
        self.rules = [
            {"type": "entry_long", "condition": "Full %K crosses above %D in oversold zone"},
            {"type": "entry_short", "condition": "Full %K crosses below %D in overbought zone"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            lowest_low = low.rolling(self.k_period).min()
            highest_high = high.rolling(self.k_period).max()
            k_raw = 100 * (price - lowest_low) / ((highest_high - lowest_low) + EPSILON)
            k = k_raw.rolling(self.k_smooth).mean()
            d = k.rolling(self.d_period).mean()
            
            signals[(k > d) & (k < self.oversold)] = 1
            signals[(k < d) & (k > self.overbought)] = -1
        
        return signals


"""Stochastic Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON


class StochRSI(Strategy):
    """
    Stochastic RSI
    
    Logic: Stochastic applied to RSI
    Best for: Faster reversal signals
    """
    
    def __init__(self, params: Dict):
        super().__init__("StochRSI", params)
        self.rsi_period = params.get("rsi_period", 14)
        self.stoch_period = params.get("stoch_period", 14)
        self.oversold = params.get("oversold", 20)
        self.overbought = params.get("overbought", 80)
        
        self.rules = [
            {"type": "entry_long", "condition": "StochRSI crosses above 20"},
            {"type": "entry_short", "condition": "StochRSI crosses above 80"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        
        delta = price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / (loss + EPSILON)
        rsi = 100 - (100 / (1 + rs))
        
        lowest_rsi = rsi.rolling(self.stoch_period).min()
        highest_rsi = rsi.rolling(self.stoch_period).max()
        stoch_rsi = 100 * (rsi - lowest_rsi) / ((highest_rsi - lowest_rsi) + EPSILON)
        
        signals[(stoch_rsi > self.oversold) & (stoch_rsi.shift(1) <= self.oversold)] = 1
        signals[(stoch_rsi > self.overbought) & (stoch_rsi.shift(1) <= self.overbought)] = -1
        
        return signals


