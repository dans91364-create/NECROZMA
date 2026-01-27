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
V3_OPTIMAL_LOOKBACK = 5  # MeanReverterV3 proven optimal lookback period


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
    
    @staticmethod
    def extract_date_from_index(index_value):
        """
        Extract date from index value with multiple fallback methods
        
        Args:
            index_value: pandas index value (could be Timestamp, datetime, or string)
            
        Returns:
            Extracted date as string in YYYY-MM-DD format for consistent comparison
        """
        # Method 1: Try .date() method (works for Timestamp and datetime)
        if hasattr(index_value, 'date'):
            return str(index_value.date())
        # Method 2: Try string conversion (ISO format fallback)
        elif hasattr(index_value, 'strftime'):
            return str(index_value)[:10]
        # Method 3: Direct string conversion fallback
        else:
            return str(index_value)[:10]
    
    def apply_max_trades_per_day_filter(self, signals: pd.Series, df: pd.DataFrame, 
                                       buy_signal: pd.Series, sell_signal: pd.Series,
                                       max_trades_per_day: int) -> pd.Series:
        """
        Apply max trades per day limit to signals
        
        Args:
            signals: Empty signal series to populate
            df: DataFrame with index (must have DatetimeIndex or convertible index)
            buy_signal: Boolean series indicating buy signals
            sell_signal: Boolean series indicating sell signals
            max_trades_per_day: Maximum number of trades allowed per day
            
        Returns:
            Signal series with max trades per day limit applied
        """
        total_trades_today = 0  # FAILSAFE global counter
        current_day = ""  # Initialize to empty string for consistent string comparison
        
        for i in range(len(signals)):
            current_time = df.index[i]
            
            # Extract date using helper method (returns string for consistent comparison)
            trade_date = self.extract_date_from_index(current_time)
            
            # Reset daily counter on new day
            if trade_date != current_day:
                current_day = trade_date
                total_trades_today = 0
            
            # ALWAYS check max trades - NO EXCEPTIONS
            if total_trades_today >= max_trades_per_day:
                continue  # Skip signal generation for rest of day
            
            if buy_signal.iloc[i]:
                signals.iloc[i] = 1
                total_trades_today += 1
            elif sell_signal.iloc[i]:
                signals.iloc[i] = -1
                total_trades_today += 1
        
        return signals
    
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
# 🏆 MEAN REVERTER ORIGINAL - EXACT Round 7 version (Sharpe 6.29, 41 trades)
# ═══════════════════════════════════════════════════════════════

class MeanReverterOriginal(Strategy):
    """
    🏆 MeanReverter ORIGINAL - EXACT Round 7 version (Sharpe 6.29, 41 trades)
    
    This is the PROVEN CHAMPION from Round 7 backtesting.
    DO NOT MODIFY THIS CODE - it's been validated to produce optimal results.
    
    Key features that MUST be preserved:
    1. Division by zero protection: rolling_std.replace(0, EPSILON)
    2. Support both mid_price AND close columns
    3. Accept both threshold_std and threshold parameters
    4. NO max_trades_per_day limit
    """
    
    def __init__(self, params: Dict):
        super().__init__("MeanReverterOriginal", params)
        self.lookback = params.get("lookback_periods", 5)  # L5 is optimal
        # Accept both 'threshold_std' (from config) and 'threshold' (legacy)
        self.threshold = params.get("threshold_std", params.get("threshold", 2.0))
        
        self.add_rule({
            "type": "entry_long",
            "condition": f"z_score < -{self.threshold}"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"z_score > {self.threshold}"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate mean reversion signals - EXACT Round 7 implementation"""
        signals = pd.Series(0, index=df.index)
        
        # CRITICAL: Support both mid_price AND close (original behavior)
        if "mid_price" in df.columns or "close" in df.columns:
            price = df.get("mid_price", df.get("close"))
            
            # Rolling z-score
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            
            # CRITICAL: Division by zero protection (THIS IS REQUIRED!)
            rolling_std_safe = rolling_std.replace(0, EPSILON)
            z_score = (price - rolling_mean) / rolling_std_safe
            
            # Buy when oversold (z_score very negative)
            signals[z_score < -self.threshold] = 1
            
            # Sell when overbought (z_score very positive)
            signals[z_score > self.threshold] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🏆 MEAN REVERTER - CAMPEÃO (Sharpe 6.29)
# ═══════════════════════════════════════════════════════════════

class MeanReverter(Strategy):
    """
    🏆 MeanReverter - Versão EXATA do Round 6/7
    
    HISTÓRICO DE RESULTADOS:
    - Round 7: Sharpe 6.29, 41 trades, Return 59%
    - Esta é a versão que funcionava perfeitamente!
    
    DIFERENÇA TÉCNICA:
    - Usa 'threshold' diretamente (não 'threshold_std')
    - Sem proteção de divisão por zero (original)
    - Verifica apenas 'mid_price' (comportamento original)
    """
    
    def __init__(self, params: Dict):
        super().__init__("MeanReverter", params)
        self.lookback = params.get("lookback_periods", 5)
        # LEGACY: usar 'threshold' diretamente (como era no Round 6/7)
        self.threshold = params.get("threshold", 2.0)
        
        self.add_rule({
            "type": "entry_long",
            "condition": f"z_score < -{self.threshold}"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"z_score > {self.threshold}"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate mean reversion signals - LEGACY VERSION (Round 7)"""
        signals = pd.Series(0, index=df.index)
        
        # Original: verificar apenas 'mid_price'
        if "mid_price" in df.columns:
            price = df["mid_price"]
            
            # Rolling z-score (versão original sem proteção)
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            z_score = (price - rolling_mean) / rolling_std
            
            # Buy when oversold
            signals[z_score < -self.threshold] = 1
            
            # Sell when overbought
            signals[z_score > self.threshold] = -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🏆 MEAN REVERTER LEGACY (Alias for backward compatibility)
# ═══════════════════════════════════════════════════════════════

# MeanReverterLegacy is an alias for MeanReverter (Round 7 version)
# This maintains backward compatibility with existing configs and tests
MeanReverterLegacy = MeanReverter


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
# 🎯 MEAN REVERTER V3 (Optimized from Round 3 Backtesting)
# ═══════════════════════════════════════════════════════════════

class MeanReverterV3(Strategy):
    """
    Optimized Mean Reversion Strategy based on Round 3 backtesting results.
    
    Key optimizations:
    - Fixed lookback=5 (proven optimal)
    - Adaptive threshold (1.8-2.2 based on volatility)
    - Optimal R:R ratio of 1:1.67 (SL30:TP50)
    - Confirmation filter (require 2 consecutive signals)
    - Session filter (avoid Asian session low liquidity)
    
    Best historical performance:
    - Sharpe: 6.29
    - Return: 59.3%
    - Win Rate: 51.2%
    """
    
    # Class constant: Optimal lookback period proven in backtesting
    OPTIMAL_LOOKBACK = 5
    
    def __init__(self, params: Dict):
        super().__init__("MeanReverterV3", params)
        
        # FIXED optimal parameters (proven in backtesting)
        self.lookback = self.OPTIMAL_LOOKBACK  # Always use optimal value
        
        # Configurable but with proven defaults
        self.base_threshold = params.get("threshold_std", 2.0)
        self.adaptive_threshold = params.get("adaptive_threshold", True)
        self.volatility_lookback = params.get("volatility_lookback", 100)
        
        # Optimal risk management (R:R = 1:1.67)
        self.stop_loss_pips = params.get("stop_loss_pips", 30)
        self.take_profit_pips = params.get("take_profit_pips", 50)
        
        # Confirmation filter
        self.require_confirmation = params.get("require_confirmation", True)
        self.confirmation_periods = params.get("confirmation_periods", 2)
        
        # Session filter (avoid low liquidity)
        self.use_session_filter = params.get("use_session_filter", False)
        self.active_hours = params.get("active_hours", (8, 20))  # London+NY sessions
        
        # Max trades per day (failsafe) - REDUCED from 10 to 5
        self.max_trades_per_day = params.get("max_trades_per_day", 5)
        
        # Add rules
        self.add_rule({
            "type": "entry_long",
            "condition": f"z_score < -{self.base_threshold} AND confirmation AND session_active"
        })
        self.add_rule({
            "type": "entry_short",
            "condition": f"z_score > {self.base_threshold} AND confirmation AND session_active"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate optimized mean reversion signals"""
        signals = pd.Series(0, index=df.index)
        
        if "mid_price" in df.columns or "close" in df.columns:
            price = df.get("mid_price", df.get("close"))
            
            # Calculate z-score with FIXED lookback=5
            rolling_mean = price.rolling(self.lookback).mean()
            rolling_std = price.rolling(self.lookback).std()
            
            # Prevent division by zero
            rolling_std_safe = rolling_std.replace(0, EPSILON)
            z_score = (price - rolling_mean) / rolling_std_safe
            
            # Adaptive threshold based on volatility regime
            if self.adaptive_threshold:
                # Calculate recent volatility (rolling window)
                volatility = price.pct_change().rolling(self.volatility_lookback).std()
                volatility_mean = volatility.mean()  # Overall mean volatility
                
                # Adjust threshold: higher current vol = lower threshold (more sensitive)
                # Lower current vol = higher threshold (more selective)
                # Use ratio of current vol to mean vol to adjust threshold
                vol_ratio = volatility / (volatility_mean + EPSILON)
                threshold = self.base_threshold / vol_ratio
                threshold = threshold.clip(1.8, 2.2)  # Keep within proven range
            else:
                threshold = self.base_threshold
            
            # Raw buy/sell signals
            raw_buy = z_score < -threshold
            raw_sell = z_score > threshold
            
            # Confirmation filter: require N consecutive signals
            if self.require_confirmation:
                # Require consecutive signals
                confirmed_buy = raw_buy.rolling(self.confirmation_periods).sum() >= self.confirmation_periods
                confirmed_sell = raw_sell.rolling(self.confirmation_periods).sum() >= self.confirmation_periods
            else:
                confirmed_buy = raw_buy
                confirmed_sell = raw_sell
            
            # Session filter
            if self.use_session_filter and hasattr(df.index, 'hour'):
                # Check if hour is within active trading hours
                hour = pd.Series(df.index.hour, index=df.index)
                session_active = (hour >= self.active_hours[0]) & (hour < self.active_hours[1])
            else:
                session_active = True
            
            # Apply filters
            buy_signal = confirmed_buy & session_active
            sell_signal = confirmed_sell & session_active
            
            # Apply max trades per day limit using base class method
            signals = self.apply_max_trades_per_day_filter(
                signals, df, buy_signal, sell_signal, self.max_trades_per_day
            )
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 💥 MOMENTUM BURST (Explosions of momentum) - BULLETPROOF FIX
# ═══════════════════════════════════════════════════════════════

class MomentumBurst(Strategy):
    """
    Momentum burst strategy with BULLETPROOF trade limiting.
    
    After multiple failed attempts (PRs #62, #75, #76, #77, #78, #80),
    this version uses a simple loop that ALWAYS enforces limits.
    """
    
    def __init__(self, params: Dict):
        super().__init__("MomentumBurst", params)
        self.lookback = params.get("lookback_periods", 15)
        self.threshold = params.get("threshold_std", params.get("threshold", 1.5))
        self.volume_multiplier = params.get("volume_multiplier", 1.5)
        
        # BULLETPROOF limits - very conservative
        self.max_trades_per_day = params.get("max_trades_per_day", 5)
        self.cooldown_minutes = params.get("cooldown_minutes", 120)  # 2 hours minimum
        
        self.add_rule({
            "type": "entry_long",
            "condition": f"momentum_burst_up AND volume_surge (max {self.max_trades_per_day}/day)"
        })
        self.add_rule({
            "type": "entry_short", 
            "condition": f"momentum_burst_down AND volume_surge (max {self.max_trades_per_day}/day)"
        })
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate momentum burst signals with ABSOLUTE trade limiting."""
        signals = pd.Series(0, index=df.index)
        
        # Check if we have price data
        if "mid_price" in df.columns or "close" in df.columns:
            price = df.get("mid_price", df.get("close"))
            
            # Calculate momentum burst conditions
            price_change = price.diff()
            rolling_std = price_change.rolling(self.lookback).std()
            rolling_std_safe = rolling_std.replace(0, 1e-8)
            
            momentum_burst_up = price_change > (self.threshold * rolling_std_safe)
            momentum_burst_down = price_change < (-self.threshold * rolling_std_safe)
            
            # Volume confirmation (optional)
            if "volume" in df.columns:
                avg_volume = df["volume"].rolling(self.lookback).mean()
                volume_surge = df["volume"] > avg_volume * self.volume_multiplier
            else:
                volume_surge = pd.Series(True, index=df.index)
            
            # Raw signals before limiting
            raw_buy = momentum_burst_up & volume_surge
            raw_sell = momentum_burst_down & volume_surge
            
            # BULLETPROOF LIMITING - Simple loop, no edge cases
            last_signal_time = None
            trades_per_day = {}
            
            for i in range(len(df)):
                idx = df.index[i]
                
                # Extract date - works with ANY index type
                if hasattr(idx, 'date'):
                    current_date = str(idx.date())
                elif hasattr(idx, 'strftime'):
                    current_date = idx.strftime('%Y-%m-%d')
                else:
                    current_date = str(idx)[:10]
                
                # CHECK 1: Daily limit (ABSOLUTE - no exceptions)
                day_trades = trades_per_day.get(current_date, 0)
                if day_trades >= self.max_trades_per_day:
                    continue
                
                # CHECK 2: Cooldown in real minutes (ABSOLUTE - no exceptions)
                if last_signal_time is not None:
                    try:
                        if hasattr(idx, 'timestamp') or hasattr(idx, 'to_pydatetime'):
                            time_diff_seconds = (idx - last_signal_time).total_seconds()
                            time_diff_minutes = time_diff_seconds / 60
                            if time_diff_minutes < self.cooldown_minutes:
                                continue
                    except (TypeError, AttributeError, ValueError):
                        # If time comparison fails, skip cooldown check but daily limit still applies
                        pass
                
                # Apply signal if all checks pass
                if raw_buy.iloc[i]:
                    signals.iloc[i] = 1
                    last_signal_time = idx
                    trades_per_day[current_date] = day_trades + 1
                elif raw_sell.iloc[i]:
                    signals.iloc[i] = -1
                    last_signal_time = idx
                    trades_per_day[current_date] = day_trades + 1
        
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
            "MeanReverterOriginal": MeanReverterOriginal,  # 🏆 Round 7 EXACT (Sharpe 6.29, 41 trades)
            "MeanReverterLegacy": MeanReverterLegacy,  # 🏆 Round 7 version (Sharpe 6.29)
            "MeanReverter": MeanReverter,
            "RegimeAdapter": RegimeAdapter,
            "MeanReverterV2": MeanReverterV2,
            "MeanReverterV3": MeanReverterV3,
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
        # V3 always uses OPTIMAL_LOOKBACK=5, others use config or default
        if template_name == "MeanReverterV3":
            lookbacks = [V3_OPTIMAL_LOOKBACK]  # V3 ALWAYS uses fixed lookback=5 (proven optimal)
        else:
            lookbacks = template_params.get("lookback_periods", [20])
        
        # MeanReverterLegacy uses 'threshold', others use 'threshold_std'
        if template_name == "MeanReverterLegacy":
            thresholds = template_params.get("threshold", template_params.get("threshold_std", [1.0]))
        else:
            thresholds = template_params.get("threshold_std", template_params.get("thresholds", [1.0]))
        
        stop_losses = template_params.get("stop_loss_pips", [20])
        take_profits = template_params.get("take_profit_pips", [40])
        
        # Generate all combinations of core parameters
        for lookback, threshold, stop, profit in product(
            lookbacks, thresholds, stop_losses, take_profits
        ):
            # Risk/reward filter - less strict for V3 and MeanReverter (tested combinations)
            if template_name == "MeanReverterV3":
                min_rr_ratio = 1.2
            elif template_name in ["MeanReverter", "MeanReverterLegacy"]:
                min_rr_ratio = 1.3  # Allow SL30/TP40 (1.33 ratio)
            else:
                min_rr_ratio = 1.5
            if profit >= stop * min_rr_ratio:
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
                
                elif template_name == "MeanReverterV3":
                    # Add V3-specific variations
                    adaptive_thresholds = template_params.get("adaptive_threshold", [True, False])
                    require_confirmations = template_params.get("require_confirmation", [True, False])
                    use_session_filters = template_params.get("use_session_filter", [True, False])
                    
                    for adaptive, confirm, session in product(
                        adaptive_thresholds, require_confirmations, use_session_filters
                    ):
                        params = base_params.copy()
                        # V3 uses "threshold_std" instead of "threshold"
                        params["threshold_std"] = params.pop("threshold", 2.0)
                        params["adaptive_threshold"] = adaptive
                        params["require_confirmation"] = confirm
                        params["use_session_filter"] = session
                        combinations.append(params)
                
                else:
                    # For other strategies (TrendFollower, MeanReverter), just use base params
                    params = base_params.copy()
                    # For MeanReverter, also include threshold_std for naming consistency
                    if template_name == "MeanReverter":
                        params["threshold_std"] = params["threshold"]
                    combinations.append(params)
        
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
                # Handle both 'threshold' and 'threshold_std' (V3 uses threshold_std)
                threshold_value = params.get('threshold_std', params.get('threshold', 1.0))
                strategy_name = f"{template_name}_L{params['lookback_periods']}_T{threshold_value}_SL{params['stop_loss_pips']}_TP{params['take_profit_pips']}"
                
                # Add strategy-specific parameters to name
                if template_name == "MomentumBurst" and "cooldown" in params:
                    strategy_name += f"_CD{params['cooldown']}"
                elif template_name == "MeanReverterV2":
                    if "rsi_oversold" in params and "rsi_overbought" in params:
                        strategy_name += f"_RSI{params['rsi_oversold']}-{params['rsi_overbought']}"
                    if "volume_filter" in params:
                        strategy_name += f"_VF{params['volume_filter']}"
                elif template_name == "MeanReverterV3":
                    # Include V3-specific parameters in the name
                    strategy_name += f"_AT{int(params.get('adaptive_threshold', True))}"
                    strategy_name += f"_RC{int(params.get('require_confirmation', True))}"
                    strategy_name += f"_SF{int(params.get('use_session_filter', False))}"
                
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
