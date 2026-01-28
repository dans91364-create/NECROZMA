"""Trend Strategy Exports"""
from .moving_average import (
    SMAStrategy,
    EMAStrategy,
    WMAStrategy,
    DEMAStrategy,
    TEMAStrategy,
    KAMAStrategy,
)
from .macd import (
    MACDClassic,
    MACDHistogram,
    MACDDivergence,
)
from .adx import (
    ADXTrend,
    DMICrossover,
)
from .parabolic_sar import ParabolicSAR
from .supertrend import SuperTrend
from .ichimoku import (
    IchimokuCloud,
    IchimokuTKCross,
)
from .donchian import DonchianBreakout
from .keltner import KeltnerBreakout
from .aroon import AroonCrossover
from .vortex import VortexCrossover
from .alligator import (
    AlligatorStrategy,
    GatorOscillator,
)
from .misc_trend import (
    TRIXStrategy,
    KSTStrategy,
    CoppockCurve,
    SchaffTrendCycle,
)

__all__ = [
    "SMAStrategy",
    "EMAStrategy",
    "WMAStrategy",
    "DEMAStrategy",
    "TEMAStrategy",
    "KAMAStrategy",
    "MACDClassic",
    "MACDHistogram",
    "MACDDivergence",
    "ADXTrend",
    "DMICrossover",
    "ParabolicSAR",
    "SuperTrend",
    "IchimokuCloud",
    "IchimokuTKCross",
    "DonchianBreakout",
    "KeltnerBreakout",
    "AroonCrossover",
    "VortexCrossover",
    "AlligatorStrategy",
    "GatorOscillator",
    "TRIXStrategy",
    "KSTStrategy",
    "CoppockCurve",
    "SchaffTrendCycle",
]
