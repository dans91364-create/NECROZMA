#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BACKTESTER 💎🌟⚡

Robust Backtesting Engine
"Testing strategies across time and space"

Features:
- Walk-forward validation
- Multi-period testing
- Comprehensive metrics (Sharpe, Sortino, Calmar, etc.)
- Monte Carlo simulation
- Drawdown analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import warnings

warnings.filterwarnings("ignore")

from config import BACKTEST_CONFIG, MONTE_CARLO_CONFIG, METRIC_THRESHOLDS


# ═══════════════════════════════════════════════════════════════
# 🔧 CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Trading days per year for annualization
TRADING_DAYS_PER_YEAR = 252

# Risk-free rate (default)
DEFAULT_RISK_FREE_RATE = 0.0

# Default position sizing parameters (used if config doesn't specify)
DEFAULT_INITIAL_CAPITAL = 10000
DEFAULT_LOT_SIZE = 0.1
DEFAULT_PIP_VALUE_PER_LOT = 10
DEFAULT_PIP_DECIMAL_PLACES = 4


# ═══════════════════════════════════════════════════════════════
# 📊 PERFORMANCE METRICS
# ═══════════════════════════════════════════════════════════════

@dataclass
class BacktestResults:
    """Container for backtest results"""
    strategy_name: str
    n_trades: int
    win_rate: float
    profit_factor: float
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    expectancy: float
    recovery_factor: float
    ulcer_index: float
    trades: pd.DataFrame
    equity_curve: pd.Series
    trades_detailed: List[Dict] = field(default_factory=list)  
    """
    Detailed trade information including:
    - entry_time, exit_time: Timestamps as strings
    - entry_price, exit_price: Trade prices
    - direction: 'long' or 'short'
    - pnl_pips, pnl_usd, pnl_pct: P&L in pips, USD, and percentage
    - duration_minutes: Trade duration
    - exit_reason: 'stop_loss', 'take_profit', or 'signal'
    - market_context: Dict with volatility, trend_strength, volume_relative, 
                      spread_pips, pattern_detected, pattern_sequence, 
                      hour_of_day, day_of_week
    - price_history: Dict with timestamps, open, high, low, close, volume arrays
    """
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            "strategy_name": self.strategy_name,
            "n_trades": self.n_trades,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "total_return": self.total_return,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "calmar_ratio": self.calmar_ratio,
            "max_drawdown": self.max_drawdown,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "expectancy": self.expectancy,
            "recovery_factor": self.recovery_factor,
            "ulcer_index": self.ulcer_index,
        }
        
        # Add detailed trades if available
        if self.trades_detailed:
            result["trades_detailed"] = self.trades_detailed
        
        return result


# ═══════════════════════════════════════════════════════════════
# 🎯 BACKTESTER ENGINE
# ═══════════════════════════════════════════════════════════════

class Backtester:
    """
    Robust backtesting engine with walk-forward validation
    
    Usage:
        backtester = Backtester()
        results = backtester.backtest(strategy, df)
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize backtester
        
        Args:
            config: Configuration dictionary (uses BACKTEST_CONFIG if None)
        """
        self.config = config or BACKTEST_CONFIG
        
        # Extract position sizing parameters
        capital_config = self.config.get('capital', {})
        self.initial_capital = capital_config.get('initial_capital', DEFAULT_INITIAL_CAPITAL)
        self.lot_size = capital_config.get('default_lot_size', DEFAULT_LOT_SIZE)
        self.pip_value_per_lot = capital_config.get('pip_value_per_lot', DEFAULT_PIP_VALUE_PER_LOT)
        self.pip_decimal_places = capital_config.get('pip_decimal_places', DEFAULT_PIP_DECIMAL_PLACES)
        
        # Track detailed trade information
        self.trades_detailed = []
        self.df = None  # Store DataFrame for context retrieval
    
    def _pips_to_usd(self, pips: float) -> float:
        """
        Convert pips to USD based on lot size
        
        For EUR/USD with 0.1 lot:
        - 1 pip = 0.0001 price change
        - pip value = $10 per pip per standard lot (1.0 lot)
        - For 0.1 lot: pip value = $10 * 0.1 = $1 per pip
        - 20 pips = 20 * $1 = $20
        
        Args:
            pips: Number of pips (positive or negative)
            
        Returns:
            USD value of the pips for current lot size
        """
        pip_value = self.pip_value_per_lot * self.lot_size
        return pips * pip_value
        
    def _calculate_returns(self, trades: pd.DataFrame) -> pd.Series:
        """Calculate returns from trades"""
        if len(trades) == 0:
            return pd.Series([])
        
        returns = trades["pnl"].values
        return pd.Series(returns)
    
    def _calculate_equity_curve(self, trades: pd.DataFrame, 
                                initial_capital: float = None) -> pd.Series:
        """
        Calculate equity curve starting from initial capital
        
        Args:
            trades: DataFrame with trade results
            initial_capital: Starting capital (uses default if None)
            
        Returns:
            Series with equity values (starts with initial capital)
        """
        if initial_capital is None:
            initial_capital = DEFAULT_INITIAL_CAPITAL
            
        if len(trades) == 0:
            return pd.Series([initial_capital])
        
        # Build equity curve: start with initial capital, then cumsum of PnL
        # This is more efficient than a loop for large trade counts
        equity_curve = pd.concat([
            pd.Series([initial_capital]),
            initial_capital + trades["pnl"].cumsum()
        ], ignore_index=True)
        
        return equity_curve
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, 
                               risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(TRADING_DAYS_PER_YEAR) * (excess_returns.mean() / excess_returns.std())
    
    def _calculate_sortino_ratio(self, returns: pd.Series,
                                 risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return np.sqrt(TRADING_DAYS_PER_YEAR) * (excess_returns.mean() / downside_returns.std())
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(equity_curve) < 2:
            return 0.0
        
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        return abs(drawdown.min())
    
    def _calculate_calmar_ratio(self, total_return: float, 
                                max_drawdown: float) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown == 0:
            return 0.0
        
        return total_return / max_drawdown
    
    def _calculate_ulcer_index(self, equity_curve: pd.Series) -> float:
        """Calculate Ulcer Index (downside risk)"""
        if len(equity_curve) < 2:
            return 0.0
        
        running_max = equity_curve.expanding().max()
        drawdown_pct = ((equity_curve - running_max) / running_max) * 100
        
        squared_drawdowns = drawdown_pct ** 2
        ulcer = np.sqrt(squared_drawdowns.mean())
        
        return ulcer
    
    def _calculate_metrics(self, trades: pd.DataFrame, 
                          equity_curve: pd.Series) -> Dict:
        """Calculate all performance metrics"""
        if len(trades) == 0:
            return self._empty_metrics()
        
        # Basic stats
        winning_trades = trades[trades["pnl"] > 0]
        losing_trades = trades[trades["pnl"] < 0]
        
        n_trades = len(trades)
        n_wins = len(winning_trades)
        n_losses = len(losing_trades)
        
        win_rate = n_wins / n_trades if n_trades > 0 else 0.0
        
        # PnL stats
        total_profit = winning_trades["pnl"].sum() if n_wins > 0 else 0.0
        total_loss = abs(losing_trades["pnl"].sum()) if n_losses > 0 else 0.0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0.0
        
        avg_win = winning_trades["pnl"].mean() if n_wins > 0 else 0.0
        avg_loss = losing_trades["pnl"].mean() if n_losses > 0 else 0.0
        
        largest_win = winning_trades["pnl"].max() if n_wins > 0 else 0.0
        largest_loss = losing_trades["pnl"].min() if n_losses > 0 else 0.0
        
        # Expectancy
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        
        # Returns-based metrics
        returns = self._calculate_returns(trades)
        
        sharpe = self._calculate_sharpe_ratio(returns)
        sortino = self._calculate_sortino_ratio(returns)
        
        # Equity-based metrics
        initial_capital = equity_curve.iloc[0] if len(equity_curve) > 0 else 10000
        final_capital = equity_curve.iloc[-1] if len(equity_curve) > 0 else initial_capital
        
        total_return = (final_capital - initial_capital) / initial_capital
        max_dd = self._calculate_max_drawdown(equity_curve)
        calmar = self._calculate_calmar_ratio(total_return, max_dd)
        ulcer = self._calculate_ulcer_index(equity_curve)
        
        recovery_factor = total_return / max_dd if max_dd > 0 else 0.0
        
        return {
            "n_trades": n_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "max_drawdown": max_dd,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "expectancy": expectancy,
            "recovery_factor": recovery_factor,
            "ulcer_index": ulcer,
        }
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dict"""
        return {
            "n_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "max_drawdown": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "expectancy": 0.0,
            "recovery_factor": 0.0,
            "ulcer_index": 0.0,
        }
    
    def _get_market_context(self, idx: int) -> Dict:
        """
        Extract market conditions at given index.
        
        Args:
            idx (int): Index in DataFrame
        
        Returns:
            dict: Market context including volatility, trend, volume, etc.
        """
        if self.df is None or idx >= len(self.df):
            return {}
        
        bar = self.df.iloc[idx]
        
        # Calculate volatility (ATR-like measure over last 20 bars)
        window_start = max(0, idx - 20)
        window = self.df.iloc[window_start:idx + 1]
        
        if len(window) > 1:
            high_low_range = window['high'] - window['low']
            volatility = (high_low_range.mean() / window['close'].mean()) if window['close'].mean() > 0 else 0.0
        else:
            volatility = 0.0
        
        # Trend strength (momentum if available)
        trend_strength = abs(float(bar.get('momentum', 0.0)))
        
        # Volume relative to average
        if 'volume' in window.columns and len(window) > 1:
            volume_avg = window['volume'].mean()
            volume_relative = float(bar.get('volume', volume_avg) / volume_avg) if volume_avg > 0 else 1.0
        else:
            volume_relative = 1.0
        
        # Spread (use default if not available)
        spread_pips = float(bar.get('spread', 1.5))
        
        # Pattern detected
        pattern_detected = str(bar.get('pattern', 'unknown'))
        
        # Get pattern sequence (last 3 bars)
        pattern_sequence = []
        for i in range(max(0, idx - 2), idx + 1):
            if i < len(self.df):
                pattern_sequence.append(str(self.df.iloc[i].get('pattern', 'unknown')))
        
        # Time features
        timestamp = self.df.index[idx]
        hour_of_day = timestamp.hour if hasattr(timestamp, 'hour') else 0
        day_of_week = timestamp.strftime('%A') if hasattr(timestamp, 'strftime') else 'Unknown'
        
        return {
            'volatility': float(volatility),
            'trend_strength': float(trend_strength),
            'volume_relative': float(volume_relative),
            'spread_pips': float(spread_pips),
            'pattern_detected': pattern_detected,
            'pattern_sequence': pattern_sequence,
            'hour_of_day': int(hour_of_day),
            'day_of_week': day_of_week
        }
    
    def _get_price_history(self, entry_idx: int, exit_idx: int) -> Dict:
        """
        Get OHLCV data around the trade for charting.
        
        Args:
            entry_idx (int): Entry bar index
            exit_idx (int): Exit bar index
        
        Returns:
            dict: Price history with timestamps and OHLC data
        """
        if self.df is None:
            return {}
        
        # Get 50 bars before entry, all bars during trade, 20 bars after exit
        start_idx = max(0, entry_idx - 50)
        end_idx = min(len(self.df), exit_idx + 20)
        
        history_slice = self.df.iloc[start_idx:end_idx]
        
        # Get volume data efficiently
        if 'volume' in history_slice.columns:
            volume_data = [float(x) for x in history_slice['volume'].tolist()]
        else:
            volume_data = [0.0] * len(history_slice)
        
        return {
            'timestamps': [str(ts) for ts in history_slice.index],
            'open': [float(x) for x in history_slice['open'].tolist()],
            'high': [float(x) for x in history_slice['high'].tolist()],
            'low': [float(x) for x in history_slice['low'].tolist()],
            'close': [float(x) for x in history_slice['close'].tolist()],
            'volume': volume_data
        }
    
    def _record_detailed_trade(self, entry_idx: int, exit_idx: int, 
                              entry_price: float, exit_price: float,
                              direction: str, pnl_pips: float, pnl_usd: float, 
                              exit_reason: str = 'unknown'):
        """
        Record a detailed trade with full context
        
        Args:
            entry_idx: Entry bar index
            exit_idx: Exit bar index
            entry_price: Entry price
            exit_price: Exit price
            direction: 'long' or 'short'
            pnl_pips: P&L in pips
            pnl_usd: P&L in USD
            exit_reason: Reason for exit ('stop_loss', 'take_profit', 'signal')
        """
        if self.df is None:
            return
        
        # Get timestamps
        entry_time = self.df.index[entry_idx] if entry_idx < len(self.df) else None
        exit_time = self.df.index[exit_idx] if exit_idx < len(self.df) else None
        
        # Calculate duration
        duration_minutes = 0
        if entry_time and exit_time:
            # Check if both timestamps support datetime operations
            try:
                duration_minutes = int((exit_time - entry_time).total_seconds() / 60)
            except (AttributeError, TypeError):
                # If not datetime, use index difference as proxy (bars)
                duration_minutes = exit_idx - entry_idx
        
        # Calculate P&L percentage
        pnl_pct = (pnl_usd / self.initial_capital * 100) if self.initial_capital > 0 else 0.0
        
        # Create detailed trade record
        trade_detail = {
            'entry_time': str(entry_time) if entry_time else '',
            'exit_time': str(exit_time) if exit_time else '',
            'entry_price': float(entry_price),
            'exit_price': float(exit_price),
            'direction': direction,
            'pnl_pips': float(pnl_pips),
            'pnl_usd': float(pnl_usd),
            'pnl_pct': float(pnl_pct),
            'duration_minutes': duration_minutes,
            'exit_reason': exit_reason,
            'market_context': self._get_market_context(entry_idx),
            'price_history': self._get_price_history(entry_idx, exit_idx)
        }
        
        self.trades_detailed.append(trade_detail)
    
    def simulate_trades(self, signals: pd.Series, prices: pd.Series,
                       stop_loss_pips: float = 20, 
                       take_profit_pips: float = 40,
                       pip_value: float = 0.0001) -> pd.DataFrame:
        """
        Simulate trades from signals with Forex position sizing
        
        PnL is calculated in USD based on lot size:
        - Pips are calculated from price changes
        - Pips are converted to USD using lot_size and pip_value_per_lot
        - For 0.1 lot EUR/USD: 20 pips = 20 * ($10/pip/lot * 0.1) = $20
        
        Args:
            signals: Series with signals (1=buy, -1=sell, 0=neutral)
            prices: Series with prices
            stop_loss_pips: Stop loss in pips
            take_profit_pips: Take profit in pips
            pip_value: Value of 1 pip in price terms (0.0001 for EUR/USD)
            
        Returns:
            DataFrame with trade results (pnl in USD)
        """
        trades = []
        in_position = False
        entry_price = 0.0
        entry_idx = 0
        position_type = 0  # 1=long, -1=short
        
        for i in range(len(signals)):
            if in_position:
                # Check exit conditions
                current_price = prices.iloc[i]
                
                if position_type == 1:  # Long position
                    # Calculate pips
                    pips = (current_price - entry_price) / pip_value
                    
                    # Check stop/target
                    if pips <= -stop_loss_pips:
                        # Stop loss hit - convert pips to USD
                        pnl = self._pips_to_usd(-stop_loss_pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "long",
                            "exit_reason": "stop_loss",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "long", -stop_loss_pips, pnl, "stop_loss"
                        )
                        in_position = False
                    elif pips >= take_profit_pips:
                        # Take profit hit - convert pips to USD
                        pnl = self._pips_to_usd(take_profit_pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "long",
                            "exit_reason": "take_profit",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "long", take_profit_pips, pnl, "take_profit"
                        )
                        in_position = False
                    elif signals.iloc[i] == -1:
                        # Exit signal - convert pips to USD
                        pnl = self._pips_to_usd(pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "long",
                            "exit_reason": "signal",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "long", pips, pnl, "signal"
                        )
                        in_position = False
                        
                else:  # Short position
                    # Calculate pips
                    pips = (entry_price - current_price) / pip_value
                    
                    # Check stop/target
                    if pips <= -stop_loss_pips:
                        # Stop loss hit - convert pips to USD
                        pnl = self._pips_to_usd(-stop_loss_pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "short",
                            "exit_reason": "stop_loss",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "short", -stop_loss_pips, pnl, "stop_loss"
                        )
                        in_position = False
                    elif pips >= take_profit_pips:
                        # Take profit hit - convert pips to USD
                        pnl = self._pips_to_usd(take_profit_pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "short",
                            "exit_reason": "take_profit",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "short", take_profit_pips, pnl, "take_profit"
                        )
                        in_position = False
                    elif signals.iloc[i] == 1:
                        # Exit signal - convert pips to USD
                        pnl = self._pips_to_usd(pips)
                        trades.append({
                            "entry_idx": entry_idx,
                            "exit_idx": i,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "pnl": pnl,
                            "type": "short",
                            "exit_reason": "signal",
                        })
                        # Record detailed trade
                        self._record_detailed_trade(
                            entry_idx, i, entry_price, current_price,
                            "short", pips, pnl, "signal"
                        )
                        in_position = False
            
            # Check entry signals
            if not in_position and signals.iloc[i] != 0:
                in_position = True
                entry_price = prices.iloc[i]
                entry_idx = i
                position_type = signals.iloc[i]
        
        return pd.DataFrame(trades)
    
    def backtest(self, strategy, df: pd.DataFrame,
                initial_capital: float = None) -> BacktestResults:
        """
        Backtest a strategy
        
        Args:
            strategy: Strategy object with generate_signals method
            df: DataFrame with price and feature data
            initial_capital: Starting capital (uses config default if None)
            
        Returns:
            BacktestResults object
        """
        # Store DataFrame for context retrieval
        self.df = df
        
        # Reset detailed trades for new backtest
        self.trades_detailed = []
        
        # Use config default if not specified
        if initial_capital is None:
            initial_capital = self.initial_capital
        
        # ═══ VALIDATION: Check data quality ═══
        if df is None or len(df) == 0:
            raise ValueError("❌ DataFrame is empty!")
        
        # Check for price column
        if "mid_price" not in df.columns and "close" not in df.columns:
            raise ValueError("❌ DataFrame must have 'mid_price' or 'close' column")
        
        # Get prices early for validation
        if "mid_price" in df.columns:
            prices = df["mid_price"]
        elif "close" in df.columns:
            prices = df["close"]
        else:
            raise ValueError("DataFrame must have 'mid_price' or 'close' column")
        
        # Validate price data quality
        if prices.isnull().all():
            raise ValueError("❌ All prices are null!")
        
        if prices.std() == 0:
            raise ValueError("❌ Price data has no variation (constant prices)!")
        
        if (prices <= 0).any():
            raise ValueError("❌ Price data contains zero or negative values!")
        
        # Generate signals
        signals = strategy.generate_signals(df)
        
        # Simulate trades
        stop_loss = strategy.params.get("stop_loss_pips", 20)
        take_profit = strategy.params.get("take_profit_pips", 40)
        
        trades = self.simulate_trades(signals, prices, stop_loss, take_profit)
        
        # Calculate equity curve
        equity_curve = self._calculate_equity_curve(trades, initial_capital)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, equity_curve)
        
        # ═══ WARNING: Check if results look suspicious ═══
        if metrics["total_return"] != 0:
            # Returns suspiciously small (like e-07)?
            if abs(metrics["total_return"]) < 1e-5:
                import warnings
                warnings.warn(f"⚠️  Suspiciously small return: {metrics['total_return']:.2e}", UserWarning)
        
        # Create results object
        results = BacktestResults(
            strategy_name=strategy.name,
            trades=trades,
            equity_curve=equity_curve,
            trades_detailed=self.trades_detailed,  # Include detailed trades
            **metrics
        )
        
        return results
    
    def test_strategies(self, strategies: List, df: pd.DataFrame, 
                        verbose: bool = True) -> List[BacktestResults]:
        """
        Backtest multiple strategies
        
        Args:
            strategies: List of Strategy objects
            df: DataFrame with price/feature data
            verbose: Show progress (default: True)
            
        Returns:
            List of BacktestResults
        """
        results = []
        total = len(strategies)
        
        for i, strategy in enumerate(strategies, 1):
            if verbose and i % 100 == 0:
                print(f"   📊 Backtesting {i}/{total} ({100*i/total:.1f}%)...")
            
            try:
                result = self.backtest(strategy, df)
                results.append(result)
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Strategy '{strategy.name}' failed: {e}")
        
        return results
    
    def walk_forward_test(self, strategy, df: pd.DataFrame,
                         n_splits: int = None) -> List[BacktestResults]:
        """
        Walk-forward validation
        
        Args:
            strategy: Strategy object
            df: DataFrame with data
            n_splits: Number of splits (default from config)
            
        Returns:
            List of BacktestResults for each split
        """
        if n_splits is None:
            n_splits = self.config.get("n_splits", 5)
        
        print(f"\n📊 Walk-forward testing with {n_splits} splits...")
        
        results = []
        
        # Split data
        split_size = len(df) // n_splits
        
        for i in range(n_splits):
            start_idx = i * split_size
            end_idx = start_idx + split_size if i < n_splits - 1 else len(df)
            
            split_df = df.iloc[start_idx:end_idx]
            
            print(f"   Split {i+1}/{n_splits}: {len(split_df):,} rows")
            
            result = self.backtest(strategy, split_df)
            results.append(result)
        
        return results


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              📊 BACKTESTER TEST 📊                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    print("📊 Generating test data...")
    np.random.seed(42)
    n_samples = 1000
    
    test_df = pd.DataFrame({
        "mid_price": 1.10 + np.cumsum(np.random.randn(n_samples) * 0.0001),
        "momentum": np.random.randn(n_samples),
    })
    
    # Create simple test strategy
    from strategy_factory import TrendFollower
    
    strategy = TrendFollower({"lookback_periods": 20, "threshold": 0.5,
                              "stop_loss_pips": 15, "take_profit_pips": 30})
    
    # Run backtest
    print("\n🧪 Running backtest...")
    backtester = Backtester()
    results = backtester.backtest(strategy, test_df)
    
    print(f"\n📊 Results for {results.strategy_name}:")
    print(f"   Trades: {results.n_trades}")
    print(f"   Win Rate: {results.win_rate:.1%}")
    print(f"   Profit Factor: {results.profit_factor:.2f}")
    print(f"   Total Return: {results.total_return:.1%}")
    print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"   Sortino Ratio: {results.sortino_ratio:.2f}")
    print(f"   Max Drawdown: {results.max_drawdown:.1%}")
    print(f"   Expectancy: {results.expectancy:.4f}")
    
    # Walk-forward test
    print("\n" + "="*60)
    wf_results = backtester.walk_forward_test(strategy, test_df, n_splits=3)
    
    print(f"\n📊 Walk-Forward Summary:")
    for i, result in enumerate(wf_results):
        print(f"   Split {i+1}: {result.n_trades} trades, "
              f"Return: {result.total_return:.1%}, "
              f"Sharpe: {result.sharpe_ratio:.2f}")
    
    print("\n✅ Backtester test complete!")
