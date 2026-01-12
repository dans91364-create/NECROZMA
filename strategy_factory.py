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
        self.threshold = params.get("threshold", 2.0)
        
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
# 💥 BREAKOUT TRADER
# ═══════════════════════════════════════════════════════════════

class BreakoutTrader(Strategy):
    """Breakout trading strategy"""
    
    def __init__(self, params: Dict):
        super().__init__("BreakoutTrader", params)
        self.lookback = params.get("lookback_periods", 20)
        self.threshold = params.get("threshold", 1.5)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"price > upper_band AND volume > avg_volume * 1.5"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"price < lower_band AND volume > avg_volume * 1.5"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate breakout signals"""
        signals = pd.Series(0, index=df.index)
        
        if "mid_price" in df.columns:
            price = df["mid_price"]
            
            # Calculate bands
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            
            upper_band = rolling_mean + (self.threshold * rolling_std)
            lower_band = rolling_mean - (self.threshold * rolling_std)
            
            # Buy on upward breakout
            signals[price > upper_band] = 1
            
            # Sell on downward breakout
            signals[price < lower_band] = -1
        
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
            "BreakoutTrader": BreakoutTrader,
            "RegimeAdapter": RegimeAdapter,
        }
    
    def generate_parameter_combinations(self) -> List[Dict]:
        """
        Generate all parameter combinations
        
        Returns:
            List of parameter dictionaries
        """
        # Get parameter ranges
        lookbacks = self.params.get("lookback_periods", [10, 20, 30])
        thresholds = self.params.get("thresholds", [1.0, 2.0, 3.0])
        stop_losses = self.params.get("stop_loss_pips", [10, 20, 30])
        take_profits = self.params.get("take_profit_pips", [20, 30, 40])
        
        # Generate combinations
        combinations = []
        for lookback, threshold, stop, profit in product(
            lookbacks, thresholds, stop_losses, take_profits
        ):
            # Only keep reasonable risk/reward
            if profit >= stop * 1.5:
                combinations.append({
                    "lookback_periods": lookback,
                    "threshold": threshold,
                    "stop_loss_pips": stop,
                    "take_profit_pips": profit,
                })
        
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
        param_combinations = self.generate_parameter_combinations()
        
        print(f"   Parameter combinations: {len(param_combinations)}")
        
        # Track strategy names to avoid duplicates
        strategy_names = set()
        
        for template_name in self.templates:
            if template_name not in self.template_classes:
                print(f"⚠️  Unknown template: {template_name}")
                continue
            
            template_class = self.template_classes[template_name]
            
            for params in param_combinations:
                # Create unique name including all key parameters
                strategy_name = (
                    f"{template_name}_"
                    f"L{params['lookback_periods']}_"
                    f"T{params['threshold']}_"
                    f"SL{params['stop_loss_pips']}_"
                    f"TP{params['take_profit_pips']}"
                )
                
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
        
        # Final deduplication check (just in case)
        unique_strategies = []
        seen_names = set()
        for strategy in strategies:
            if strategy.name not in seen_names:
                unique_strategies.append(strategy)
                seen_names.add(strategy.name)
        
        if len(unique_strategies) < len(strategies):
            print(f"   ⚠️  Removed {len(strategies) - len(unique_strategies)} duplicate strategies")
        
        print(f"   ✅ Generated {len(unique_strategies)} unique strategies")
        
        return unique_strategies
    
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
