# Batch Processing for Strategy Backtesting

## Overview

The batch processing system prevents memory accumulation issues when backtesting large numbers of strategies (e.g., 4620 strategies) by dividing them into smaller batches that run in isolated subprocesses.

## Problem Solved

When running all strategies sequentially in a single process:
- Memory and resources accumulate over time
- Process hangs at around 26% completion (~1086 strategies)
- Individual strategies work fine (0.23s each), but the issue is cumulative

## Solution

Batch processing with subprocess isolation:
- Divides 4620 strategies into batches (default: 200 per batch)
- Each batch runs in an isolated subprocess
- Subprocess exits after completion, cleaning all memory
- Results are collected and merged at the end

## Usage

### Using main.py (Recommended)

Enable batch mode when running strategy discovery:

```bash
# Basic batch mode with default batch size (200)
python main.py --strategy-discovery --batch-mode

# Custom batch size
python main.py --strategy-discovery --batch-mode --batch-size 150

# With test mode
python main.py --strategy-discovery --batch-mode --test-mode --test-strategy balanced
```

### Using batch_runner.py directly

```bash
# Run with default batch size (200)
python batch_runner.py

# Custom batch size
python batch_runner.py --batch-size 150

# Custom data file
python batch_runner.py --batch-size 200 --parquet /path/to/data.parquet

# Skip merging (for debugging)
python batch_runner.py --no-merge
```

### Using backtest_batch.py (Worker Script)

Process a specific batch range:

```bash
# Process strategies 0-200
python backtest_batch.py --start 0 --end 200 --output results_batch_0.parquet

# Process strategies 200-400
python backtest_batch.py --start 200 --end 400 --output results_batch_1.parquet
```

## Expected Output

```
Running 4620 strategies in 24 batches of 200...

Batch  1/24:    0-200   ✅ 46.2s | 200 strategies | RAM: 3.1%
Batch  2/24:  200-400   ✅ 45.8s | 200 strategies | RAM: 3.0%
Batch  3/24:  400-600   ✅ 47.1s | 200 strategies | RAM: 3.2%
...
Batch 24/24: 4600-4620  ✅  4.6s |  20 strategies | RAM: 2.9%

Merging results...
✅ Complete! 4620 strategies tested in 18m 32s
```

## Files Created

### Batch Results
- `ultra_necrozma_results/batch_results/results_batch_0.parquet`
- `ultra_necrozma_results/batch_results/results_batch_1.parquet`
- ... (one file per batch)

### Merged Results
- `ultra_necrozma_results/EURUSD_2025_backtest_results_merged.parquet`

## Architecture

### Components

1. **batch_runner.py** - Main orchestrator
   - Calculates total strategies and divides into batches
   - Spawns subprocess for each batch
   - Tracks progress with timing and RAM usage
   - Merges all batch results into single file

2. **backtest_batch.py** - Worker script
   - Loads data
   - Generates strategies for specific range
   - Runs backtest
   - Saves results to parquet
   - Exits cleanly (memory cleanup)

3. **main.py** - Integration point
   - `--batch-mode` flag enables batch processing
   - `--batch-size` sets strategies per batch (default: 200)

### Process Flow

```
1. Calculate total strategies (e.g., 4620)
2. Divide into batches (e.g., 24 batches of 200)
3. For each batch:
   a. Spawn subprocess
   b. Worker loads data
   c. Worker generates strategies [start:end]
   d. Worker runs backtest
   e. Worker saves results to parquet
   f. Subprocess exits (memory freed)
4. Merge all batch results
5. Return merged results file
```

## Performance

- **Individual strategy**: ~0.23s
- **Batch of 200**: ~45s (including subprocess overhead)
- **Total (4620 strategies, 24 batches)**: ~18-20 minutes
- **RAM usage**: Stays constant (~3%) instead of accumulating

## Error Handling

- Failed batches are logged but don't stop the entire process
- Batch results are saved incrementally
- Partial results can be merged even if some batches fail

## Testing

Run the test suite:

```bash
# Full test with merge
python test_batch_processing.py

# Keep test files for inspection
python test_batch_processing.py --no-cleanup
```

## Configuration

Default batch size (200) is optimized for:
- Balance between subprocess overhead and memory management
- Reasonable progress updates
- ~45 seconds per batch

Adjust `--batch-size` based on:
- Available RAM (smaller batches for low RAM)
- Desired progress granularity
- Subprocess overhead tolerance

## Troubleshooting

### Batch fails with timeout
- Increase timeout in `batch_runner.py` (default: 1 hour)
- Reduce batch size

### Merging fails
- Check that batch files exist in `ultra_necrozma_results/batch_results/`
- Verify parquet files are not corrupted
- Check disk space

### High memory usage
- Reduce batch size
- Check for memory leaks in strategy generation or backtesting code

## Comparison: Standard vs Batch Mode

| Aspect | Standard Mode | Batch Mode |
|--------|--------------|------------|
| Memory | Accumulates | Constant |
| Completion | Hangs at 26% | Completes 100% |
| RAM Usage | Grows to 90%+ | Stays at 3-5% |
| Resumability | No | Yes (per batch) |
| Progress Tracking | Basic | Detailed with ETA |
| Overhead | None | ~1-2s per batch |

## Future Enhancements

Potential improvements:
- Parallel batch execution (multiple subprocesses)
- Automatic retry for failed batches
- Checkpointing for long-running jobs
- Distributed execution across multiple machines
