# Timestamp and Cache Features

This document describes the timestamp-based file naming and cache management features implemented to solve the following problems:

## Problems Solved

### 1. Results Being Overwritten
Previously, running multiple backtest rounds would overwrite the final results (`*_backtest_results_merged.parquet`), losing valuable data for training AI in the future.

**Solution**: Added timestamp to `FILE_PREFIX` so each run generates unique result files.

### 2. Pattern Mining Without Cache
Step 3 (Pattern Mining) always recalculated from scratch, even when data didn't change.

**Solution**: Added cache system for pattern mining results with automatic load/save.

### 3. Manual Cache Cleanup
When strategy parameters changed in `config.py`, users had to manually delete backtest cache files.

**Solution**: Added `--clean-strategy-cache` command to delete strategy-related caches while preserving important data.

---

## Features

### 1. Timestamp-Based File Prefix (`config.py`)

Two file prefixes are now available:

#### `FILE_PREFIX_STABLE` (without timestamp)
- Used for **reusable caches** that don't change between runs
- Format: `PAIR_NAME_DATA_YEAR_` (e.g., `EURUSD_2025_`)
- Used for:
  - `regimes.parquet` - Market regime detection results
  - `patterns.json` - Pattern mining results
  - `labels/` - Label cache files

#### `FILE_PREFIX` (with timestamp)
- Used for **unique results** specific to each run
- Format: `PAIR_NAME_DATA_YEAR_YYYYMMDD_HHMMSS_` (e.g., `EURUSD_2025_20260118_143052_`)
- Used for:
  - `backtest_results_merged.parquet` - Final backtest results
  - `rankings.parquet` - Strategy rankings
  - `LIGHT_REPORT_*.json` - Final reports

**Example**:
```python
from config import FILE_PREFIX, FILE_PREFIX_STABLE

# Cache files (reusable)
regimes_path = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}regimes.parquet"
patterns_path = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}patterns.json"

# Result files (unique per run)
results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
report_path = OUTPUT_DIR / f"{FILE_PREFIX}LIGHT_REPORT.json"
```

### 2. Pattern Mining Cache (`main.py` - Step 3)

Pattern mining results are now cached to avoid recalculation:

```python
from config import FILE_PREFIX_STABLE, OUTPUT_DIR
import json

patterns_cache_path = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}patterns.json"

if patterns_cache_path.exists():
    # Load from cache
    with open(patterns_cache_path, 'r') as f:
        patterns = json.load(f)
    print("✅ Loaded patterns from cache")
else:
    # Calculate and save
    miner = PatternMiner()
    patterns = miner.discover_patterns(df, labels_dict)
    
    with open(patterns_cache_path, 'w') as f:
        json.dump(patterns, f, indent=2, default=str)
    print("💾 Patterns saved to cache")
```

**Benefits**:
- Saves computation time on subsequent runs
- Uses `FILE_PREFIX_STABLE` so cache is reused across runs
- Automatic cache invalidation when data changes (different pair/year)

### 3. Clean Strategy Cache Command

New command-line argument to clean strategy-related caches:

```bash
python main.py --clean-strategy-cache
```

#### What Gets Deleted:
- `batch_results/` directory (Step 5 intermediate files)
- `*_rankings*` files (Step 6 rankings)
- `*_LIGHT_REPORT_*.json` files (Step 7 reports)

#### What Gets Preserved:
- `labels/` directory (Step 1 label data)
- `cache/labels_*.pkl` (Step 1 cache)
- `*regimes.parquet` (Step 2 regime detection)
- `*patterns.json` (Step 3 pattern cache)
- `universes/` (original analysis data)
- `*_backtest_results_merged.parquet` (FINAL RESULTS - valuable for ML training)

**Example**:
```bash
# Clean strategy cache before running with new parameters
python main.py --clean-strategy-cache --strategy-discovery --batch-mode
```

---

## Usage Examples

### Example 1: Multiple Runs Without Overwriting

```bash
# First run
python main.py --strategy-discovery --batch-mode
# Creates: EURUSD_2025_20260118_143052_backtest_results_merged.parquet

# Second run (different parameters)
python main.py --strategy-discovery --batch-mode
# Creates: EURUSD_2025_20260118_145233_backtest_results_merged.parquet

# Both result files exist!
ls ultra_necrozma_results/*_backtest_results_merged.parquet
```

### Example 2: Using Pattern Cache

```bash
# First run - calculates patterns
python main.py --strategy-discovery --batch-mode
# Output: "🔄 Running pattern mining..."
#         "💾 Patterns saved to: EURUSD_2025_patterns.json"

# Second run - loads from cache
python main.py --strategy-discovery --batch-mode
# Output: "✅ Loading saved patterns from cache..."
#         "   Loaded in 0.1s"
```

### Example 3: Cleaning Strategy Cache

```bash
# Change strategy parameters in config.py
# Clean old strategy caches
python main.py --clean-strategy-cache

# Output:
# 🗑️  Cleaning strategy cache...
#    ✅ Deleted: batch_results/
#    ✅ Deleted: EURUSD_2025_rankings.parquet
#    ✅ Deleted: EURUSD_2025_LIGHT_REPORT_20260118.json
#    🧹 Cleaned 3 items
#    ✅ Labels, regimes, patterns, and merged results preserved
```

### Example 4: Complete Workflow

```bash
# 1. First run with default parameters
python main.py --strategy-discovery --batch-mode
# Creates timestamped results, caches patterns and regimes

# 2. Change strategy parameters in config.py
# Edit: STRATEGY_PARAMS = {...}

# 3. Clean strategy cache (keeps patterns/regimes)
python main.py --clean-strategy-cache

# 4. Run again with new parameters
python main.py --strategy-discovery --batch-mode
# Reuses pattern/regime cache, creates new timestamped results

# 5. Compare results from both runs
ls ultra_necrozma_results/*_backtest_results_merged.parquet
```

---

## Testing

Run the comprehensive test suite:

```bash
python test_timestamp_and_cache.py
```

Tests cover:
1. ✅ FILE_PREFIX includes timestamp and is unique
2. ✅ FILE_PREFIX_STABLE is constant
3. ✅ Pattern cache works correctly
4. ✅ Clean strategy cache deletes correct files
5. ✅ Integration scenario (multiple runs)

---

## File Structure

After multiple runs with cache:

```
ultra_necrozma_results/
├── EURUSD_2025_regimes.parquet           # Stable cache
├── EURUSD_2025_patterns.json             # Stable cache
├── labels/                                # Stable cache
│   └── *.pkl
├── EURUSD_2025_20260118_143052_backtest_results_merged.parquet  # Run 1
├── EURUSD_2025_20260118_143052_LIGHT_REPORT.json                # Run 1
├── EURUSD_2025_20260118_145233_backtest_results_merged.parquet  # Run 2
└── EURUSD_2025_20260118_145233_LIGHT_REPORT.json                # Run 2
```

---

## Benefits

### 1. No More Lost Results
- Each run creates uniquely named result files
- Perfect for comparing different parameter configurations
- Valuable historical data for ML training

### 2. Faster Iterations
- Pattern mining cache saves significant computation time
- Regime detection cache reused across runs
- Focus on testing strategies, not recalculating features

### 3. Easy Cleanup
- One command to clean strategy caches
- Important data automatically preserved
- No manual file deletion needed

### 4. Better Organization
- Clear separation between cache and results
- Timestamp in filename shows when run was executed
- Easy to identify latest results

---

## Implementation Details

### config.py Changes

```python
from datetime import datetime

# Generate timestamp for unique run identification
_run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Stable prefix for reusable caches
FILE_PREFIX_STABLE = f"{PAIR_NAME}_{DATA_YEAR}_"

# Unique prefix for run-specific results
FILE_PREFIX = f"{PAIR_NAME}_{DATA_YEAR}_{_run_timestamp}_"
```

### main.py Changes

1. **Pattern cache in Step 3**:
   - Check if `{FILE_PREFIX_STABLE}patterns.json` exists
   - Load from cache or calculate and save

2. **Regime cache updated**:
   - Changed to use `FILE_PREFIX_STABLE` instead of `FILE_PREFIX`

3. **New argument**:
   - Added `--clean-strategy-cache` to argument parser

4. **New function**:
   - `clean_strategy_cache()` - deletes strategy-related files

5. **Integration**:
   - Clean function called before banner if flag is set

---

## Future Enhancements

Potential future improvements:

1. **Cache Versioning**: Add version check to invalidate cache when code changes
2. **Automatic Cleanup**: Auto-delete old results after N runs
3. **Cache Statistics**: Show cache hit/miss rates and time saved
4. **Selective Cache**: Allow caching specific pattern mining methods
5. **Result Comparison**: Tool to compare results from different runs

---

## Troubleshooting

### Problem: Pattern cache not being used

**Solution**: 
- Check that `FILE_PREFIX_STABLE` matches between runs
- Verify `PAIR_NAME` and `DATA_YEAR` haven't changed
- Delete cache and regenerate: `rm ultra_necrozma_results/*patterns.json`

### Problem: Clean command deletes too much

**Solution**:
- Review what clean_strategy_cache() deletes (see source code)
- Important files are preserved by design
- If in doubt, backup `ultra_necrozma_results/` first

### Problem: Timestamp not showing in filenames

**Solution**:
- Verify you're using `FILE_PREFIX` for result files
- Check config loads correctly: `python -c "from config import FILE_PREFIX; print(FILE_PREFIX)"`
- Timestamp is generated once when config loads

---

## Summary

These features provide:
- ✅ **Unique result files** - never overwrite previous runs
- ✅ **Smart caching** - reuse expensive computations
- ✅ **Easy cleanup** - one command to reset strategy caches
- ✅ **Data preservation** - important files never deleted
- ✅ **Better workflow** - iterate faster on strategy parameters

For questions or issues, refer to the test file `test_timestamp_and_cache.py` for usage examples.
