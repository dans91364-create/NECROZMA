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
from dataclasses import dataclass
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
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
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
        self.initial_capital = capital_config.get('initial_capital', 10000)
        self.lot_size = capital_config.get('default_lot_size', 0.1)
        self.pip_value_per_lot = capital_config.get('pip_value_per_lot', 10)
        self.pip_decimal_places = capital_config.get('pip_decimal_places', 4)
    
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
                                initial_capital: float = 10000) -> pd.Series:
        """Calculate equity curve starting from initial capital"""
        if len(trades) == 0:
            return pd.Series([initial_capital])
        
        # Build equity curve: start with initial capital, then add each trade's PnL
        equity_values = [initial_capital]
        running_capital = initial_capital
        
        for pnl in trades["pnl"]:
            running_capital += pnl
            equity_values.append(running_capital)
        
        # Return as Series (first value is initial capital, rest track after each trade)
        return pd.Series(equity_values)
    
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
            **metrics
        )
        
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
