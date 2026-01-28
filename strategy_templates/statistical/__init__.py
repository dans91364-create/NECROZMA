"""Statistical Strategies"""
from .zscore_strategy import ZScoreStatArb
from .kalman_filter import KalmanFilterTrend
from .hurst_exponent import HurstExponent
from .regime_detection import HiddenMarkovRegime, RegimeSwitching, VarianceRatio, AutocorrelationStrat
from .mean_reversion_stat import MeanReversionOU
from .garch import GARCHVolatility
from .linear_regression import LinearRegressionChannel, StandardDevChannel
from .entropy import (EntropyStrategy, FractalDimension, SpectralAnalysis, PCAStrategy, FactorModel,
    MonteCarloSim, BootstrapStrategy, JumpDiffusion, KellyCriterion)
__all__ = ["ZScoreStatArb", "KalmanFilterTrend", "HurstExponent", "HiddenMarkovRegime", "RegimeSwitching", "VarianceRatio", "AutocorrelationStrat", "MeanReversionOU", "GARCHVolatility", "LinearRegressionChannel", "StandardDevChannel", "EntropyStrategy", "FractalDimension", "SpectralAnalysis", "PCAStrategy", "FactorModel", "MonteCarloSim", "BootstrapStrategy", "JumpDiffusion", "KellyCriterion"]
