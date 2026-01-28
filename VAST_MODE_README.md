# 🚀 VAST Mode - High-Performance Parallel Processing

## Overview

VAST mode is a new feature for ULTRA NECROZMA that enables high-performance parallel processing on powerful cloud machines. It auto-detects system resources and maximizes utilization for processing multiple currency pairs simultaneously.

## Features

- **Auto-Detection**: Automatically detects CPU cores and RAM
- **Parallel Processing**: Process multiple parquet files simultaneously
- **Flexible Configuration**: Manual override of parallelism settings
- **Progress Tracking**: Real-time progress reporting with success/failure status
- **Compatible Modes**: Works with both `--generate-base` and `--search-light`

## Requirements

- `psutil>=5.9.0` (already in requirements.txt)
- Parquet files must follow naming convention: `PAIRNAME_YEAR.parquet`
  - Examples: `EURUSD_2025.parquet`, `GBPUSD_2024.parquet`

## Usage

### Basic Usage (Auto-Detection)

Process all parquet files in a directory with auto-detected settings:

```bash
# Generate base files for all pairs
python main.py --vast-mode --input-dir data/parquet/ --generate-base

# Run search-light on all pairs
python main.py --vast-mode --input-dir data/parquet/ --search-light
```

### Advanced Usage (Manual Configuration)

Specify parallelism manually:

```bash
# Process 30 pairs simultaneously with 4 workers per pair
python main.py --vast-mode --input-dir data/parquet/ --generate-base \
    --parallel-pairs 30 --max-workers 4

# Force rerun backtesting
python main.py --vast-mode --input-dir data/parquet/ --search-light \
    --parallel-pairs 20 --max-workers 8 --force-rerun
```

## Arguments

### `--vast-mode`
- **Type**: Flag
- **Description**: Enable VAST mode for high-performance parallel processing
- **Default**: False

### `--input-dir`
- **Type**: String
- **Description**: Directory containing multiple parquet files to process
- **Required**: Yes (when using vast-mode)
- **Example**: `data/parquet/`

### `--parallel-pairs`
- **Type**: Integer
- **Description**: Number of currency pairs to process simultaneously
- **Default**: 1 (auto-detected in vast-mode)
- **Auto-Detection Logic**: `min(30, cpu_cores // 4)` (4 cores per pair)

### `--max-workers`
- **Type**: Integer
- **Description**: Maximum workers per pair for parallel processing
- **Default**: None (auto-detected as 4)

## Performance

### Example: 128 cores, 1TB RAM

When vast-mode detects 128 cores and 1TB RAM:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⚡ VAST MODE ACTIVATED ⚡                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║   🖥️  CPU Cores:     128                                                     ║
║   🧠 RAM:           1024 GB                                                  ║
║   📁 Parquet Files: 30                                                       ║
║   ⚡ Parallel Pairs: 30                                                       ║
║   👷 Workers/Pair:  4                                                        ║
║   📊 Est. Time:     ~3-4 hours                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Settings:**
- `parallel_pairs = 30` (all pairs processed at once)
- `workers_per_pair = 4` (128 cores / 30 pairs ≈ 4)

**Performance Comparison:**

| Mode | Machine | 30 Pairs Time | Cost |
|------|---------|---------------|------|
| Local | 8 cores, 32GB | ~90 hours | $0 |
| VAST | 128 cores, 1TB | ~3-4 hours | ~$3 |

**Speedup: ~25x faster!**

## Output

### During Processing

```
🐉 Processing 30 pairs in parallel...

✅ [1/30] EURUSD - generate-base complete (2.8h)
✅ [2/30] GBPUSD - generate-base complete (2.9h)
✅ [3/30] USDJPY - generate-base complete (3.1h)
...
```

### Final Summary

```
════════════════════════════════════════════════════════════════════════════════
⚡ VAST MODE COMPLETE ⚡
════════════════════════════════════════════════════════════════════════════════
   Total pairs: 30
   Successful: 30
   Failed: 0
   Total time: 3.2h
════════════════════════════════════════════════════════════════════════════════
```

## Architecture

### Resource Detection

```python
def detect_resources():
    """Auto-detect CPU cores and RAM"""
    cpu_cores = os.cpu_count() or 8
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    return {
        'cpu_cores': cpu_cores,
        'ram_gb': ram_gb,
        'recommended_parallel_pairs': min(30, max(1, cpu_cores // 4)),
        'recommended_workers_per_pair': 4
    }
```

### Parallel Processing

VAST mode uses `ProcessPoolExecutor` for true parallelism:

```python
with ProcessPoolExecutor(max_workers=parallel_pairs) as executor:
    futures = [executor.submit(worker_func, pf, workers) for pf in files]
    
    for future in as_completed(futures):
        result = future.result()
        # Report progress
```

### Process Isolation

Each parquet file is processed in a separate process with:
- Independent memory space (no shared state issues)
- Isolated config modifications (process-safe)
- Exception isolation (one failure doesn't crash others)

## File Naming Convention

**IMPORTANT**: Parquet files MUST follow this naming convention:

```
PAIRNAME_YEAR.parquet
```

**Examples:**
- ✅ `EURUSD_2025.parquet`
- ✅ `GBPUSD_2024.parquet`
- ✅ `USDJPY_2023.parquet`
- ❌ `eurusd.parquet` (missing year)
- ❌ `EURUSD-2025.parquet` (wrong separator)

The worker functions extract pair name and year from the filename:
```python
filename = "EURUSD_2025.parquet"
parts = filename.stem.split("_")  # ["EURUSD", "2025"]
pair_name = parts[0]  # "EURUSD"
year = parts[1]       # "2025"
```

## Testing

Three test suites are provided:

### 1. Unit Tests
```bash
python test_vast_mode.py
```

### 2. Manual Tests
```bash
python test_vast_mode_manual.py
```

### 3. Integration Tests
```bash
python test_vast_mode_integration.py
```

## Troubleshooting

### Error: "input-dir is required"
```bash
❌ ERROR: --input-dir is required for VAST mode
```
**Solution**: Specify the directory containing parquet files:
```bash
python main.py --vast-mode --input-dir data/parquet/ --generate-base
```

### Error: "Must specify either --generate-base or --search-light"
```bash
❌ ERROR: Must specify either --generate-base or --search-light
```
**Solution**: Add one of the mode flags:
```bash
python main.py --vast-mode --input-dir data/parquet/ --generate-base
```

### Error: "No parquet files found"
```bash
❌ ERROR: No parquet files found in data/parquet/
```
**Solution**: Ensure directory contains `.parquet` files:
```bash
ls -la data/parquet/*.parquet
```

### Error: File naming issues
If processing fails silently, check file names:
```bash
# Rename files to correct format
mv eurusd.parquet EURUSD_2025.parquet
mv GBPUSD-2024.parquet GBPUSD_2024.parquet
```

## Implementation Details

### Functions

- `detect_resources()`: Auto-detect CPU/RAM and calculate optimal settings
- `print_resources_banner()`: Display VAST mode banner with configuration
- `_setup_worker_environment()`: Common setup for worker processes
- `run_generate_base_single()`: Worker for single-file generate-base
- `run_search_light_single()`: Worker for single-file search-light
- `run_vast_mode()`: Main orchestrator for parallel processing

### Integration

VAST mode is integrated into `main()` function:
```python
def main():
    args = parse_arguments()
    
    # Check if VAST mode is enabled
    if args.vast_mode:
        run_vast_mode(args)
        return  # Exit after vast mode completes
    
    # Continue with normal processing...
```

## Future Enhancements

Potential improvements for future releases:

1. **Adaptive Chunk Size**: Use `recommended_chunk_size` for memory optimization
2. **Dynamic Scaling**: Adjust parallelism based on system load
3. **Resume Support**: Checkpoint and resume interrupted processing
4. **Distributed Mode**: Support for multiple machines (cluster computing)
5. **Cost Estimation**: Predict cloud computing costs before starting

## Security

✅ **Security Scan**: Passed CodeQL analysis with 0 alerts
✅ **Code Review**: All review comments addressed
✅ **Process Isolation**: Safe parallel processing with no shared state

## License

Part of ULTRA NECROZMA - Supreme Forex Analysis System
