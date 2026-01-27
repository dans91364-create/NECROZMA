# MeanReverter Legacy Implementation Summary

## Problem
The MeanReverter strategy had a Sharpe ratio of **6.29** in Round 7 but now generates **0 trades** in Round 9. The issue was related to how the `threshold` parameter is handled.

## Solution
Created **MeanReverterLegacy** - an exact replica of the Round 7 version that worked perfectly.

## Changes Made

### 1. strategy_factory.py
- Added `MeanReverterLegacy` class (lines 186-234)
  - Uses `threshold` parameter directly (not `threshold_std`)
  - No division by zero protection (original behavior)
  - Checks only `mid_price` column (original behavior)
  - No `max_trades_per_day` limit (original behavior)
  
- Updated `StrategyFactory.template_classes` to include `MeanReverterLegacy`

- Updated parameter generation logic:
  - MeanReverterLegacy uses `threshold` from config
  - Same R/R ratio filter as MeanReverter (min 1.3)

### 2. config.py
- Added `MeanReverterLegacy` to `STRATEGY_TEMPLATES` (first in list)
- Added `MeanReverterLegacy` configuration to `STRATEGY_PARAMS`:
  ```python
  'MeanReverterLegacy': {
      'lookback_periods': [5],
      'threshold': [1.8, 2.0],           # Uses 'threshold' not 'threshold_std'
      'stop_loss_pips': [20, 30],
      'take_profit_pips': [40, 50],
  }
  ```
- Updated total strategy count: **52 strategies** (was 44)

### 3. test_strategy_fixes.py
- Added `test_meanreverter_legacy()` - validates parameter handling
- Added `test_meanreverter_legacy_vs_current()` - compares Legacy vs Current

## Strategy Breakdown

| Template | Combinations | Configuration |
|----------|-------------|---------------|
| **MeanReverterLegacy** | 8 | L5 × T1.8,2.0 × SL20,30 × TP40,50 |
| MeanReverter | 8 | L5 × T1.8,2.0 × SL20,30 × TP40,50 |
| MeanReverterV2 | 24 | L30 × T0.8,1.0,1.5 × ... |
| MeanReverterV3 | 12 | L5 × T1.7,1.8 × ... |
| **TOTAL** | **52** | |

## Key Differences: Legacy vs Current

| Feature | MeanReverterLegacy (Round 7) | MeanReverter (Round 9) |
|---------|----------------------------|----------------------|
| Parameter | `threshold` | `threshold_std` |
| Division by zero | None | Protected with EPSILON |
| Price columns | Only `mid_price` | Both `mid_price` and `close` |
| Max trades/day | None | None |

## Expected Results

When running backtesting (Round 10):

1. **MeanReverterLegacy**: Should reproduce Sharpe **~6.29** (same as Round 7)
   - Expected: **41 trades** with high Sharpe ratio
   
2. **MeanReverter**: May generate **0 trades** (confirms Round 9 bug)
   - This will help identify what exactly broke

3. **Comparison**: Will show exactly what parameter/code difference caused the issue

## How to Use

### Run Backtesting
```bash
# The existing backtesting scripts will automatically pick up the new strategies
python main.py
# or
python run_sequential_backtest.py
```

### Verify Strategy Generation
```bash
python -c "
from strategy_factory import StrategyFactory
factory = StrategyFactory()
strategies = factory.generate_strategies()
print(f'Total strategies: {len(strategies)}')
for s in strategies[:5]:
    print(f'  - {s.name}')
"
```

## Files Modified
1. `/home/runner/work/NECROZMA/NECROZMA/strategy_factory.py` - Added MeanReverterLegacy class
2. `/home/runner/work/NECROZMA/NECROZMA/config.py` - Added configuration
3. `/home/runner/work/NECROZMA/NECROZMA/test_strategy_fixes.py` - Added tests

## Validation
All validations passed:
- ✅ 52 strategies generated (8 + 8 + 24 + 12)
- ✅ MeanReverterLegacy uses `threshold` parameter
- ✅ MeanReverter uses `threshold_std` parameter
- ✅ All strategies can generate signals without errors

## Next Steps
1. Run backtesting on historical data
2. Compare results:
   - MeanReverterLegacy should show Sharpe ~6.29
   - MeanReverter may show 0 trades
3. Analyze differences to understand the root cause
4. Fix the current MeanReverter if needed
