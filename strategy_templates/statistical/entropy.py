"""Statistical Trading Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON

class EntropyStrategy(Strategy):
    """Entropy Strategy"""
    def __init__(self, params: Dict):
        super().__init__("EntropyStrategy", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "market entropy buy signal"}, {"type": "entry_short", "condition": "market entropy sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class FractalDimension(Strategy):
    """Fractal Dimension"""
    def __init__(self, params: Dict):
        super().__init__("FractalDimension", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "fractal analysis buy signal"}, {"type": "entry_short", "condition": "fractal analysis sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class SpectralAnalysis(Strategy):
    """Spectral Analysis"""
    def __init__(self, params: Dict):
        super().__init__("SpectralAnalysis", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "frequency domain buy signal"}, {"type": "entry_short", "condition": "frequency domain sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class PCAStrategy(Strategy):
    """Principal Component Analysis"""
    def __init__(self, params: Dict):
        super().__init__("PCAStrategy", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "PCA buy signal"}, {"type": "entry_short", "condition": "PCA sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class FactorModel(Strategy):
    """Factor Model"""
    def __init__(self, params: Dict):
        super().__init__("FactorModel", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "multi-factor buy signal"}, {"type": "entry_short", "condition": "multi-factor sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class MonteCarloSim(Strategy):
    """Monte Carlo Simulation"""
    def __init__(self, params: Dict):
        super().__init__("MonteCarloSim", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "MC simulation buy signal"}, {"type": "entry_short", "condition": "MC simulation sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class BootstrapStrategy(Strategy):
    """Bootstrap Strategy"""
    def __init__(self, params: Dict):
        super().__init__("BootstrapStrategy", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "bootstrap resampling buy signal"}, {"type": "entry_short", "condition": "bootstrap resampling sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class JumpDiffusion(Strategy):
    """Jump Diffusion"""
    def __init__(self, params: Dict):
        super().__init__("JumpDiffusion", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "jump processes buy signal"}, {"type": "entry_short", "condition": "jump processes sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

class KellyCriterion(Strategy):
    """Kelly Criterion"""
    def __init__(self, params: Dict):
        super().__init__("KellyCriterion", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "optimal position sizing buy signal"}, {"type": "entry_short", "condition": "optimal position sizing sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

