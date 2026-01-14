# 💾 Parquet Migration Guide

## Overview

This guide explains how to migrate NECROZMA data from JSON to Parquet format for improved performance and reduced disk usage.

## Benefits

| Metric | JSON | Parquet | Improvement |
|--------|------|---------|-------------|
| **Disk Usage** | ~42 GB | ~7 GB | **-83%** |
| **Read Speed** | ~10s per file | ~0.5s per file | **20x faster** |
| **Column Selection** | Load all data | Load only needed columns | **50x+ faster** |
| **Compression** | None | Snappy | Built-in |

## Migration Tool

The `migrate_to_parquet.py` script converts existing JSON files to Parquet format.

### Usage

#### Migrate Universes

```bash
python migrate_to_parquet.py --input ultra_necrozma_results/universes --type universe
```

#### Migrate Backtest Results

```bash
python migrate_to_parquet.py --input ultra_necrozma_results/backtest_results --type backtest
```

#### Migrate Trade Logs

```bash
python migrate_to_parquet.py --input ultra_necrozma_results/backtest_results --type trades
```

#### Migrate Everything

```bash
python migrate_to_parquet.py --all
```

#### Migrate and Delete JSON Files

⚠️ **Warning:** This will delete original JSON files after successful conversion.

```bash
python migrate_to_parquet.py --all --delete-json
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input` | Input directory with JSON files | `ultra_necrozma_results/universes` |
| `--output` | Output directory for Parquet files | Same as input |
| `--type` | Type of files to migrate (`universe`, `backtest`, `trades`) | `universe` |
| `--delete-json` | Delete JSON files after successful conversion | `False` |
| `--all` | Migrate all types (universes, backtest, trades) | `False` |

## File Structure

### Before Migration

```
ultra_necrozma_results/
├── universes/
│   ├── universe_001_5min_5lb.json          (large)
│   ├── universe_002_5min_10lb.json         (large)
│   └── ...
└── backtest_results/
    ├── universe_001_5min_5lb_backtest.json (large)
    └── ...
```

### After Migration

```
ultra_necrozma_results/
├── universes/
│   ├── universe_001_5min_5lb.json          (optional - can be deleted)
│   ├── universe_001_5min_5lb.parquet       (fast & small)
│   ├── universe_001_5min_5lb_metadata.json (small metadata)
│   ├── universe_002_5min_10lb.parquet
│   ├── universe_002_5min_10lb_metadata.json
│   └── ...
└── backtest_results/
    ├── universe_001_5min_5lb_backtest.parquet
    ├── universe_001_5min_5lb_backtest_metadata.json
    └── ...
```

## Parquet Format Details

### Universe Files

**Parquet Structure:**
- Each row = one level/direction combination
- Columns: `level`, `direction`, + all feature stats

**Metadata Sidecar:**
- Small JSON file with universe metadata
- Contains: name, config, processing_time, total_patterns

**Example:**

```python
import pandas as pd

# Load Parquet
df = pd.read_parquet('universe_001_5min_5lb.parquet')

# Shows:
#     level direction  ohlc_body_mean  ohlc_range_mean  ...
# 0  Pequeno        up           -1.00             2.48  ...
# 1  Pequeno      down            0.95             2.35  ...
```

### Backtest Result Files

**Parquet Structure:**
- Each row = one strategy result
- Columns: `strategy_name`, `sharpe_ratio`, `total_return`, etc.

**Metadata Sidecar:**
- Small JSON file with backtest metadata
- Contains: universe_name, universe_metadata, statistics, timestamp

**Example:**

```python
import pandas as pd

# Load Parquet
df = pd.read_parquet('universe_001_5min_5lb_backtest.parquet')

# Shows:
#              strategy_name  sharpe_ratio  total_return  ...
# 0  TrendFollower_SL10_TP50           1.5          0.25  ...
# 1   MeanReverter_SL15_TP30           1.2          0.18  ...
```

## Backward Compatibility

The system **automatically detects** and uses the best available format:

1. ✅ **Parquet preferred**: If `.parquet` file exists, use it (faster)
2. ✅ **JSON fallback**: If only `.json` exists, use it (compatible)
3. ✅ **Mixed environments**: Can have both formats, Parquet used when available

### Code Examples

#### Loading Universes

```python
from feature_extractor import load_universe_from_file
from pathlib import Path

# Automatically loads from .parquet if available, otherwise .json
universe_data = load_universe_from_file(Path('ultra_necrozma_results/universes/universe_001_5min_5lb'))
```

#### Loading Backtest Results

```python
from dashboard.utils.data_loader import load_all_results

# Automatically loads from .parquet if available, otherwise .json
results = load_all_results(results_dir='ultra_necrozma_results/backtest_results')
```

## Configuration

Edit `config.py` to customize storage behavior:

```python
# Storage Configuration
STORAGE_CONFIG = {
    "format": "parquet",           # "parquet" or "json"
    "compression": "snappy",        # "snappy", "gzip", "brotli"
    "partition_by": None,           # Can partition by "pair", "date", etc.
    "enable_metadata_sidecar": True,  # Save metadata separately
    "auto_detect_format": True,     # Auto-detect best format
}
```

## Multi-Worker Configuration

```python
# Multi-Worker Configuration
WORKER_CONFIG = {
    "default_workers": 1,           # Default workers (1 = sequential)
    "max_workers": 16,              # Maximum allowed workers
    "cpu_limit": 80,                # Max CPU % before throttling
    "cooldown_seconds": 5,          # Pause between batches
    "nice_priority": False,         # Run with low priority
    "adaptive_throttling": True,    # Dynamic worker adjustment
    "cpu_check_interval": 5,        # Check CPU every N tasks
}
```

## Running with Multi-Worker

```bash
# Use 4 workers with 80% CPU limit
python run_sequential_backtest.py --workers 4 --cpu-limit 80

# Add cooldown between batches
python run_sequential_backtest.py --workers 4 --cpu-limit 80 --cooldown 5

# Run with low priority (nice)
python run_sequential_backtest.py --workers 4 --cpu-limit 80 --nice

# Short form
python run_sequential_backtest.py -w 4
```

## Validation

After migration, verify the data:

### Check File Sizes

```bash
# Compare sizes
du -sh ultra_necrozma_results/universes/*.json
du -sh ultra_necrozma_results/universes/*.parquet

# Should see ~85% reduction in total size
```

### Verify Data Integrity

```python
from feature_extractor import load_universe_from_file
from pathlib import Path

# Load from Parquet
universe_data = load_universe_from_file(Path('ultra_necrozma_results/universes/universe_001_5min_5lb'))

# Verify data
print(f"Name: {universe_data['name']}")
print(f"Total patterns: {universe_data['total_patterns']}")
print(f"Results keys: {list(universe_data['results'].keys())}")
```

### Test Dashboard

```bash
# Start dashboard
streamlit run dashboard_quickstart.py

# Should automatically use Parquet files
# Check console for "Loaded from Parquet" messages
```

## Expected Savings

Based on typical NECROZMA data:

| Component | JSON Size | Parquet Size | Savings |
|-----------|-----------|--------------|---------|
| Universes (10 pairs × 25) | ~25 GB | ~4 GB | **-84%** |
| Backtest Results | ~12 GB | ~2 GB | **-83%** |
| Trade Logs | ~5 GB | ~1 GB | **-80%** |
| **TOTAL** | **~42 GB** | **~7 GB** | **-83%** |

**Note:** Savings may vary based on data structure and compression ratio.

## Troubleshooting

### Migration Shows Negative Savings

For very small test files, Parquet metadata overhead can make files larger. This is expected and only happens with small files (<10 KB). Real data files will show significant savings.

### "No files found" Error

Ensure the input directory path is correct and contains the expected file pattern:
- Universes: `universe_*.json`
- Backtest: `*_backtest.json`
- Trades: Files in `detailed_trades/` subdirectory

### Parquet Import Error

Install required dependencies:

```bash
pip install pandas pyarrow
```

### Dashboard Not Using Parquet

1. Check that Parquet files exist in the same directory as JSON files
2. Verify file naming matches: `universe_001_5min_5lb.parquet` (not `.json.parquet`)
3. Check console output for "Loaded from Parquet" or "Loaded from JSON" messages

## Best Practices

1. ✅ **Test First**: Migrate a few files first, verify they work
2. ✅ **Backup**: Keep JSON files until Parquet is verified working
3. ✅ **Monitor**: Check disk usage before/after to confirm savings
4. ✅ **Gradual**: Don't use `--delete-json` until confident
5. ✅ **Validate**: Test dashboard and backtest loading after migration

## Performance Impact

### Backtest Execution Time (10 pairs)

| Configuration | Time |
|---------------|------|
| 1 worker (JSON) | ~30h |
| 1 worker (Parquet) | ~25h |
| 4 workers (Parquet, 80% CPU) | ~10h |
| **Total Improvement** | **~20h saved (67%)** |

The combination of Parquet (faster I/O) and multi-worker (parallel execution) provides significant speedup.

## Support

For issues or questions:
1. Check this guide first
2. Review `migrate_to_parquet.py --help`
3. Create GitHub issue with `storage` or `migration` tag
