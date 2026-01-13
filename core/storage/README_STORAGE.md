# 🗄️ Smart Storage System

## Overview

The Smart Storage System implements a 2-tier architecture to efficiently store backtest results:

- **Tier 1 (Metrics)**: ALL strategies, metrics only (~50 MB for 10,000 strategies)
- **Tier 2 (Detailed Trades)**: TOP 50 strategies per universe with full trade data (~2-5 GB total)

## Why This Approach?

| Traditional | Smart Storage |
|------------|---------------|
| 115 GB for 25 universes | ~5 GB total |
| Dashboard loads 4.6 GB | Dashboard loads 50 MB |
| Can't version control | Can version metrics |
| Slow to analyze | Fast metric scanning |

## Usage

### Saving Results

```python
from core.storage.smart_storage import SmartBacktestStorage

storage = SmartBacktestStorage()

# After backtesting a universe
storage.save_universe_results(
    universe_name="universe_001_5min_5lb",
    results=all_strategy_results,
    top_n=50  # Save detailed trades for top 50
)
```

### Loading in Dashboard

```python
from dashboard.utils.data_loader import (
    load_all_strategies_metrics,  # Fast: loads all metrics
    load_strategy_detailed_trades  # On-demand: loads 1 strategy's trades
)

# Load all metrics (fast)
df = load_all_strategies_metrics()  # 50 MB

# Load specific strategy trades (on-demand)
trades = load_strategy_detailed_trades("MeanReverter_L5_T0.5_SL10_TP50")  # 50 MB
```

## File Structure

```
ultra_necrozma_results/backtest_results/
├── all_strategies_metrics.json          # 50 MB - ALL strategies
│   {
│     "total_strategies": 10000,
│     "strategies": [
│       {
│         "strategy_name": "MeanReverter_L5_T0.5_SL10_TP50",
│         "universe": "universe_001_5min_5lb",
│         "metrics": {
│           "sharpe_ratio": 1.54,
│           "total_return": 0.846,
│           "win_rate": 0.648,
│           ...  // 30+ metrics
│         }
│       }
│     ]
│   }
│
└── detailed_trades/                     # ~2-5 GB total
    ├── MeanReverter_L5_T0.5_SL10_TP50.json    (50 MB)
    │   {
    │     "strategy_name": "...",
    │     "universe": "universe_001_5min_5lb",
    │     "rank": 1,
    │     "metrics": {...},
    │     "trades": [14040 trades with full details],
    │     "equity_curve": [...],
    │     "drawdown_curve": [...]
    │   }
    └── ...  (50 files max per universe)
```

## Benefits

1. **Scalability**: Works with 100+ universes (25 GB vs 500+ GB)
2. **Performance**: Dashboard loads in 2s instead of 30s+
3. **Git-friendly**: Metrics file can be versioned
4. **Flexibility**: Still have full trade data for top performers
5. **Analysis**: Quick scanning of all strategies without loading trades

## Configuration

Adjust `top_n` parameter to save more/fewer detailed strategies:

```python
storage.save_universe_results(results, top_n=100)  # Top 100 instead of 50
```

## Migration from Old Format

Old universe JSON files (`universe_001_5min_5lb_backtest.json`) can coexist with the new format. The dashboard data loader has been updated to support both formats for backward compatibility.
