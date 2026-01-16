# 🎯 Multi-Pair File Prefix Feature

## Overview

The ULTRA NECROZMA system now automatically adds a pair prefix (`{PAIR}_{YEAR}_`) to all output files. This prevents overwriting when running analysis on multiple currency pairs.

## 📋 Problem Solved

**Before:**
```
ultra_necrozma_results/
├── universes/
│   └── universe_1m_5lb.parquet     ❌ Gets overwritten!
├── reports/
│   └── LIGHT_REPORT_20260116.json  ❌ Gets overwritten!
└── cache/
    └── labels_abc123.pkl           ❌ Gets overwritten!
```

When you run EURUSD first, then GBPUSD, all EURUSD results are lost.

**After:**
```
ultra_necrozma_results/
├── universes/
│   ├── EURUSD_2025_universe_1m_5lb.parquet     ✅ Safe!
│   └── GBPUSD_2025_universe_1m_5lb.parquet     ✅ Safe!
├── reports/
│   ├── EURUSD_2025_LIGHT_REPORT.json           ✅ Safe!
│   └── GBPUSD_2025_LIGHT_REPORT.json           ✅ Safe!
└── cache/
    ├── EURUSD_2025_labels_abc123.pkl           ✅ Safe!
    └── GBPUSD_2025_labels_abc123.pkl           ✅ Safe!
```

Each pair has its own set of files!

## 🔧 How It Works

### 1. Automatic Prefix Extraction

The system automatically extracts the pair name and year from your `PARQUET_FILE` path:

```python
# config.py or config.yaml
PARQUET_FILE = "data/EURUSD_2025.parquet"

# Automatically extracted:
PAIR_NAME = "EURUSD"
DATA_YEAR = "2025"
FILE_PREFIX = "EURUSD_2025_"
```

### 2. Applied to All Output Files

The prefix is automatically added to:

#### Universes
- `{PREFIX}universe_1m_5lb.parquet`
- `{PREFIX}universe_1m_5lb_metadata.json`
- `{PREFIX}universe_5m_10lb.parquet`
- etc.

#### Reports
- `{PREFIX}LIGHT_REPORT_{timestamp}.json`
- `{PREFIX}rankings_{timestamp}.json`
- `{PREFIX}rankings.json`
- `{PREFIX}pattern_summary.json`
- `{PREFIX}top_strategies_ranked.json`

#### Backtest Results
- `{PREFIX}universe_1m_5lb_backtest.parquet`
- `{PREFIX}universe_1m_5lb_backtest_metadata.json`
- `{PREFIX}consolidated_backtest_results.json`
- `{PREFIX}top_strategies_ranked.json`

#### Cache Files
- `{PREFIX}labels_{hash}.pkl`
- `{PREFIX}labels_progress_{hash}.json`

#### Checkpoints
- `{PREFIX}checkpoint_{step}.json`

## 🚀 Usage

### Running Multiple Pairs

**1. Run EURUSD:**
```bash
# Edit config.yaml:
parquet_file: "data/EURUSD_2025.parquet"

# Run analysis
python main.py
```

**2. Run GBPUSD:**
```bash
# Edit config.yaml:
parquet_file: "data/GBPUSD_2025.parquet"

# Run analysis
python main.py
```

**3. Results:**
```
ultra_necrozma_results/
├── EURUSD_2025_universe_1m_5lb.parquet        ✅ EURUSD results preserved
├── EURUSD_2025_LIGHT_REPORT.json
├── GBPUSD_2025_universe_1m_5lb.parquet        ✅ GBPUSD results separate
└── GBPUSD_2025_LIGHT_REPORT.json
```

### File Naming Examples

For `EURUSD_2025.parquet`:
```
EURUSD_2025_universe_1m_5lb.parquet
EURUSD_2025_LIGHT_REPORT_20260116_120000.json
EURUSD_2025_labels_a1b2c3d4.pkl
EURUSD_2025_universe_1m_5lb_backtest.parquet
```

For `GBPUSD_2025.parquet`:
```
GBPUSD_2025_universe_1m_5lb.parquet
GBPUSD_2025_LIGHT_REPORT_20260116_120000.json
GBPUSD_2025_labels_e5f6g7h8.pkl
GBPUSD_2025_universe_1m_5lb_backtest.parquet
```

## 🧪 Testing

### Run Tests
```bash
# Run comprehensive tests
python tests/test_file_prefix.py

# Validate file structure
python validate_file_prefix.py
```

### Test Output
```
============================================================
🧪 Testing File Prefix Functionality
============================================================

✅ Extracted pair: EURUSD, year: 2025
✅ FILE_PREFIX format correct: EURUSD_2025_
✅ All filename formats correct with prefix
✅ Backward compatibility verified
✅ All modules can import FILE_PREFIX

============================================================
✅ All tests passed!
============================================================
```

## 🔄 Backward Compatibility

The system is backward compatible:

- If `PARQUET_FILE` doesn't follow the `{PAIR}_{YEAR}.parquet` pattern, it will still work
- Default values: `PAIR_NAME = "UNKNOWN"`, `DATA_YEAR = "2025"`
- Empty prefix would work but not recommended

## 📊 Complete File Structure

```
ultra_necrozma_results/
├── universes/
│   ├── EURUSD_2025_universe_1m_5lb.parquet
│   ├── EURUSD_2025_universe_1m_5lb_metadata.json
│   ├── EURUSD_2025_universe_5m_10lb.parquet
│   ├── EURUSD_2025_universe_5m_10lb_metadata.json
│   ├── GBPUSD_2025_universe_1m_5lb.parquet
│   └── GBPUSD_2025_universe_1m_5lb_metadata.json
│
├── reports/
│   ├── EURUSD_2025_LIGHT_REPORT_20260116_120000.json
│   ├── EURUSD_2025_rankings_20260116_120000.json
│   ├── EURUSD_2025_rankings.json
│   ├── EURUSD_2025_pattern_summary.json
│   ├── EURUSD_2025_top_strategies_ranked.json
│   ├── GBPUSD_2025_LIGHT_REPORT_20260116_130000.json
│   └── GBPUSD_2025_rankings.json
│
├── backtest_results/
│   ├── EURUSD_2025_universe_1m_5lb_backtest.parquet
│   ├── EURUSD_2025_universe_1m_5lb_backtest_metadata.json
│   ├── EURUSD_2025_consolidated_backtest_results.json
│   ├── EURUSD_2025_top_strategies_ranked.json
│   └── GBPUSD_2025_universe_1m_5lb_backtest.parquet
│
├── cache/
│   ├── EURUSD_2025_labels_a1b2c3d4.pkl
│   ├── EURUSD_2025_labels_progress_a1b2c3d4.json
│   ├── GBPUSD_2025_labels_e5f6g7h8.pkl
│   └── GBPUSD_2025_labels_progress_e5f6g7h8.json
│
└── checkpoints/
    ├── EURUSD_2025_checkpoint_1.json
    ├── EURUSD_2025_checkpoint_2.json
    └── GBPUSD_2025_checkpoint_1.json
```

## 🔍 Implementation Details

### Modified Files

1. **config.py**
   - Added `get_pair_info()` function to extract pair and year
   - Added `PAIR_NAME`, `DATA_YEAR`, and `FILE_PREFIX` variables

2. **analyzer.py**
   - Updated `_universe_exists()` to check with prefix
   - Updated `_save_universe_parquet()` to save with prefix
   - Updated `_load_universe_metadata()` to load with prefix
   - Updated `save_results()` for rankings and summaries
   - Updated `_save_checkpoint()` for checkpoint files

3. **labeler.py**
   - Updated cache file naming in `label_all_scenarios()`
   - `clear_label_cache()` handles both prefixed and non-prefixed files

4. **reports.py**
   - Updated `light_that_burns_the_sky()` to save rankings with prefix

5. **light_report.py**
   - Updated `save_report()` to save with prefix

6. **run_sequential_backtest.py**
   - Updated `save_universe_backtest_results()` to save with prefix
   - Updated `save_consolidated_results()` to save with prefix
   - Updated top strategies ranking to use prefix

## ✅ Benefits

1. **No Overwriting**: Run multiple pairs without losing results
2. **Clear Organization**: Easy to identify files by pair and year
3. **Automatic**: No manual configuration needed
4. **Consistent**: All output files follow the same naming convention
5. **Safe**: Preserves all results for future comparison
6. **Flexible**: Works with any pair name and year combination

## 🎯 Example Workflow

```bash
# Analyze EURUSD 2025
parquet_file: "data/EURUSD_2025.parquet"
python main.py
# Creates: EURUSD_2025_*.parquet, EURUSD_2025_*.json

# Analyze GBPUSD 2025
parquet_file: "data/GBPUSD_2025.parquet"
python main.py
# Creates: GBPUSD_2025_*.parquet, GBPUSD_2025_*.json

# Analyze EURUSD 2024 (different year)
parquet_file: "data/EURUSD_2024.parquet"
python main.py
# Creates: EURUSD_2024_*.parquet, EURUSD_2024_*.json

# All results preserved and organized!
```

## 📚 Related Files

- `config.py` - Main configuration with prefix logic
- `tests/test_file_prefix.py` - Comprehensive test suite
- `validate_file_prefix.py` - Validation and demonstration script
