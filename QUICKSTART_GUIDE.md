# 🐉 NECROZMA ULTIMATE - Quick Start Guide

Welcome to NECROZMA ULTIMATE with **288 strategy templates**!

## 🚀 Quick Start

### 1. Check Available Templates

```python
from strategy_factory import StrategyFactory

factory = StrategyFactory()
print(f"Total templates: {len(factory.template_classes)}")
print(f"Sample templates: {list(factory.template_classes.keys())[:10]}")
```

### 2. Use a Specific Template

```python
from strategy_templates.trend.moving_average import SMAStrategy
from strategy_templates.mean_reversion.rsi import RSIClassic
from strategy_templates.candlestick.single_candle import HammerStrategy
import pandas as pd

# Create strategy instance
strategy = RSIClassic({
    'period': 14,
    'overbought': 70,
    'oversold': 30
})

# Generate signals (1=buy, -1=sell, 0=hold)
signals = strategy.generate_signals(df)
```

### 3. Generate All Strategy Variants

```python
from strategy_factory import StrategyFactory

factory = StrategyFactory()
strategies = factory.generate_strategies()

print(f"Generated {len(strategies)} strategy variants")
for strategy in strategies[:5]:
    print(f"  - {strategy.name}")
```

### 4. Run Backtests with --vast-mode

```bash
# Generate base strategies (creates strategy configurations)
python main.py --vast-mode --input-dir data/parquet/ --generate-base

# Run light search (fast backtesting across templates)
python main.py --vast-mode --input-dir data/parquet/ --search-light

# Run deep search (comprehensive parameter optimization)
python main.py --vast-mode --input-dir data/parquet/ --search-deep
```

## 📁 Template Categories

### Trend Following (24 templates)
```python
from strategy_templates.trend.moving_average import SMAStrategy, EMAStrategy
from strategy_templates.trend.macd import MACDClassic, MACDHistogram
from strategy_templates.trend.ichimoku import IchimokuCloud
```

### Mean Reversion (28 templates)
```python
from strategy_templates.mean_reversion.rsi import RSIClassic, RSIDivergence
from strategy_templates.mean_reversion.bollinger import BollingerBounce, BollingerSqueeze
from strategy_templates.mean_reversion.stochastic import StochasticFast
```

### Momentum (22 templates)
```python
from strategy_templates.momentum.roc import ROCStrategy
from strategy_templates.momentum.elder_impulse import ElderImpulse
from strategy_templates.momentum.squeeze_momentum import SqueezeMomentum
```

### Volatility (24 templates)
```python
from strategy_templates.volatility.atr import ATRBreakout, ATRTrailing
from strategy_templates.volatility.range_strategies import NR7Strategy
from strategy_templates.volatility.bollinger_bandwidth import BollingerBandwidth
```

### Volume (20 templates)
```python
from strategy_templates.volume.obv import OBVStrategy
from strategy_templates.volume.vwap import VWAPStrategy
from strategy_templates.volume.chaikin import ChaikinMoneyFlow
```

### Candlestick Patterns (41 templates)
```python
from strategy_templates.candlestick.single_candle import DojiStrategy, HammerStrategy
from strategy_templates.candlestick.double_candle import BullishEngulfing
from strategy_templates.candlestick.triple_candle import MorningStar
```

### Chart Patterns (29 templates)
```python
from strategy_templates.chart_patterns.head_shoulders import HeadShoulders
from strategy_templates.chart_patterns.double_triple import DoubleTop
from strategy_templates.chart_patterns.triangles import AscendingTriangle
```

### Fibonacci/Harmonic (14 templates)
```python
from strategy_templates.fibonacci.retracement import FibRetracement618
from strategy_templates.fibonacci.harmonic_gartley import GartleyPattern
from strategy_templates.fibonacci.abcd_pattern import ABCDPattern
```

### Time-Based (13 templates)
```python
from strategy_templates.time_based.session_breakout import LondonOpenBreakout
from strategy_templates.time_based.day_of_week import DayOfWeekEffect
from strategy_templates.time_based.news_trading import NFPStrategy
```

### Multi-Pair/Correlation (25 templates)
```python
from strategy_templates.multi_pair.correlation import CorrelationTrader
from strategy_templates.multi_pair.currency_strength import CurrencyStrength
from strategy_templates.multi_pair.carry_trade import CarryTrade
```

### Smart Money Concepts (32 templates)
```python
from strategy_templates.smc.order_blocks import OrderBlocks
from strategy_templates.smc.fair_value_gap import FairValueGap
from strategy_templates.smc.liquidity import LiquidityPools
from strategy_templates.smc.wyckoff import WyckoffMethod
```

### Statistical/Quantitative (19 templates)
```python
from strategy_templates.statistical.kalman_filter import KalmanFilterTrend
from strategy_templates.statistical.regime_detection import HiddenMarkovRegime
from strategy_templates.statistical.garch import GARCHVolatility
```

### Exotic/Alternative (27 templates)
```python
from strategy_templates.exotic.renko import RenkoStrategy
from strategy_templates.exotic.heikin_ashi import HeikinAshiStrategy
from strategy_templates.exotic.market_profile import MarketProfileTPO
```

### Risk Management (13 templates)
```python
from strategy_templates.risk_management.position_sizing import KellyOptimal
from strategy_templates.risk_management.stop_strategies import ATRStopStrategy
from strategy_templates.risk_management.exit_strategies import ProfitTargetScale
```

## 🎯 Strategy Customization

### Create Custom Parameters

```python
from strategy_templates.trend.moving_average import SMAStrategy

# Customize parameters
custom_params = {
    'fast_period': 10,
    'slow_period': 50,
    'signal_period': 9
}

strategy = SMAStrategy(custom_params)
```

### Modify Existing Template

```python
from strategy_templates.mean_reversion.rsi import RSIClassic

class MyCustomRSI(RSIClassic):
    def __init__(self, params):
        super().__init__(params)
        # Add custom logic
        
    def generate_signals(self, df):
        # Override signal generation
        signals = super().generate_signals(df)
        # Add custom filters
        return signals
```

## 📊 Backtesting Examples

### Single Strategy Backtest

```python
from backtester import Backtester
from strategy_templates.trend.moving_average import SMAStrategy

strategy = SMAStrategy({'fast_period': 10, 'slow_period': 50})
backtester = Backtester(strategy)
results = backtester.run(df)

print(f"Sharpe Ratio: {results['sharpe']:.2f}")
print(f"Total Return: {results['total_return']:.2%}")
print(f"Win Rate: {results['win_rate']:.2%}")
```

### Multi-Strategy Comparison

```python
from strategy_factory import StrategyFactory
from backtester import Backtester

factory = StrategyFactory()
strategies = factory.generate_strategies()

results = []
for strategy in strategies:
    backtester = Backtester(strategy)
    result = backtester.run(df)
    results.append({
        'name': strategy.name,
        'sharpe': result['sharpe'],
        'return': result['total_return']
    })

# Sort by Sharpe ratio
results.sort(key=lambda x: x['sharpe'], reverse=True)
print("Top 10 Strategies:")
for i, r in enumerate(results[:10], 1):
    print(f"{i}. {r['name']}: Sharpe={r['sharpe']:.2f}, Return={r['return']:.2%}")
```

## 🔧 Advanced Usage

### Template Discovery

```python
from strategy_factory import StrategyFactory

factory = StrategyFactory()

# Find all trend templates
trend_templates = [k for k in factory.template_classes.keys() 
                   if any(x in k for x in ['SMA', 'EMA', 'MACD', 'Trend'])]
print(f"Found {len(trend_templates)} trend templates")

# Find all candlestick patterns
candle_templates = [k for k in factory.template_classes.keys() 
                    if any(x in k for x in ['Doji', 'Hammer', 'Engulfing', 'Star'])]
print(f"Found {len(candle_templates)} candlestick templates")
```

### Parameter Grid Search

```python
from itertools import product
from strategy_templates.mean_reversion.rsi import RSIClassic

# Define parameter grid
periods = [7, 14, 21]
overbought = [70, 75, 80]
oversold = [20, 25, 30]

# Test all combinations
best_sharpe = -999
best_params = None

for p, ob, os in product(periods, overbought, oversold):
    strategy = RSIClassic({
        'period': p,
        'overbought': ob,
        'oversold': os
    })
    result = backtester.run(df, strategy)
    
    if result['sharpe'] > best_sharpe:
        best_sharpe = result['sharpe']
        best_params = (p, ob, os)

print(f"Best params: period={best_params[0]}, OB={best_params[1]}, OS={best_params[2]}")
print(f"Best Sharpe: {best_sharpe:.2f}")
```

## 🎓 Template Implementation Guide

### Creating Your Own Template

```python
from strategy_templates.base import Strategy
import pandas as pd

class MyCustomStrategy(Strategy):
    """
    My custom trading strategy
    
    Logic: [Explain your entry/exit logic]
    Best for: [Market conditions]
    """
    
    def __init__(self, params):
        super().__init__("MyCustom", params)
        self.period = params.get("period", 20)
        self.threshold = params.get("threshold", 2.0)
        
        self.rules = [
            {"type": "entry_long", "condition": "Your condition"},
            {"type": "entry_short", "condition": "Your condition"},
            {"type": "exit", "condition": "Your exit condition"},
        ]
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate trading signals: 1=buy, -1=sell, 0=hold"""
        signals = pd.Series(0, index=df.index)
        
        # Calculate your indicators
        ma = df['close'].rolling(self.period).mean()
        std = df['close'].rolling(self.period).std()
        
        # Generate signals
        signals[df['close'] < ma - self.threshold * std] = 1  # Buy
        signals[df['close'] > ma + self.threshold * std] = -1  # Sell
        
        return signals
```

### Register Custom Template

```python
# In strategy_factory.py, add to template_classes:
from my_module import MyCustomStrategy

self.template_classes['MyCustomStrategy'] = MyCustomStrategy
```

## 📚 Additional Resources

- **Full Documentation**: See `STRATEGY_TEMPLATE_IMPLEMENTATION.md`
- **Template Report**: See `TEMPLATE_COUNT_REPORT.md`
- **Distribution**: See `TEMPLATE_DISTRIBUTION.txt`

## 🐉 The NECROZMA Creed

*"O universo é grande e NECROZMA quer percorrer todo ele em busca da luz"*

**288 TEMPLATES × 30 PAIRS × 20 PARAMS = 172,800 PATHS TO THE LIGHT** 🌟✨

---

**Happy Trading with NECROZMA ULTIMATE!** 🚀
