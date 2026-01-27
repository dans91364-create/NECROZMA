# run_mass_test.py - Mass Testing System with Resume Support

## Overview

The `run_mass_test.py` script has been completely rewritten to address critical issues with the previous implementation:

### Problems Fixed

1. **❌ No Subprocess Isolation** - Previously imported and called `main()` directly, which:
   - Didn't pass `--strategy-discovery` and `--batch-mode` flags
   - Caused shared state issues between tests
   - Made it impossible to properly isolate test runs

2. **❌ No Resume Capability** - If the script crashed or was interrupted:
   - All progress was lost
   - Had to restart from the beginning
   - Wasted hours/days of computation

3. **❌ Poor Error Handling** - Any error would stop the entire batch

### New Implementation

The new implementation uses:

1. **✅ Subprocess Execution (NO TIMEOUT)**
   ```python
   subprocess.run([
       sys.executable,
       "main.py",
       "--strategy-discovery",
       "--batch-mode",
       "--parquet", str(parquet_file)
   ])  # NO timeout - runs until completion
   ```

2. **✅ Robust Progress Tracking**
   - Progress saved to `results/mass_test/progress.json`
   - Each completed dataset is marked
   - Failed datasets tracked separately
   - Automatic resume on restart

3. **✅ New CLI Arguments**
   - `--status` - Show current progress
   - `--fresh` - Start from scratch (ignore previous progress)
   - `--retry-failed` - Retry only failed datasets
   - Kept: `--pair`, `--year`, `--list`

4. **✅ Better Error Handling**
   - Continues to next dataset if one fails
   - Ctrl+C safely saves progress
   - Detailed error logging

## Usage

### Basic Usage

```bash
# Run all pairs/years (auto-resume if interrupted)
python run_mass_test.py

# Test specific pair
python run_mass_test.py --pair EURUSD

# Test specific year
python run_mass_test.py --year 2024

# Test specific pairs and years
python run_mass_test.py --pair EURUSD GBPUSD --year 2023 2024
```

### Progress Management

```bash
# Check current progress
python run_mass_test.py --status

# Start fresh (ignore previous progress)
python run_mass_test.py --fresh

# Retry only failed datasets
python run_mass_test.py --retry-failed

# List available datasets
python run_mass_test.py --list
```

## How It Works

### 1. Dataset Discovery

Scans `data/parquet/` for files matching pattern `{PAIR}_{YEAR}.parquet`:
- EURUSD_2024.parquet → pair=EURUSD, year=2024
- GBPUSD_2023.parquet → pair=GBPUSD, year=2023

### 2. Progress Tracking

The script maintains a `progress.json` file with:

```json
{
  "completed": ["EURUSD_2024", "GBPUSD_2023"],
  "failed": ["USDJPY_2025"],
  "in_progress": "EURJPY_2024",
  "started_at": "2024-01-27T10:30:00",
  "last_update": "2024-01-27T15:45:00",
  "results": {
    "EURUSD_2024": {
      "status": "success",
      "best_sharpe": 2.45,
      "elapsed_time": 3600,
      "...": "..."
    }
  },
  "errors": {
    "USDJPY_2025": "File not found"
  }
}
```

### 3. Sequential Execution

For each dataset:
1. Mark as "in_progress"
2. Run subprocess with `--strategy-discovery --batch-mode --parquet <file>`
3. Wait for completion (NO timeout)
4. Parse results from report file
5. Mark as "completed" or "failed"
6. Save progress

### 4. Safe Interruption

Press `Ctrl+C` at any time:
- Current progress is saved
- Can resume by running the script again
- Skips already completed datasets

## Progress Output

### During Execution

```
======================================================================
⚡🌟💎 NECROZMA MASS TESTING SYSTEM 💎🌟⚡
        WITH RESUME SUPPORT (NO TIMEOUT)
======================================================================

📊 Datasets to process: 3
   • EURUSD 2024: data/parquet/EURUSD_2024.parquet
   • GBPUSD 2023: data/parquet/GBPUSD_2023.parquet
   • USDJPY 2025: data/parquet/USDJPY_2025.parquet

🚀 Starting mass test (3 datasets)...
   Press Ctrl+C to pause (progress is saved automatically)

──────────────────────────────────────────────────────────────────────
📌 Progress: 1/3 (33.3%)
──────────────────────────────────────────────────────────────────────

======================================================================
🚀 Testing EURUSD 2024
   File: data/parquet/EURUSD_2024.parquet
   Started: 2024-01-27 10:30:00
======================================================================
   Command: /usr/bin/python3 main.py --strategy-discovery --batch-mode --parquet data/parquet/EURUSD_2024.parquet
   Running... (NO TIMEOUT - will complete fully)
   ✅ Completed in 2.5h
   📄 Report: EURUSD_2024_LIGHT_REPORT_20240127_133000.json
   ✅ EURUSD_2024: Best Sharpe = 2.45
```

### Status Check

```bash
$ python run_mass_test.py --status

======================================================================
📊 MASS TEST PROGRESS STATUS
======================================================================

📈 Overall Progress:
   Total datasets:    10
   ✅ Completed:      6 (60.0%)
   ❌ Failed:         1
   ⏳ Remaining:      3

⏱️  Started: 2024-01-27T10:30:00
   Last update: 2024-01-27T15:45:00
   🔄 In progress: EURJPY_2024

✅ Completed (6):
   • EURUSD_2024: Sharpe 2.45, Time 2.5h
   • GBPUSD_2023: Sharpe 1.89, Time 3.2h
   • AUDJPY_2024: Sharpe 2.01, Time 2.8h
   ...

❌ Failed (1):
   • USDJPY_2025: File not found

⏳ Next up:
   • EURJPY_2025
   • USDCAD_2024
```

## Final Reports

After completion, the script generates:

### 1. JSON Report
`results/mass_test/mass_test_report_20240127_153000.json`
- Complete results for all datasets
- Detailed error information
- Full progress history

### 2. CSV Summary
`results/mass_test/mass_test_summary_20240127_153000.csv`

| pair_year    | pair   | year | status  | best_strategy      | best_sharpe | avg_sharpe | total_strategies | elapsed_time |
|--------------|--------|------|---------|--------------------| ------------|------------|------------------|--------------|
| EURUSD_2024  | EURUSD | 2024 | success | MomentumBurst_250  | 2.45        | 1.82       | 247              | 2.5h         |
| GBPUSD_2023  | GBPUSD | 2023 | success | MeanReverter_150   | 1.89        | 1.45       | 189              | 3.2h         |

### 3. Console Summary

```
======================================================================
🏁 MASS TEST COMPLETE!
======================================================================

📊 FINAL RESULTS (9 datasets)
──────────────────────────────────────────────────────────────────────

🏆 Top 10 by Sharpe Ratio:
    1. EURUSD_2024: Sharpe 2.45 - MomentumBurst_250
    2. AUDJPY_2024: Sharpe 2.01 - TrendFollower_500
    3. GBPUSD_2023: Sharpe 1.89 - MeanReverter_150
    ...

💾 CSV saved: results/mass_test/mass_test_summary_20240127_153000.csv
💾 JSON saved: results/mass_test/mass_test_report_20240127_153000.json
```

## Technical Details

### Key Differences from Old Implementation

| Feature                  | Old Implementation         | New Implementation                |
|--------------------------|----------------------------|-----------------------------------|
| Execution Method         | Direct function call       | subprocess.run()                  |
| CLI Flags                | Not passed                 | --strategy-discovery --batch-mode |
| Timeout                  | N/A                        | None (runs until complete)        |
| Progress Tracking        | None                       | JSON file with auto-save          |
| Resume Support           | No                         | Yes (automatic)                   |
| Error Handling           | Stop on first error        | Continue on errors                |
| Parallel Execution       | ProcessPoolExecutor        | Sequential (safer)                |
| Ctrl+C Handling          | Unsafe                     | Safe (saves progress)             |

### Why Sequential Instead of Parallel?

The new implementation runs tests sequentially (one at a time) instead of in parallel because:

1. **Resource Management** - Each test is very resource-intensive (CPU, memory)
2. **Progress Tracking** - Easier to track and resume sequential execution
3. **Debugging** - Easier to identify which dataset caused issues
4. **Subprocess Isolation** - Each test runs in its own process already

## Testing

Run the test suite:

```bash
python3 test_run_mass_test.py
```

Tests cover:
- Progress tracking (load, save, mark completed/failed/in-progress)
- Dataset discovery
- Subprocess command construction
- CLI argument parsing
- Edge cases (no datasets, division by zero)

## Migration from Old Version

If you were using the old version with `--parallel`:

**Old:**
```bash
python run_mass_test.py --parallel 4
```

**New:**
```bash
# Just run - it's sequential but has resume support
python run_mass_test.py

# Can safely interrupt and resume
# Each test runs in isolated subprocess
```

The new version is safer and more robust, even though it's sequential.

## Troubleshooting

### No datasets found
```bash
$ python run_mass_test.py --list
⚠️ Parquet directory not found: data/parquet
```

**Solution:** Create `data/parquet/` directory and add `.parquet` files

### Progress file corrupted
```bash
$ python run_mass_test.py --fresh
```

This will ignore the old progress file and start fresh.

### Want to retry only failed tests
```bash
$ python run_mass_test.py --retry-failed
```

### See what's happening
```bash
$ python run_mass_test.py --status
```

## Summary

The new `run_mass_test.py` is:
- ✅ More robust (subprocess isolation)
- ✅ More reliable (resume support)
- ✅ Better error handling (continues on failures)
- ✅ Safer (proper Ctrl+C handling)
- ✅ More informative (progress tracking, status command)
- ✅ Fully tested (test suite included)

Perfect for overnight/multi-day testing runs without losing progress!
