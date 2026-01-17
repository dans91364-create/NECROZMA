# LightFinder DataFrame Support - Usage Guide

## Overview

`light_finder.py` now supports **both** input formats:
1. **List[BacktestResults]** objects (legacy format)
2. **pd.DataFrame** (new batch processing format)

This allows seamless integration with the batch processing system (`backtest_batch.py`) while maintaining backward compatibility.

## Quick Start

### Using with DataFrame (Batch Processing Format)

```python
import pandas as pd
from light_finder import LightFinder

# Load batch results from parquet file
results_df = pd.read_parquet('ultra_necrozma_results/EURUSD_2025_backtest_results_merged.parquet')

# Initialize LightFinder
finder = LightFinder()

# Rank strategies
top_strategies = finder.rank_strategies(results_df, top_n=10)

# Get top strategies by specific metric
top_sharpe = finder.get_top_strategies_by_metric(results_df, metric='sharpe_ratio', top_n=5)
```

### Using with BacktestResults Objects (Legacy Format)

```python
from backtester import Backtester, BacktestResults
from light_finder import LightFinder

# Run backtests (returns List[BacktestResults])
backtester = Backtester(df, initial_capital=10000)
results = []
for strategy in strategies:
    result = backtester.run(strategy)
    results.append(result)

# Initialize LightFinder
finder = LightFinder()

# Rank strategies (works exactly as before)
top_strategies = finder.rank_strategies(results, top_n=10)

# Get top strategies by specific metric
top_sharpe = finder.get_top_strategies_by_metric(results, metric='sharpe_ratio', top_n=5)
```

## DataFrame Format Requirements

The DataFrame should have these columns:
- `strategy_name` (required)
- `total_return` (required)
- `sharpe_ratio` (required)
- `sortino_ratio` (required)
- `max_drawdown` (required)
- `win_rate` (required)
- `n_trades` (required)
- `profit_factor` (required)
- `ulcer_index` (optional - defaults to 5.0 if missing)
- `lot_size` (optional - if present, best lot_size per strategy is selected)

Additional columns are ignored but can be included (e.g., `gross_pnl`, `net_pnl`, `total_commission`).

## Handling Multiple Lot Sizes

If your DataFrame contains multiple results per strategy (e.g., different lot sizes), LightFinder will automatically:
1. Group by `strategy_name`
2. Select the row with the **highest `total_return`** for each strategy
3. Use that row for scoring and ranking

```python
# DataFrame with multiple lot_sizes per strategy
df = pd.DataFrame({
    'strategy_name': ['Strategy_A', 'Strategy_A', 'Strategy_A', 'Strategy_B', 'Strategy_B', 'Strategy_B'],
    'lot_size': [0.01, 0.1, 1.0, 0.01, 0.1, 1.0],
    'total_return': [0.25, 0.30, 0.28, 0.20, 0.22, 0.21],
    # ... other columns
})

# LightFinder will select lot_size=0.1 for Strategy_A (highest return: 0.30)
# and lot_size=0.1 for Strategy_B (highest return: 0.22)
ranked = finder.rank_strategies(df, top_n=10)
```

## Missing ulcer_index Column

If the DataFrame doesn't have the `ulcer_index` column (common in batch processing), LightFinder will:
- Use a default value of **5.0** for all strategies
- Continue with scoring normally
- This ensures compatibility with batch results that don't include this metric

## Example: Integration with Batch Processing

```python
import pandas as pd
from pathlib import Path
from light_finder import LightFinder

# Step 1: Load batch processing results
results_dir = Path('ultra_necrozma_results')
results_file = results_dir / 'EURUSD_2025_backtest_results_merged.parquet'

# Load the DataFrame
print(f"Loading results from: {results_file}")
df = pd.read_parquet(results_file)

print(f"Loaded {len(df)} results")
print(f"Unique strategies: {df['strategy_name'].nunique()}")
print(f"Lot sizes: {df['lot_size'].unique()}")

# Step 2: Initialize LightFinder
finder = LightFinder()

# Step 3: Rank strategies
print("\nRanking strategies...")
top_10 = finder.rank_strategies(df, top_n=10)

# Step 4: Display results
print("\nTop 10 Strategies:")
for _, row in top_10.iterrows():
    print(f"  #{row['rank']} {row['strategy_name']}")
    print(f"     Score: {row['composite_score']:.3f}")
    print(f"     Return: {row['total_return']:.1%}, Sharpe: {row['sharpe_ratio']:.2f}")

# Step 5: Get top strategies by specific metrics
print("\nTop 5 by Sharpe Ratio:")
top_sharpe = finder.get_top_strategies_by_metric(df, metric='sharpe_ratio', top_n=5)
for _, row in top_sharpe.iterrows():
    print(f"  {row['strategy_name']}: Sharpe={row['sharpe_ratio']:.2f}")
```

## API Compatibility

Both `rank_strategies()` and `get_top_strategies_by_metric()` accept either format:

| Method | Input Type | Return Type |
|--------|-----------|-------------|
| `rank_strategies(List[BacktestResults])` | List | DataFrame |
| `rank_strategies(DataFrame)` | DataFrame | DataFrame |
| `get_top_strategies_by_metric(List[BacktestResults])` | List | List |
| `get_top_strategies_by_metric(DataFrame)` | DataFrame | DataFrame |

## Migration Guide

No code changes needed! The API is backward compatible:

**Before (still works):**
```python
from light_finder import LightFinder
finder = LightFinder()
ranked = finder.rank_strategies(backtest_results_list, top_n=10)
```

**After (also works):**
```python
from light_finder import LightFinder
finder = LightFinder()
ranked = finder.rank_strategies(results_dataframe, top_n=10)
```

## Testing

Run the test suite to verify functionality:
```bash
# Run unit tests
pytest tests/test_light_finder.py -v

# Run integration test
python test_light_finder_dataframe.py
```

All 11 tests should pass. ✅
