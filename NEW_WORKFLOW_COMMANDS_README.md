# New Workflow Commands: --generate-base and --search-light

## Overview

This document describes the new split workflow commands that optimize the strategy discovery process by separating heavy computation (run once) from strategy testing (run multiple times).

## Problem Solved

Previously, the `--strategy-discovery` command ran all 7 steps every time, which was inefficient when:
- Testing different strategies/templates on the same data
- Experimenting with different parameters
- Comparing results across 30 pairs

## Solution

Split the workflow into two separate commands:

### 1. `--generate-base` (Run ONCE per pair)

Generates the complete base needed for strategy testing.

**Steps executed:**
1. Load parquet (tick data)
2. `analyzer.run_analysis()` → Generate UNIVERSES
3. `analyzer.save_results()` → Save universes/*.parquet
4. Labeling (if not cached)
5. Pattern Mining (if not cached) → Save `{PAIR}_{YEAR}_patterns.json`
6. Regime Detection → Save `{PAIR}_{YEAR}_regimes.parquet`
7. 🗑️ DELETE `labels/` directory (~56GB freed!)
8. ⏹️ STOP

**Output (BASE):**
- `{PAIR}_{YEAR}.parquet` (tick data - kept!)
- `universes/*.parquet` (feature extraction)
- `{PAIR}_{YEAR}_patterns.json`
- `{PAIR}_{YEAR}_regimes.parquet`

**Time:** ~2-4 hours per pair

### 2. `--search-light` (Run MANY times)

Uses the existing base to test strategies quickly.

**Requires (from base):**
- parquet (tick data)
- universes/*.parquet
- patterns.json
- regimes.parquet

**Steps executed:**
1. Load parquet (tick data)
2. SKIP universes (already exist)
3. LOAD patterns.json (from cache)
4. LOAD regimes.parquet (from cache)
5. Strategy Generation
6. Backtesting (tick-level precision)
7. SKIP Ranking (not needed now)
8. SKIP Report (not needed now)

**Output:**
- `{PAIR}_{YEAR}_backtest_results.parquet` (raw results for analysis)

**Time:** ~30-60 minutes per run

## Usage

### Basic Workflow

```bash
# 1. Convert CSV to Parquet (if needed)
python main.py --csv GBPUSD_2025.csv --convert-only

# 2. Generate complete base (universes + patterns + regimes)
python main.py --parquet GBPUSD_2025.parquet --generate-base

# 3. Search for light (test strategies) - can run multiple times!
python main.py --parquet GBPUSD_2025.parquet --search-light

# 4. Modify config.py, then test again
python main.py --parquet GBPUSD_2025.parquet --search-light --force-rerun
```

### Additional Options

```bash
# Sequential processing (recommended for VMs)
python main.py --parquet GBPUSD_2025.parquet --generate-base --sequential

# With batch mode for better memory management
python main.py --parquet GBPUSD_2025.parquet --search-light --batch-mode --batch-size 200

# Force rerun backtesting (ignore cache)
python main.py --parquet GBPUSD_2025.parquet --search-light --force-rerun
```

## Workflow for 30 Pairs

```bash
# Phase 1: Generate base for all pairs (run once)
for PAIR in EURUSD GBPUSD USDJPY USDCHF USDCAD AUDUSD NZDUSD \
            EURJPY EURGBP GBPJPY AUDJPY NZDJPY CADJPY CHFJPY \
            EURAUD GBPAUD EURCHF XAUUSD XAGUSD XPTUSD XPDUSD \
            XCUUSD XALUSD XNIUSD USDMXN USDZAR USDTRY EURNOK \
            USDSEK DXY; do
    echo "Processing ${PAIR}..."
    python main.py --csv ${PAIR}_2025.csv --convert-only
    python main.py --parquet ${PAIR}_2025.parquet --generate-base --sequential
done

# Phase 2: Experiment with strategies (run many times)
python main.py --parquet EURUSD_2025.parquet --search-light

# Adjust config.py with new templates or parameters...
python main.py --parquet EURUSD_2025.parquet --search-light --force-rerun

# Test across all pairs with current config...
for PAIR in EURUSD GBPUSD USDJPY; do
    python main.py --parquet ${PAIR}_2025.parquet --search-light
done
```

## Benefits

| Command | Time | Purpose | Output |
|---------|------|---------|--------|
| `--generate-base` | ~2-4 hours | Heavy lifting, run once per pair | Base files (universes, patterns, regimes) |
| `--search-light` | ~30-60 min | Fast experimentation, run ∞ times | Backtest results |

### Time Savings Example

**Old workflow (running --strategy-discovery 3 times):**
- Run 1: 2-4 hours
- Run 2: 2-4 hours (even though base data unchanged)
- Run 3: 2-4 hours (even though base data unchanged)
- **Total: 6-12 hours**

**New workflow (--generate-base once + --search-light 3 times):**
- Generate base: 2-4 hours (once)
- Search 1: 30-60 min
- Search 2: 30-60 min
- Search 3: 30-60 min
- **Total: 3.5-6 hours (40-50% faster!)**

## Important Notes

1. **Run Order**: Always run `--generate-base` before `--search-light`
2. **Base Files**: The base files are cached, so if they exist, they will be loaded instead of regenerated
3. **Force Rerun**: Use `--force-rerun` with `--search-light` to ignore cached backtest results
4. **Both Flags**: If you accidentally provide both `--generate-base` and `--search-light`, only `--generate-base` will run (with a warning)
5. **Sequential Mode**: Use `--sequential` for VMs or low-memory systems
6. **Batch Mode**: Use `--batch-mode` with `--search-light` for better memory management during backtesting

## File Locations

All output files use the format `{PAIR}_{YEAR}_*`:

```
output/
├── EURUSD_2025_patterns.json          # Pattern mining results
├── EURUSD_2025_regimes.parquet        # Regime detection results
├── EURUSD_2025_backtest_results.parquet  # Backtest results
└── universes/
    ├── universe_001_EURUSD_2025.parquet
    ├── universe_002_EURUSD_2025.parquet
    └── ...
```

## Error Handling

### Base files not found
```
❌ Patterns file not found: output/EURUSD_2025_patterns.json
   Run --generate-base first to create base files!
```
**Solution**: Run `--generate-base` before running `--search-light`

### Both flags provided
```
⚠️  WARNING: Both --generate-base and --search-light flags provided
   Only --generate-base will be executed (--search-light will be ignored)
   Run these commands separately for the intended workflow
```
**Solution**: Run the commands separately

## Testing

Run the test suite to verify the implementation:

```bash
python test_new_workflow_commands.py
```

Expected output:
```
======================================================================
✅ All tests passed!
======================================================================

📋 Summary:
   • Argument parsing works correctly
   • New functions exist and are callable
   • Help text generated successfully
   • Arguments work independently
```

## Technical Details

### Implementation

- **New Arguments**: Added to `parse_arguments()` in `main.py`
- **New Functions**: 
  - `run_generate_base(df, args)` - Generates base files
  - `run_search_light(df, args)` - Tests strategies with base files
- **Main Function**: Updated to route to appropriate function based on flags

### Code Changes

- Modified `main.py`:
  - Added `--generate-base` and `--search-light` arguments
  - Implemented `run_generate_base()` function
  - Implemented `run_search_light()` function
  - Updated `main()` to check flags and route accordingly
  - Added warning when both flags provided
  
- Added `test_new_workflow_commands.py`:
  - Tests argument parsing
  - Tests function existence
  - Tests argument independence
  - Tests both flags provided together

### Compatibility

- ✅ Compatible with existing `--strategy-discovery` command
- ✅ Compatible with all existing flags (`--sequential`, `--batch-mode`, `--force-rerun`, etc.)
- ✅ Works with both CSV and Parquet input
- ✅ Maintains backward compatibility

## Future Enhancements

Potential improvements for future versions:

1. **Parallel Base Generation**: Generate base files for multiple pairs in parallel
2. **Base Validation**: Add command to validate base files integrity
3. **Base Update**: Add command to update only specific base components
4. **Strategy Comparison**: Add tool to compare results across multiple `--search-light` runs

## Support

For questions or issues:
1. Check this documentation first
2. Run tests: `python test_new_workflow_commands.py`
3. Check help: `python main.py --help`
4. Review error messages carefully
