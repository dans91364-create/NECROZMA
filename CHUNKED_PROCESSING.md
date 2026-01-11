# 💎 Chunked Processing System Documentation

## Overview

The **Chunked Processing System** enables ULTRA NECROZMA to process large datasets (14M+ rows) efficiently with flexible memory constraints, checkpoint/resume capabilities, and thermal protection.

---

## 🎯 Key Features

### 1. **Data Chunking**
Split large parquet files into manageable temporal chunks:
- **Monthly**: ~1.2M rows per chunk (12 chunks/year) - Default, balanced
- **Weekly**: ~300K rows per chunk (52 chunks/year) - Smaller memory footprint
- **Daily**: ~40K rows per chunk (365 chunks/year) - Minimal memory usage

### 2. **Dual Processing Strategies**

#### **Chunked Strategy** (Fast, More Memory)
```
FOR each chunk:
    FOR each universe:
        Process universe on chunk
    Merge universe results
    Save chunk_XX_results.parquet
```
- **Pros**: Faster processing (10-16h for full dataset)
- **Cons**: Higher memory usage (3-4GB peak)
- **Best for**: Bare-metal systems with 32GB+ RAM

#### **Universe Strategy** (Slow, Less Memory)
```
FOR each universe:
    FOR each chunk:
        Process chunk for universe
    Merge chunks for universe
    Save universe_XX_results.parquet
```
- **Pros**: Lower memory usage (1-2GB peak), more granular checkpoints
- **Cons**: Slower processing (18-24h for full dataset)
- **Best for**: VMs, systems with <32GB RAM

#### **Auto Strategy** (Recommended)
Automatically selects best strategy based on:
- VM detection (VMware, VirtualBox, KVM, etc.)
- Available RAM (threshold: 32GB)
- System type (bare-metal vs virtualized)

### 3. **Checkpoint/Resume System**
- **Granular checkpoints**: Save progress after each chunk/universe
- **Resume from failure**: Continue from last checkpoint after crash
- **Metadata tracking**: Store system state, elapsed time, memory usage
- **Checkpoint cleanup**: Automatic removal of old checkpoints

### 4. **Thermal Protection**
- **Cooling breaks**: Periodic pauses to prevent overheating
  - After N chunks (default: 3)
  - After N universes (default: 5)
  - Configurable duration (default: 120s)
- **CPU monitoring**: Track CPU usage as temperature proxy
  - Pause if CPU > 85% for 5+ minutes
  - Early resume when CPU < 40%
- **VM-safe operation**: Prevents thermal throttling in cloud VMs

### 5. **Memory Management**
- **Aggressive garbage collection** between processing steps
- **Memory usage monitoring** with warnings
- **Automatic cooldown** when memory > 80%

---

## 📋 Usage Examples

### Basic Chunked Processing
```bash
# Auto-select strategy (recommended)
python main.py --chunk-size monthly --strategy auto

# Explicit strategy selection
python main.py --chunk-size weekly --strategy universe
python main.py --chunk-size monthly --strategy chunked
```

### Resume from Checkpoint
```bash
# Resume from last checkpoint
python main.py --resume

# Start fresh (ignore checkpoints)
python main.py --fresh

# Resume with specific settings
python main.py --resume --strategy universe --chunk-size monthly
```

### VM-Safe Mode
```bash
# Recommended for VMs with thermal concerns
python main.py \
  --strategy universe \
  --chunk-size weekly \
  --cooling-chunk-interval 3 \
  --cooling-universe-interval 5 \
  --max-cpu 80
```

### Process Specific Universes/Chunks
```bash
# Process specific universes
python main.py --universes "1,5,10-15,20"

# Process specific chunks
python main.py --chunks "1-6,12"

# Combine both
python main.py --universes "1-10" --chunks "1-3"
```

### Disable Cooling Breaks
```bash
# For controlled environments or testing
python main.py \
  --cooling-chunk-interval 0 \
  --cooling-universe-interval 0
```

### Keep Chunk Files
```bash
# Don't delete chunk files after processing
python main.py --keep-chunks
```

---

## 🔧 Configuration

### CLI Arguments

#### Chunking
- `--chunk-size {daily,weekly,monthly}`: Temporal chunk size (default: monthly)
- `--keep-chunks`: Keep chunk files after processing

#### Strategy
- `--strategy {auto,chunked,universe}`: Processing strategy (default: auto)

#### Cooling
- `--cooling-chunk-interval N`: Cooling break every N chunks (default: 3, 0=disable)
- `--cooling-universe-interval N`: Cooling break every N universes (default: 5, 0=disable)
- `--cooling-duration N`: Cooling break duration in seconds (default: 120)

#### CPU Monitoring
- `--max-cpu N`: Pause if CPU > N% for 5+ minutes (default: 85)

#### Resume
- `--resume`: Resume from last checkpoint
- `--fresh`: Ignore checkpoints and start fresh

#### Specific Processing
- `--universes "RANGE"`: Process specific universes (e.g., "1,5,10-15,20")
- `--chunks "RANGE"`: Process specific chunks (e.g., "1-6,12")

---

## 📊 Expected Performance

| Metric | Chunked Strategy | Universe Strategy |
|--------|------------------|-------------------|
| Peak Memory | 3-4GB | 1-2GB |
| Total Time (14M rows) | 10-16h | 18-24h |
| Checkpoints | 12 (monthly) | 300 (25 universes × 12 chunks) |
| Resume Precision | ±2h work | ±10min work |
| I/O Operations | Lower | Higher |
| VM-Safe | Good | Excellent |

### Strategy Selection Guide

**Use Chunked Strategy when:**
- ✅ Running on bare-metal with 32GB+ RAM
- ✅ Speed is priority over memory
- ✅ System has good cooling
- ✅ No strict memory constraints

**Use Universe Strategy when:**
- ✅ Running in VM (VMware, VirtualBox, AWS, etc.)
- ✅ Limited RAM (<32GB)
- ✅ Thermal concerns (overheating risk)
- ✅ Need granular checkpoints
- ✅ Memory stability is critical

**Use Auto Strategy when:**
- ✅ Unsure which to choose (recommended default)
- ✅ System may change (bare-metal ↔ VM)
- ✅ Want optimal automatic selection

---

## 🏗️ Architecture

### File Structure
```
NECROZMA/
├── data/
│   ├── EURUSD_2025.parquet
│   └── chunks/
│       ├── chunk_001_2025-01.parquet
│       ├── chunk_002_2025-02.parquet
│       └── ...
├── ultra_necrozma_results/
│   ├── .checkpoint/
│   │   └── u018_c009_20260111_034523.json
│   ├── chunks/
│   │   └── chunks_metadata.json
│   ├── universe_01_patterns.parquet
│   ├── universe_02_patterns.parquet
│   ├── ...
│   ├── final_patterns.parquet
│   └── performance_report.md
├── data_chunker.py           # Temporal chunking
├── checkpoint_manager.py     # Checkpoint/resume
├── thermal_manager.py        # Cooling & CPU monitoring
├── result_consolidator.py    # Result merging
├── universe_processor.py     # Dual strategy processor
└── main.py                   # Entry point
```

### Components

#### 1. **DataChunker**
```python
from data_chunker import DataChunker

chunker = DataChunker(output_dir=Path("data/chunks"))
chunks = chunker.split_temporal(parquet_path, chunk_size="monthly")
metadata = chunker.get_chunk_metadata()
```

#### 2. **CheckpointManager**
```python
from checkpoint_manager import CheckpointManager

mgr = CheckpointManager(checkpoint_dir=Path(".checkpoint"))
checkpoint = mgr.save_checkpoint(universe_idx, chunk_idx, partial_results)
u_idx, c_idx, results = mgr.load_checkpoint()
```

#### 3. **CoolingManager & CPUMonitor**
```python
from thermal_manager import CoolingManager, CPUMonitor

cooling = CoolingManager(chunk_interval=3, universe_interval=5)
if cooling.should_pause_chunk(chunk_idx):
    cooling.cooling_break(duration=120, reason="periodic")

cpu_mon = CPUMonitor(max_cpu=85)
if cpu_mon.is_overheating():
    cpu_mon.wait_for_cooldown()
```

#### 4. **ResultConsolidator**
```python
from result_consolidator import ResultConsolidator

consolidator = ResultConsolidator(output_dir=Path("results"))
merged = consolidator.merge_universe_results(universe_dir)
report = consolidator.generate_final_report(merged, metadata)
```

#### 5. **UniverseProcessor**
```python
from universe_processor import UniverseProcessor

processor = UniverseProcessor(
    strategy='auto',
    chunk_size='monthly',
    enable_checkpoints=True,
    enable_cooling=True
)

results = processor.process(df, universes, resume=True)
```

---

## 🧪 Testing

Run integration tests:
```bash
python tests/test_chunked_processing.py
```

Test individual modules:
```bash
python data_chunker.py           # Test chunking
python checkpoint_manager.py     # Test checkpointing
python thermal_manager.py        # Test cooling/CPU
python result_consolidator.py    # Test consolidation
python universe_processor.py     # Test processor
```

---

## 💡 Tips & Best Practices

### For VMs
1. **Always use universe strategy**: Better checkpointing, lower memory
2. **Enable cooling breaks**: Prevent thermal throttling
3. **Monitor CPU**: Set `--max-cpu 80` for safety margin
4. **Use weekly/daily chunks**: Further reduce memory usage

### For Bare-Metal
1. **Try chunked strategy first**: Faster completion
2. **Monitor memory**: Ensure 32GB+ available
3. **Adjust chunk size**: Monthly chunks usually optimal
4. **Disable cooling if stable**: Save time on controlled systems

### For Interrupted Processing
1. **Always use `--resume`**: Continue from last checkpoint
2. **Check checkpoint age**: Stale checkpoints (>24h) may be ignored
3. **Use `--fresh` carefully**: Deletes all progress

### Memory Management
1. **Start with larger chunks**: Test with monthly first
2. **Scale down if needed**: Try weekly → daily if memory issues
3. **Monitor during processing**: Watch for memory warnings
4. **Close other apps**: Free up RAM before large runs

---

## 🐛 Troubleshooting

### Out of Memory
```
ISSUE: Process killed due to memory
FIX: Use smaller chunks and universe strategy
     python main.py --strategy universe --chunk-size weekly
```

### Checkpoint Not Resuming
```
ISSUE: --resume not working
CHECK: 
  - Checkpoint age (<24h)
  - .checkpoint directory exists
  - Not using --fresh flag
FIX: Check checkpoint with:
     ls -lh ultra_necrozma_results/.checkpoint/
```

### CPU Overheating
```
ISSUE: System throttling/overheating
FIX: 
  - Reduce --max-cpu threshold
  - Increase cooling intervals
  - Use universe strategy
     python main.py --strategy universe --max-cpu 75 \
       --cooling-chunk-interval 2
```

### Slow Processing
```
ISSUE: Taking too long
TRY:
  - Use chunked strategy (if enough RAM)
  - Increase workers (--workers N)
  - Use larger chunks (monthly)
  - Disable cooling (if safe)
```

---

## 📈 Monitoring Progress

The system displays detailed progress:
```
╔══════════════════════════════════════════════════════════════╗
║  🌟 ULTRA NECROZMA - Processing Progress                    ║
╚══════════════════════════════════════════════════════════════╝

📊 Configuration:
   Strategy:       universe
   Total tasks:    25
   
🔄 Progress:
   Current:        Universe 18/25
   Overall:        18/25 (72.0%)
   
⏱️  Timing:
   Elapsed:        8h 34min
   ETA:            2h 51min
   
💾 Resources:
   Memory:         2.3GB / 16.0GB (14%)
   CPU:            45.0%
```

---

## 🔄 Migration from Old Workflow

The old single-pass workflow still works! Chunking is opt-in:

```bash
# Old way (still works)
python main.py

# New chunked way
python main.py --chunk-size monthly --strategy auto
```

To migrate existing results:
1. Process with chunking enabled
2. Results are saved in same format
3. Compatible with existing analysis tools
4. No data conversion needed

---

## 📝 Additional Resources

- **Main README**: `/README.md`
- **Integration Tests**: `/tests/test_chunked_processing.py`
- **Module Docs**: See docstrings in each `.py` file
- **Configuration**: `/config.yaml`

---

**🌟 Happy Processing! 🌟**
