# NECROZMA Mass Testing System

## Overview

The Mass Testing System allows you to test NECROZMA strategies across multiple currency pairs and years automatically. This enables systematic evaluation of strategy performance across different market conditions.

## Features

- **Multi-Pair Testing**: Test all 10 supported currency pairs
- **Multi-Year Testing**: Test across years 2023, 2024, and 2025
- **Parallel Execution**: Run multiple tests simultaneously for faster results
- **Consolidated Reports**: Generate JSON and CSV summary reports
- **Flexible Filtering**: Test specific pairs or years as needed
- **Progress Tracking**: Real-time feedback on test execution

## Supported Pairs

- AUDJPY, AUDUSD
- EURGBP, EURJPY, EURUSD
- GBPJPY, GBPUSD
- USDCAD, USDCHF, USDJPY

**Total Combinations**: 10 pairs × 3 years = 30 backtests

## Installation

No additional dependencies beyond NECROZMA's requirements.

## Usage

### Basic Usage

Test all available pairs and years:
```bash
python run_mass_test.py
```

### List Available Datasets

See what data files are available:
```bash
python run_mass_test.py --list
```

### Test Specific Pairs

Test only EURUSD:
```bash
python run_mass_test.py --pair EURUSD
```

Test multiple pairs:
```bash
python run_mass_test.py --pair EURUSD GBPUSD USDJPY
```

### Test Specific Years

Test only 2024 data:
```bash
python run_mass_test.py --year 2024
```

Test multiple years:
```bash
python run_mass_test.py --year 2023 2024
```

### Combine Filters

Test EURUSD and GBPUSD for 2024 and 2025:
```bash
python run_mass_test.py --pair EURUSD GBPUSD --year 2024 2025
```

### Parallel Execution

Run 4 tests in parallel for faster execution:
```bash
python run_mass_test.py --parallel 4
```

**Note**: Parallel execution uses more CPU and memory. Adjust based on your system resources.

## Data Requirements

### Directory Structure

Place your parquet files in the `data/parquet/` directory:
```
data/parquet/
├── AUDJPY_2023.parquet
├── AUDJPY_2024.parquet
├── AUDJPY_2025.parquet
├── EURUSD_2023.parquet
├── EURUSD_2024.parquet
└── ...
```

### Naming Convention

Files must follow the pattern: `{PAIR}_{YEAR}.parquet`
- PAIR: Currency pair (e.g., EURUSD, GBPUSD)
- YEAR: Year (e.g., 2023, 2024, 2025)

## Output

### Reports Directory

Results are saved to `results/mass_test/`:
```
results/mass_test/
├── mass_test_report_20250127_120000.json
└── mass_test_summary_20250127_120000.csv
```

### JSON Report

Contains detailed results for each test including:
- Executive summary statistics
- Best strategy per pair
- Top 10 global strategies
- Strategy consistency analysis
- Full results for each pair/year

### CSV Summary

Tabular format with key metrics:
- Pair and year
- Best strategy name
- Sharpe ratio
- Total return
- Win rate
- Max drawdown
- Number of strategies tested
- Execution time

## Report Analysis

### Console Output

The system provides real-time progress updates:
```
⚡🌟💎 NECROZMA MASS TESTING SYSTEM 💎🌟⚡
======================================================================

📊 Found 30 datasets to test:
   • AUDJPY 2023: data/parquet/AUDJPY_2023.parquet
   • AUDJPY 2024: data/parquet/AUDJPY_2024.parquet
   ...

🚀 Running 30 tests sequentially...

✅ AUDJPY 2023: Sharpe 4.52, 44 strategies
✅ EURUSD 2024: Sharpe 6.29, 44 strategies
...

======================================================================
📊 MASS TEST SUMMARY REPORT
======================================================================

📈 Overall Statistics:
   Total tests: 30
   Successful: 30
   Failed: 0
   Total time: 45.2m

🏆 Best Strategy by Pair:
   EURUSD (2024): MeanReverter_L5_T1.8_SL20_TP40
      Sharpe: 6.29, Win Rate: 68.3%
```

### Global Top 10

The report includes the top 10 strategies across all pairs and years, sorted by Sharpe ratio. This helps identify strategies that perform well across different market conditions.

### Consistency Analysis

Shows how many times each strategy type appears in the results and their average Sharpe ratio, helping identify robust strategies.

## Strategies Tested

The system tests 44 strategy combinations:

### MeanReverter (8 strategies)
- Champion strategy from 10 rounds of backtesting
- Lookback: 5
- Thresholds: 1.8, 2.0
- Stop Loss: 20, 30 pips
- Take Profit: 40, 50 pips

### MeanReverterV2 (24 strategies)
- High volume strategy with consistent Sharpe
- Lookback: 30
- Thresholds: 0.8, 1.0, 1.5
- Stop Loss: 15, 20 pips
- Take Profit: 40, 50 pips
- RSI filters and volume confirmation

### MeanReverterV3 (12 strategies)
- Adaptive threshold strategy
- Lookback: 5
- Thresholds: 1.7, 1.8
- Stop Loss: 20, 25, 30 pips
- Take Profit: 45, 55 pips
- Adaptive threshold enabled

## Performance Considerations

### Sequential vs Parallel

**Sequential** (default):
- Safer for limited resources
- Easier to debug
- Predictable memory usage

**Parallel** (--parallel N):
- Faster completion
- Uses N CPU cores
- Requires N times the memory
- Recommended for powerful machines

### Execution Time

Approximate times (varies by data size):
- Sequential: ~1.5 minutes per pair/year
- Parallel (4 workers): ~4× faster for 30 tests

### Memory Usage

Each test loads a full parquet file into memory:
- Sequential: ~1-2 GB RAM
- Parallel: N × (1-2 GB) RAM

## Troubleshooting

### No Datasets Found

```
❌ No datasets found!
```

**Solution**: Check that parquet files exist in `data/parquet/` directory with correct naming pattern.

### Report Not Found

```
❌ EURUSD 2023: Report file not found
```

**Solution**: This usually means the backtest failed. Check the console output for errors during the test execution.

### Out of Memory

**Solution**: 
- Use sequential mode instead of parallel
- Test fewer pairs/years at once
- Reduce data size if possible

### Permission Errors

**Solution**: Ensure `run_mass_test.py` is executable:
```bash
chmod +x run_mass_test.py
```

## Integration with NECROZMA

The mass testing system integrates seamlessly with NECROZMA:

1. Uses the same configuration from `config.py`
2. Temporarily overrides `PARQUET_FILE` for each test
3. Sets `FILE_PREFIX` to include pair/year for unique report names
4. Uses existing `main.py` execution flow
5. Collects reports from standard output directory

## Advanced Usage

### Custom Analysis

Load the JSON report for custom analysis:
```python
import json

with open('results/mass_test/mass_test_report_20250127_120000.json') as f:
    report = json.load(f)

# Analyze results
for result in report['results']:
    if result['status'] == 'success':
        print(f"{result['pair']} {result['year']}: "
              f"Sharpe {result['avg_sharpe']:.2f}")
```

### CSV Analysis

Use pandas to analyze the CSV summary:
```python
import pandas as pd

df = pd.read_csv('results/mass_test/mass_test_summary_20250127_120000.csv')
print(df.groupby('pair')['sharpe_ratio'].mean())
```

## Best Practices

1. **Test Incrementally**: Start with a few pairs/years before running all 30 tests
2. **Use --list First**: Verify your data files are recognized correctly
3. **Monitor Resources**: Watch CPU and memory usage during parallel execution
4. **Backup Results**: Save important reports before running new tests
5. **Sequential for Debugging**: Use sequential mode when troubleshooting issues

## Future Enhancements

Potential improvements for future versions:
- Resume interrupted test runs
- Real-time dashboard during execution
- Email/notification when tests complete
- Automated comparison across test runs
- Strategy parameter optimization based on results

## License

Part of the NECROZMA project.
