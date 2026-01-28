"""Multi-pair Strategies"""
from .correlation import CorrelationTrader, PairDivergence
from .cointegration import LeadLagStrategy, StatisticalArbitrage, SpreadTrading
from .basket_trading import BasketTrading, EMBasket
from .currency_strength import CurrencyStrength, USDStrengthIndex, DXYFollower, G10Momentum
from .risk_sentiment import RiskOnRiskOff
from .carry_trade import CarryTrade, TriangularArbitrage
from .cross_asset import GoldForexCorrelation, EquityForexCorr, VIXCorrelation, BondForexCorr, CommodityCurrency, GlobalMacro
__all__ = ["CorrelationTrader", "PairDivergence", "LeadLagStrategy", "StatisticalArbitrage", "SpreadTrading", "BasketTrading", "EMBasket", "CurrencyStrength", "USDStrengthIndex", "DXYFollower", "G10Momentum", "RiskOnRiskOff", "CarryTrade", "TriangularArbitrage", "GoldForexCorrelation", "EquityForexCorr", "VIXCorrelation", "BondForexCorr", "CommodityCurrency", "GlobalMacro"]
