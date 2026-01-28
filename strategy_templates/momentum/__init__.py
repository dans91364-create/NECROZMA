"""Momentum Strategies"""
from .roc import ROCStrategy
from .momentum_indicator import MomentumIndicator, ChandeForecast, PriceMomentumOsc, RelativeMomentum
from .elder_impulse import ElderImpulse, ElderRay
from .awesome_oscillator import ErgodicOscillator, PrettyGoodOsc
from .squeeze_momentum import PsychologicalLine, BalanceOfPower, SqueezeMomentum, AbsoluteStrength, DoubleSmoothedStoch, MomentumDivergence
__all__ = ["ROCStrategy", "MomentumIndicator", "ChandeForecast", "PriceMomentumOsc", "RelativeMomentum",
    "ElderImpulse", "ElderRay", "ErgodicOscillator", "PrettyGoodOsc", "PsychologicalLine", "BalanceOfPower",
    "SqueezeMomentum", "AbsoluteStrength", "DoubleSmoothedStoch", "MomentumDivergence"]
