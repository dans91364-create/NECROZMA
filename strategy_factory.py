#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - STRATEGY FACTORY 💎🌟⚡

Automatic Strategy Generation System
"From patterns to profit - the strategy forge"

Features:
- Multiple strategy templates (Trend, Mean Reversion, Breakout, Regime)
- Parameter variation and combination
- Rule generation from patterns
- Strategy pool creation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from itertools import product
import json

from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS

# Constants
EPSILON = 1e-8  # Small value to prevent division by zero


# ═══════════════════════════════════════════════════════════════
# 🎯 STRATEGY BASE CLASS
# ═══════════════════════════════════════════════════════════════

class Strategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str, params: Dict):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params
        self.rules = []
        
    def add_rule(self, rule: Dict):
        """Add a trading rule"""
        self.rules.append(rule)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals
        
        Args:
            df: DataFrame with features
            
        Returns:
            Series with signals (1=buy, -1=sell, 0=neutral)
        """
        raise NotImplementedError("Subclasses must implement generate_signals")
    
    def to_dict(self) -> Dict:
        """Convert strategy to dictionary"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "params": self.params,
            "rules": self.rules,
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


# ═══════════════════════════════════════════════════════════════
# 📈 TREND FOLLOWER
# ═══════════════════════════════════════════════════════════════

class TrendFollower(Strategy):
    """Trend following strategy"""
    
    def __init__(self, params: Dict):
        super().__init__("TrendFollower", params)
        self.lookback = params.get("lookback_periods", 20)
        self.threshold = params.get("threshold", 1.0)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"momentum > {self.threshold} AND trend_strength > 0.5"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"momentum < -{self.threshold} AND trend_strength > 0.5"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate trend following signals"""
        signals = pd.Series(0, index=df.index)
        
        # Look for momentum/trend features
        momentum_cols = [c for c in df.columns if "momentum" in c.lower() or "trend" in c.lower()]
        
        if momentum_cols:
            momentum = df[momentum_cols[0]]
            
            # Buy when momentum is strong positive
            signals[momentum > self.threshold] = 1
            
            # Sell when momentum is strong negative
            signals[momentum < -self.threshold] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🔄 MEAN REVERTER
# ═══════════════════════════════════════════════════════════════

class MeanReverter(Strategy):
    """Mean reversion strategy"""
    
    def __init__(self, params: Dict):
        super().__init__("MeanReverter", params)
        self.lookback = params.get("lookback_periods", 20)
        self.threshold = params.get("threshold", 1.5)  # Changed from 2.0 to 1.5
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"z_score < -{self.threshold} AND volatility < 0.8"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"z_score > {self.threshold} AND volatility < 0.8"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate mean reversion signals"""
        signals = pd.Series(0, index=df.index)
        
        # Calculate z-score of price
        if "mid_price" in df.columns:
            price = df["mid_price"]
            
            # Rolling z-score
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            z_score = (price - rolling_mean) / rolling_std
            
            # Buy when oversold
            signals[z_score < -self.threshold] = 1
            
            # Sell when overbought
            signals[z_score > self.threshold] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🎭 REGIME ADAPTER
# ═══════════════════════════════════════════════════════════════

class RegimeAdapter(Strategy):
    """Regime-adaptive strategy"""
    
    def __init__(self, params: Dict):
        super().__init__("RegimeAdapter", params)
        self.trending_threshold = params.get("threshold", 0.5)
        
        # Add rules
        self.add_rule({
            "type": "regime_trend",
            "condition": "IF trending regime: use trend following"
        })
        self.add_rule({
            "type": "regime_range",
            "condition": "IF ranging regime: use mean reversion"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate regime-adaptive signals"""
        signals = pd.Series(0, index=df.index)
        
        # Check for regime column
        if "regime" in df.columns:
            # Different strategy per regime
            for regime in df["regime"].unique():
                regime_mask = df["regime"] == regime
                
                # Simple heuristic: alternate between trend and mean reversion
                if regime % 2 == 0:
                    # Trend following in even regimes
                    sub_strategy = TrendFollower(self.params)
                else:
                    # Mean reversion in odd regimes
                    sub_strategy = MeanReverter(self.params)
                
                regime_signals = sub_strategy.generate_signals(df[regime_mask])
                signals[regime_mask] = regime_signals
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🔄 MEAN REVERTER V2 (Bollinger + RSI + Volume)
# ═══════════════════════════════════════════════════════════════

class MeanReverterV2(Strategy):
    """
    Enhanced Mean Reversion with Bollinger Bands, RSI, and Volume confirmation
    - Entry: Price touches lower/upper Bollinger Band + RSI oversold/overbought + Volume spike
    - More selective than original MeanReverter
    """
    
    def __init__(self, params: Dict):
        super().__init__("MeanReverterV2", params)
        self.lookback = params.get("lookback_periods", 20)
        self.threshold = params.get("threshold", 2.0)
        self.rsi_oversold = params.get("rsi_oversold", 25)  # Changed from 30
        self.rsi_overbought = params.get("rsi_overbought", 75)  # Changed from 70
        self.volume_multiplier = params.get("volume_multiplier", 1.3)  # Changed from 1.5
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"price < lower_bb AND rsi < {self.rsi_oversold} AND volume > avg_volume * {self.volume_multiplier}"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"price > upper_bb AND rsi > {self.rsi_overbought} AND volume > avg_volume * {self.volume_multiplier}"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate enhanced mean reversion signals"""
        signals = pd.Series(0, index=df.index)
        
        if "mid_price" in df.columns or "close" in df.columns:
            price = df.get("mid_price", df.get("close"))
            
            # Calculate Bollinger Bands
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            
            upper_bb = rolling_mean + (self.threshold * rolling_std)
            lower_bb = rolling_mean - (self.threshold * rolling_std)
            
            # Simple RSI approximation (change / range)
            price_change = price.diff()
            rolling_std_safe = rolling_std.replace(0, EPSILON)  # Prevent division by zero
            rsi = 50 + (price_change.rolling(self.lookback).mean() / rolling_std_safe * 100)
            rsi = rsi.clip(0, 100)
            
            # Volume check
            if "volume" in df.columns:
                avg_volume = df["volume"].rolling(self.lookback).mean()
                volume_spike = df["volume"] > avg_volume * self.volume_multiplier
            else:
                volume_spike = True  # No volume filter if not available
            
            # Buy when oversold (price below lower BB, low RSI, volume spike)
            buy_signal = (price < lower_bb) & (rsi < self.rsi_oversold) & volume_spike
            signals[buy_signal] = 1
            
            # Sell when overbought (price above upper BB, high RSI, volume spike)
            sell_signal = (price > upper_bb) & (rsi > self.rsi_overbought) & volume_spike
            signals[sell_signal] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 💥 MOMENTUM BURST (Explosions of momentum)
# ═══════════════════════════════════════════════════════════════

class MomentumBurst(Strategy):
    """
    Captures sudden momentum explosions with volume confirmation
    - Detects rapid price movement (> 2 std dev)
    - Requires volume confirmation (> 1.5x average)
    - Rides the momentum wave
    """
    
    def __init__(self, params: Dict):
        super().__init__("MomentumBurst", params)
        self.lookback = params.get("lookback_periods", 20)
        self.threshold = params.get("threshold", 2.0)  # Std dev threshold
        self.volume_multiplier = 1.5
        self.cooldown = params.get("cooldown", 60)  # NEW: cooldown candles
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"price_change > {self.threshold} * std_dev AND volume > avg_volume * {self.volume_multiplier}"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"price_change < -{self.threshold} * std_dev AND volume > avg_volume * {self.volume_multiplier}"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate momentum burst signals"""
        signals = pd.Series(0, index=df.index)
        
        if "mid_price" in df.columns or "close" in df.columns:
            price = df.get("mid_price", df.get("close"))
            
            # Calculate price changes
            price_change = price.diff()
            rolling_std = price_change.rolling(self.lookback).std()
            
            # Detect momentum burst (> threshold std devs)
            momentum_burst_up = price_change > (self.threshold * rolling_std)
            momentum_burst_down = price_change < (-self.threshold * rolling_std)
            
            # Volume confirmation
            if "volume" in df.columns:
                avg_volume = df["volume"].rolling(self.lookback).mean()
                volume_surge = df["volume"] > avg_volume * self.volume_multiplier
            else:
                volume_surge = True  # No volume filter if not available
            
            # RAW signals before cooldown
            raw_buy = momentum_burst_up & volume_surge
            raw_sell = momentum_burst_down & volume_surge
            
            # Apply cooldown - only allow signal if no signal in last N candles
            last_signal_idx = -self.cooldown - 1
            for i in range(len(signals)):
                if raw_buy.iloc[i] and (i - last_signal_idx) > self.cooldown:
                    signals.iloc[i] = 1
                    last_signal_idx = i
                elif raw_sell.iloc[i] and (i - last_signal_idx) > self.cooldown:
                    signals.iloc[i] = -1
                    last_signal_idx = i
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🔗 CORRELATION TRADER (Correlation Breakdown)
# ═══════════════════════════════════════════════════════════════

class CorrelationTrader(Strategy):
    """
    Trade correlation breakdowns between pairs
    - Detect when correlation breaks (divergence)
    - Bet on convergence (mean reversion of spread)
    
    Parameters:
    - correlation_threshold: 0.7, 0.8, 0.85
    - zscore_entry: 1.5, 2.0, 2.5
    - zscore_exit: 0.5, 1.0
    """
    
    def __init__(self, params: Dict):
        super().__init__("CorrelationTrader", params)
        self.lookback = params.get("lookback_periods", 50)
        self.correlation_threshold = params.get("correlation_threshold", 0.7)
        self.zscore_entry = params.get("zscore_entry", 2.0)
        self.zscore_exit = params.get("zscore_exit", 1.0)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"correlation > {self.correlation_threshold} AND zscore < -{self.zscore_entry}"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"correlation > {self.correlation_threshold} AND zscore > {self.zscore_entry}"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate signals based on correlation breakdown"""
        signals = pd.Series(0, index=df.index)
        
        # Look for correlation features in the dataframe
        corr_cols = [c for c in df.columns if "_corr_" in c and "zscore" not in c]
        zscore_cols = [c for c in df.columns if "_corr_zscore_" in c]
        
        if corr_cols and zscore_cols:
            # Use first correlation pair found
            corr = df[corr_cols[0]]
            zscore = df[zscore_cols[0]]
            
            # High correlation + extreme divergence = entry
            high_corr = corr > self.correlation_threshold
            
            # Buy when negative divergence (zscore < -threshold)
            buy_signal = high_corr & (zscore < -self.zscore_entry)
            signals[buy_signal] = 1
            
            # Sell when positive divergence (zscore > threshold)
            sell_signal = high_corr & (zscore > self.zscore_entry)
            signals[sell_signal] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 📊 PAIR DIVERGENCE (Divergence Between Correlated Pairs)
# ═══════════════════════════════════════════════════════════════

class PairDivergence(Strategy):
    """
    Detect divergences between correlated pairs
    - EUR/USD up, GBP/USD not following → buy GBP/USD
    - Mean reversion of spread
    
    Parameters:
    - divergence_std: 1.5, 2.0, 2.5
    - lookback_period: 20, 50, 100
    """
    
    def __init__(self, params: Dict):
        super().__init__("PairDivergence", params)
        self.lookback = params.get("lookback_periods", 50)
        self.divergence_std = params.get("divergence_std", 2.0)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"divergence < -{self.divergence_std} std"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"divergence > {self.divergence_std} std"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate signals based on pair divergence"""
        signals = pd.Series(0, index=df.index)
        
        # Look for divergence features
        div_cols = [c for c in df.columns if "_divergence" in c]
        
        if div_cols:
            divergence = df[div_cols[0]]
            
            # Calculate rolling stats
            rolling_mean = divergence.rolling(self.lookback).mean()
            rolling_std = divergence.rolling(self.lookback).std()
            
            # Z-score of divergence
            zscore = (divergence - rolling_mean) / (rolling_std + EPSILON)
            
            # Buy when extreme negative divergence
            buy_signal = zscore < -self.divergence_std
            signals[buy_signal] = 1
            
            # Sell when extreme positive divergence
            sell_signal = zscore > self.divergence_std
            signals[sell_signal] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# ⏱️ LEAD-LAG STRATEGY (Leader-Follower Relationship)
# ═══════════════════════════════════════════════════════════════

class LeadLagStrategy(Strategy):
    """
    Exploit lead/lag relationship between pairs
    - EUR/USD often leads GBP/USD
    - Enter in follower after leader moves
    
    Parameters:
    - lag_periods: 1, 2, 3, 5
    - min_leader_move: 0.1%, 0.2%, 0.3%
    """
    
    def __init__(self, params: Dict):
        super().__init__("LeadLagStrategy", params)
        self.lookback = params.get("lookback_periods", 20)
        self.lag_periods = params.get("lag_periods", 2)
        self.min_leader_move = params.get("min_leader_move", 0.002)  # 0.2%
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"leader moved up > {self.min_leader_move*100}% in last {self.lag_periods} periods"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"leader moved down > {self.min_leader_move*100}% in last {self.lag_periods} periods"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate signals based on lead-lag relationship"""
        signals = pd.Series(0, index=df.index)
        
        # Look for lead-lag features
        lag_cols = [c for c in df.columns if "_lead_lag" in c and "_corr" not in c]
        
        if lag_cols and ("mid_price" in df.columns or "close" in df.columns):
            price = df.get("mid_price", df.get("close"))
            
            # Calculate price movement
            price_change = price.pct_change(periods=self.lag_periods)
            
            # Detect significant leader movement
            leader_moved_up = price_change > self.min_leader_move
            leader_moved_down = price_change < -self.min_leader_move
            
            # Follow the leader
            signals[leader_moved_up] = 1
            signals[leader_moved_down] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🎭 RISK SENTIMENT (Risk-On / Risk-Off)
# ═══════════════════════════════════════════════════════════════

class RiskSentiment(Strategy):
    """
    Trade based on risk-on/risk-off sentiment
    - Risk ON: AUD, NZD up / JPY, CHF down
    - Risk OFF: AUD, NZD down / JPY, CHF up
    
    Parameters:
    - sentiment_threshold: 0.6, 0.7, 0.8
    - confirmation_periods: 3, 5, 10
    """
    
    def __init__(self, params: Dict):
        super().__init__("RiskSentiment", params)
        self.lookback = params.get("lookback_periods", 20)
        self.sentiment_threshold = params.get("sentiment_threshold", 0.7)
        self.confirmation_periods = params.get("confirmation_periods", 5)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"risk_sentiment > {self.sentiment_threshold} for {self.confirmation_periods} periods"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"risk_sentiment < {1-self.sentiment_threshold} for {self.confirmation_periods} periods"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate signals based on risk sentiment"""
        signals = pd.Series(0, index=df.index)
        
        # Look for risk sentiment score
        if "risk_sentiment_score" in df.columns:
            sentiment = df["risk_sentiment_score"]
            
            # Detect sustained risk-on (high sentiment)
            risk_on = sentiment.rolling(self.confirmation_periods).mean() > self.sentiment_threshold
            
            # Detect sustained risk-off (low sentiment)
            risk_off = sentiment.rolling(self.confirmation_periods).mean() < (1 - self.sentiment_threshold)
            
            # Buy on risk-on sentiment
            signals[risk_on] = 1
            
            # Sell on risk-off sentiment
            signals[risk_off] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 💵 USD STRENGTH (USD Strength Index)
# ═══════════════════════════════════════════════════════════════

class USDStrength(Strategy):
    """
    Trade based on USD strength index
    - USD strong: sell EUR/USD, GBP/USD, buy USD/JPY, USD/CHF
    - USD weak: buy EUR/USD, GBP/USD, sell USD/JPY, USD/CHF
    
    Parameters:
    - strength_threshold: 0.6, 0.7, 0.8
    - pairs_to_trade: 2, 3, 4
    """
    
    def __init__(self, params: Dict):
        super().__init__("USDStrength", params)
        self.lookback = params.get("lookback_periods", 20)
        self.strength_threshold = params.get("strength_threshold", 0.7)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"USD_strength < {1-self.strength_threshold} (USD weak)"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"USD_strength > {self.strength_threshold} (USD strong)"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate signals based on USD strength"""
        signals = pd.Series(0, index=df.index)
        
        # Look for USD strength index
        if "USD_strength_index" in df.columns:
            usd_strength = df["USD_strength_index"]
            
            # Strong USD
            usd_strong = usd_strength > self.strength_threshold
            
            # Weak USD
            usd_weak = usd_strength < (1 - self.strength_threshold)
            
            # Buy when USD is weak (for EUR/USD, GBP/USD, etc.)
            signals[usd_weak] = 1
            
            # Sell when USD is strong
            signals[usd_strong] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🏭 STRATEGY FACTORY
# ═══════════════════════════════════════════════════════════════

class StrategyFactory:
    """
    Automatic strategy generation factory
    
    Usage:
        factory = StrategyFactory()
        strategies = factory.generate_strategies()
    """
    
    def __init__(self, templates: List[str] = None, params: Dict = None):
        """
        Initialize strategy factory
        
        Args:
            templates: List of template names (default: from config)
            params: Parameter ranges (default: from config)
        """
        self.templates = templates or STRATEGY_TEMPLATES
        self.params = params or STRATEGY_PARAMS
        
        # Map template names to classes
        self.template_classes = {
            "TrendFollower": TrendFollower,
            "MeanReverter": MeanReverter,
            "RegimeAdapter": RegimeAdapter,
            "MeanReverterV2": MeanReverterV2,
            "MomentumBurst": MomentumBurst,
            # Correlation Templates (not used in Round 3)
            "CorrelationTrader": CorrelationTrader,
            "PairDivergence": PairDivergence,
            "LeadLagStrategy": LeadLagStrategy,
            "RiskSentiment": RiskSentiment,
            "USDStrength": USDStrength,
        }
    
    def generate_parameter_combinations(self, template_name: str) -> List[Dict]:
        """
        Generate parameter combinations for a specific strategy template
        
        Args:
            template_name: Name of the strategy template
            
        Returns:
            List of parameter dictionaries
        """
        # Get template-specific params or use global params as fallback
        if isinstance(self.params, dict) and template_name in self.params:
            # New format: per-strategy parameters
            template_params = self.params[template_name]
        else:
            # Old format: global parameters (fallback for compatibility)
            template_params = self.params
        
        combinations = []
        
        # Extract parameter lists
        lookbacks = template_params.get("lookback_periods", [20])
        thresholds = template_params.get("threshold_std", template_params.get("thresholds", [1.0]))
        stop_losses = template_params.get("stop_loss_pips", [20])
        take_profits = template_params.get("take_profit_pips", [40])
        
        # Generate all combinations of core parameters
        for lookback, threshold, stop, profit in product(
            lookbacks, thresholds, stop_losses, take_profits
        ):
            # Only keep reasonable risk/reward (profit >= stop * 1.5)
            if profit >= stop * 1.5:
                base_params = {
                    "lookback_periods": lookback,
                    "threshold": threshold,
                    "stop_loss_pips": stop,
                    "take_profit_pips": profit,
                }
                
                # Add strategy-specific parameters
                if template_name == "MomentumBurst":
                    # Add cooldown variations
                    cooldowns = template_params.get("cooldown_minutes", template_params.get("cooldown", [60]))
                    for cooldown in cooldowns:
                        params = base_params.copy()
                        params["cooldown"] = cooldown
                        combinations.append(params)
                
                elif template_name == "MeanReverterV2":
                    # Add RSI and volume filter variations
                    rsi_oversolds = template_params.get("rsi_oversold", [30])
                    rsi_overboughts = template_params.get("rsi_overbought", [70])
                    volume_filters = template_params.get("volume_filter", [1.5])
                    
                    for rsi_os, rsi_ob, vol_filter in product(rsi_oversolds, rsi_overboughts, volume_filters):
                        params = base_params.copy()
                        params["rsi_oversold"] = rsi_os
                        params["rsi_overbought"] = rsi_ob
                        params["volume_filter"] = vol_filter
                        combinations.append(params)
                
                else:
                    # For other strategies (TrendFollower, MeanReverter), just use base params
                    combinations.append(base_params)
        
        return combinations
    
    def generate_strategies(self, max_strategies: int = None) -> List[Strategy]:
        """
        Generate pool of strategies
        
        Args:
            max_strategies: Maximum number of strategies (default: all)
            
        Returns:
            List of Strategy objects (with unique names)
        """
        print(f"\n🏭 Generating strategies from {len(self.templates)} templates...")
        
        strategies = []
        strategy_names = set()
        
        for template_name in self.templates:
            if template_name not in self.template_classes:
                print(f"⚠️  Unknown template: {template_name}")
                continue
            
            template_class = self.template_classes[template_name]
            
            # Generate parameter combinations for this template
            param_combinations = self.generate_parameter_combinations(template_name)
            print(f"   {template_name}: {len(param_combinations)} combinations")
            
            for params in param_combinations:
                # Create unique name including all key parameters
                strategy_name = f"{template_name}_L{params['lookback_periods']}_T{params['threshold']}_SL{params['stop_loss_pips']}_TP{params['take_profit_pips']}"
                
                # Add strategy-specific parameters to name
                if template_name == "MomentumBurst" and "cooldown" in params:
                    strategy_name += f"_CD{params['cooldown']}"
                elif template_name == "MeanReverterV2":
                    if "rsi_oversold" in params and "rsi_overbought" in params:
                        strategy_name += f"_RSI{params['rsi_oversold']}-{params['rsi_overbought']}"
                    if "volume_filter" in params:
                        strategy_name += f"_VF{params['volume_filter']}"
                
                # Check for duplicates
                if strategy_name in strategy_names:
                    continue  # Skip duplicate
                
                strategy = template_class(params)
                strategy.name = strategy_name
                strategies.append(strategy)
                strategy_names.add(strategy_name)
                
                if max_strategies and len(strategies) >= max_strategies:
                    break
            
            if max_strategies and len(strategies) >= max_strategies:
                break
        
        print(f"   ✅ Generated {len(strategies)} unique strategies")
        
        return strategies
    
    def create_strategy_from_rules(self, rules: List[Dict], 
                                   name: str = "CustomStrategy") -> Strategy:
        """
        Create custom strategy from discovered rules
        
        Args:
            rules: List of rule dictionaries
            name: Strategy name
            
        Returns:
            Custom Strategy object
        """
        # Use TrendFollower as base and add custom rules
        params = {"lookback_periods": 20, "threshold": 1.0}
        strategy = TrendFollower(params)
        strategy.name = name
        strategy.rules = rules
        
        return strategy
    
    def save_strategies(self, strategies: List[Strategy], filepath: str):
        """
        Save strategies to JSON file
        
        Args:
            strategies: List of Strategy objects
            filepath: Output file path
        """
        data = {
            "n_strategies": len(strategies),
            "strategies": [s.to_dict() for s in strategies],
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(strategies)} strategies to {filepath}")


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🏭 STRATEGY FACTORY TEST 🏭                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create factory
    factory = StrategyFactory()
    
    # Generate strategies
    strategies = factory.generate_strategies(max_strategies=20)
    
    print(f"\n📋 Generated Strategies:")
    for i, strategy in enumerate(strategies[:10]):
        print(f"   {i+1:2d}. {strategy.name}")
        print(f"       Type: {strategy.__class__.__name__}")
        print(f"       Params: {strategy.params}")
        print(f"       Rules: {len(strategy.rules)}")
    
    if len(strategies) > 10:
        print(f"   ... and {len(strategies) - 10} more")
    
    # Test signal generation with dummy data
    print(f"\n🧪 Testing signal generation...")
    np.random.seed(42)
    
    test_df = pd.DataFrame({
        "mid_price": 1.10 + np.cumsum(np.random.randn(100) * 0.001),
        "momentum": np.random.randn(100),
        "trend_strength": np.random.uniform(0, 1, 100),
    })
    
    strategy = strategies[0]
    signals = strategy.generate_signals(test_df)
    
    print(f"   Strategy: {strategy.name}")
    print(f"   Signals: {signals.value_counts().to_dict()}")
    
    # Save strategies
    factory.save_strategies(strategies, "/tmp/test_strategies.json")
    
    print("\n✅ Strategy factory test complete!")
