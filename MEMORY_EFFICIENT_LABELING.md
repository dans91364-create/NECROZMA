# Memory-Efficient Labeling System

## Problem

The original labeler accumulated **ALL** 210 configs in memory before saving:

```
14.6M rows × 210 configs × ~20 columns × 8 bytes = ~500GB of RAM needed!
```

**Result:** Crashes even with 86GB RAM, **ZERO files saved** (all work lost)

## Solution

The new memory-efficient labeler saves each config **immediately** to disk:

1. ✅ **Save immediately**: Each config written to `labels/{config}.parquet` right after processing
2. ✅ **Clear memory**: Run `gc.collect()` every 10 configs to free RAM
3. ✅ **Resume support**: Skip configs that already have saved files
4. ✅ **Memory efficient**: Peak RAM ~5-10GB (down from ~500GB!)

## Usage

### Memory-Efficient Mode (Default)

```python
from labeler import label_dataframe

# Returns list of saved file paths
saved_files = label_dataframe(
    df,
    target_pips=[5, 10, 15],
    stop_pips=[5, 10],
    horizons=[30, 60, 240],
    return_dict=False  # Default: memory-efficient!
)

print(f"Saved {len(saved_files)} files to labels/")
# Output: Saved 18 files to labels/
```

### Loading Results

```python
from labeler import load_label_results, load_all_label_results

# Load specific config (recommended)
df = load_label_results("T10_S5_H30")
print(f"Loaded {len(df):,} rows")

# Load all configs (⚠️ memory-intensive!)
all_results = load_all_label_results()
print(f"Loaded {len(all_results)} configs")
```

### Backward Compatibility Mode

```python
# Old behavior: load all results into RAM
results_dict = label_dataframe(
    df,
    target_pips=[10],
    stop_pips=[5],
    horizons=[60],
    return_dict=True  # Loads all into memory
)

# Same as before
for config_key, labels_df in results_dict.items():
    print(f"{config_key}: {len(labels_df)} rows")
```

## Resume Support

The labeler automatically resumes from where it left off:

```python
# First run - processes 4 configs
label_dataframe(df, target_pips=[10, 20], stop_pips=[5], horizons=[30, 60])
# Output:
#   💾 Saved T10_S5_H30.parquet
#   💾 Saved T10_S5_H60.parquet
#   💾 Saved T20_S5_H30.parquet
#   💾 Saved T20_S5_H60.parquet

# Crash happens here! 💥

# Second run - adds more configs, SKIPS existing ones!
label_dataframe(df, target_pips=[10, 20, 30], stop_pips=[5], horizons=[30, 60])
# Output:
#   ⏭️  Found 4/6 already saved - resuming...
#   💾 Saved T30_S5_H30.parquet  (only new ones!)
#   💾 Saved T30_S5_H60.parquet
```

## File Structure

```
labels/
├── T5_S5_H1.parquet
├── T5_S5_H5.parquet
├── T5_S5_H15.parquet
├── T5_S5_H30.parquet
├── ...
└── T50_S30_H1440.parquet

Total: 210 files (6 targets × 5 stops × 7 horizons)
Each file: ~10-50 MB (depends on data size)
```

## Memory Comparison

| Metric | Before | After |
|--------|--------|-------|
| Peak RAM | ~500GB 💥 | ~5-10GB ✅ |
| Files saved on crash | 0 😱 | 210 ✅ |
| Resume support | No ❌ | Yes ✅ |
| Processing speed | Same | Same |
| Accuracy | Same | Same |

## API Reference

### `label_dataframe()`

```python
def label_dataframe(
    df: pd.DataFrame,
    target_pips: List[float] = None,
    stop_pips: List[float] = None,
    horizons: List[int] = None,
    num_workers: int = None,  # Deprecated
    pip_value: float = 0.0001,
    progress_callback = None,
    use_cache: bool = None,
    return_dict: bool = False
) -> Union[List[str], Dict[str, pd.DataFrame]]:
```

**Returns:**
- `List[str]` of file paths (if `return_dict=False`, default)
- `Dict[str, pd.DataFrame]` (if `return_dict=True`, backward compatibility)

### `load_label_results()`

```python
def load_label_results(config_key: str) -> pd.DataFrame:
    """
    Load a specific labeled dataset from disk
    
    Args:
        config_key: Configuration key (e.g., "T5_S5_H1")
        
    Returns:
        DataFrame with labeled results
    """
```

### `load_all_label_results()`

```python
def load_all_label_results() -> Dict[str, pd.DataFrame]:
    """
    Load all labeled datasets from disk
    
    ⚠️ WARNING: Loads ALL results into memory!
    Only use if you have enough RAM.
    
    Returns:
        Dict mapping config_key -> DataFrame
    """
```

## Demo

Run the demo script to see it in action:

```bash
python demo_memory_efficient_labeling.py
```

## Migration Guide

### For Existing Code

**Old code:**
```python
results = label_dataframe(df)
for config_key, labels_df in results.items():
    analyze(labels_df)
```

**Option 1: Update to memory-efficient (recommended)**
```python
saved_files = label_dataframe(df, return_dict=False)
for file in saved_files:
    config_key = Path(file).stem
    labels_df = load_label_results(config_key)
    analyze(labels_df)
```

**Option 2: Use backward compatibility mode**
```python
results = label_dataframe(df, return_dict=True)  # Just add this!
for config_key, labels_df in results.items():
    analyze(labels_df)
```

## Implementation Details

### How It Works

1. **Process config**: Label all candles for one config using Numba vectorization
2. **Save immediately**: Write DataFrame to `labels/{config}.parquet`
3. **Clear memory**: Delete DataFrame and run `gc.collect()` every 10 configs
4. **Repeat**: Move to next config

### File Naming Convention

Files are named using the pattern: `T{target}_S{stop}_H{horizon}.parquet`

Examples:
- `T5_S5_H1.parquet` → target=5, stop=5, horizon=1 minute
- `T10_S5_H60.parquet` → target=10, stop=5, horizon=60 minutes
- `T50_S30_H1440.parquet` → target=50, stop=30, horizon=1440 minutes (1 day)

### Garbage Collection

`gc.collect()` is called every 10 configs (not every config) for optimal performance.
This balances memory efficiency with processing speed.

## Testing

Run the test suite:

```bash
# Memory-efficient labeling tests
pytest tests/test_memory_efficient_labeler.py -v

# All labeler tests
pytest tests/test_*label*.py -v
```

All tests pass ✅

## FAQ

**Q: Will this change my existing code?**  
A: No! Use `return_dict=True` for backward compatibility.

**Q: Can I still use the old caching system?**  
A: Yes, but it's not recommended. The new system is more robust and memory-efficient.

**Q: What if I delete a parquet file?**  
A: Just run `label_dataframe()` again - it will regenerate only the missing file.

**Q: Can I process configs in parallel?**  
A: Not currently. Sequential processing with resume support is safer and memory-efficient.

**Q: How do I clear all label files?**  
A: Simply delete the `labels/` directory: `rm -rf labels/`

## Benefits Summary

✅ **No more RAM overflow** - Only ~5-10GB needed instead of ~500GB  
✅ **No data loss** - Each config saved immediately to disk  
✅ **Resume support** - Restart after crash without redoing work  
✅ **Backward compatible** - Old code still works with `return_dict=True`  
✅ **Same accuracy** - Identical labeling results  
✅ **Same speed** - Still uses Numba vectorization  

---

**Need help?** Check out `demo_memory_efficient_labeling.py` for examples!
