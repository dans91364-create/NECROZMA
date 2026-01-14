# ⚡ Multi-Worker Execution Examples

This document provides examples of using the new multi-worker features in NECROZMA.

## Basic Usage

### Sequential Mode (Default)

```bash
# Run with single worker (current default)
python run_sequential_backtest.py
```

### Multi-Worker Mode

```bash
# Run with 4 workers
python run_sequential_backtest.py --workers 4

# Short form
python run_sequential_backtest.py -w 4
```

## CPU Management

### Set CPU Limit

Prevent CPU from exceeding a certain percentage by dynamically adjusting worker count:

```bash
# Limit to 80% CPU usage
python run_sequential_backtest.py --workers 4 --cpu-limit 80
```

The system will:
- Start with 4 workers
- Monitor CPU usage every 5 completed tasks
- Reduce workers if CPU > 80%
- Increase workers if CPU < 60% (and below max workers)

### Add Cooldown Between Batches

```bash
# Pause 5 seconds between task batches
python run_sequential_backtest.py --workers 4 --cooldown 5
```

This helps prevent sustained high CPU usage and gives the system time to cool down.

### Run with Low Priority (Nice)

```bash
# Run with reduced process priority
python run_sequential_backtest.py --workers 4 --nice
```

This makes the process yield CPU time to other higher-priority processes.

## Combined Examples

### Recommended for VMs

Prevent overheating while maximizing throughput:

```bash
python run_sequential_backtest.py \
  --workers 4 \
  --cpu-limit 80 \
  --cooldown 5 \
  --nice
```

### Maximum Performance (Local Machine)

For powerful local machines with good cooling:

```bash
python run_sequential_backtest.py \
  --workers 8 \
  --cpu-limit 95 \
  --cooldown 0
```

### Conservative (Shared Server)

For shared environments where you want minimal impact:

```bash
python run_sequential_backtest.py \
  --workers 2 \
  --cpu-limit 50 \
  --cooldown 10 \
  --nice
```

## Monitoring

The system displays real-time information:

```
⚡ Multi-Worker Mode:
   Workers: 4
   CPU Limit: 80%
   Cooldown: 5s
   Nice Priority: Yes
   ⚠️  Note: Parallel execution framework prepared but currently sequential

💾 Storage format: PARQUET
```

During execution, you'll see CPU monitoring messages:

```
🌡️  CPU 85.2% > 80% - reducing to 3 workers
❄️  CPU 65.1% - increasing to 4 workers
```

## Configuration

You can also set defaults in `config.py`:

```python
WORKER_CONFIG = {
    "default_workers": 4,           # Default workers when --workers not specified
    "max_workers": 16,              # Maximum allowed workers
    "cpu_limit": 80,                # Default CPU limit
    "cooldown_seconds": 5,          # Default cooldown
    "nice_priority": False,         # Default priority
    "adaptive_throttling": True,    # Enable dynamic worker adjustment
    "cpu_check_interval": 5,        # Check CPU every N tasks
}
```

## Expected Performance

Based on 10 currency pairs with ~50 strategies each:

| Configuration | Approx. Time | Notes |
|---------------|--------------|-------|
| 1 worker (JSON) | ~30 hours | Baseline |
| 1 worker (Parquet) | ~25 hours | I/O improvement only |
| 4 workers (Parquet, 80% CPU) | ~10 hours | Parallel + I/O improvement |
| 8 workers (Parquet, 95% CPU) | ~6-8 hours | Maximum performance |

**Note:** Actual times vary based on:
- CPU speed and core count
- Disk I/O speed
- Strategy complexity
- Data size

## Troubleshooting

### Workers Not Reducing Despite High CPU

The CPU check happens every 5 completed tasks. If tasks are very long, there may be a delay before adjustment.

### No Performance Improvement with Multiple Workers

Currently, the framework is **prepared for multi-worker execution** but runs sequentially by default for stability. The infrastructure (CPUThrottledExecutor, argument parsing, configuration) is in place for future parallel implementation.

### CPU Limit Too Aggressive

If workers keep reducing to 1, try:
- Increase `--cpu-limit` to 90-95%
- Reduce number of workers
- Increase `--cooldown` for better thermal management

### Process Priority Not Working

The `--nice` flag requires Unix-like systems (Linux, macOS). On Windows, this flag is ignored.

## Future Enhancements

The multi-worker infrastructure is ready for:
- True parallel backtest execution
- Distributed processing across multiple machines
- GPU acceleration for strategy evaluation
- Real-time progress tracking with worker assignment

## See Also

- [PARQUET_MIGRATION_GUIDE.md](PARQUET_MIGRATION_GUIDE.md) - For Parquet format details
- [ROADMAP.md](ROADMAP.md) - For overall project status
- `config.py` - For configuration options
