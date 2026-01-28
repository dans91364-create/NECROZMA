"""
NECROZMA Strategy Templates
Complete library of 285+ trading strategy templates across 14 categories
"""

from .base import Strategy, EPSILON

# Import all strategy categories
from .trend import *
from .mean_reversion import *
from .momentum import *
from .volatility import *
from .volume import *
from .candlestick import *
from .chart_patterns import *
from .fibonacci import *
from .time_based import *
from .multi_pair import *
from .smc import *
from .statistical import *
from .exotic import *
from .risk_management import *

# Legacy strategies from strategy_factory.py
from .mean_reversion import RSIClassic as MeanReverterLegacy_Placeholder

__all__ = ["Strategy", "EPSILON"]

# Export all strategies from submodules
from . import trend, mean_reversion, momentum, volatility, volume
from . import candlestick, chart_patterns, fibonacci, time_based, multi_pair
from . import smc, statistical, exotic, risk_management
