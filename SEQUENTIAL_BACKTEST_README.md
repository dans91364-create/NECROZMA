# 🌟 Sequential Backtesting Runner - Documentation

## Overview

The `run_sequential_backtest.py` script loads processed universe results and executes backtesting sequentially with CPU management and cooling breaks. This is the second phase of the ULTRA NECROZMA analysis pipeline.

## 📋 Requirements

### Input Data
- Universe result JSON files in `ultra_necrozma_results/` directory
- Expected format: `universe_NNN_Xmin_Ylb.json`
- Each file should contain:
  - `interval`: Time interval in minutes
  - `lookback`: Lookback period
  - `total_patterns`: Number of patterns found
  - `features`: Dictionary of calculated features
  - `patterns`: List of discovered patterns (optional)

### Dependencies
- Python 3.8+
- pandas
- numpy
- scikit-learn
- psutil (optional, for CPU monitoring)

## 🚀 Usage

### Basic Usage
```bash
# Process all universes with default settings
python run_sequential_backtest.py

# Skip Telegram notifications
python run_sequential_backtest.py --skip-telegram
```

### Advanced Usage

#### Select Specific Universes
```bash
# Single universe
python run_sequential_backtest.py --universes 1

# Multiple universes
python run_sequential_backtest.py --universes 1,5,10

# Range of universes
python run_sequential_backtest.py --universes 1-5

# Mixed selection
python run_sequential_backtest.py --universes 1,5,10-15,25
```

#### Adjust CPU and Cooling Settings
```bash
# Lower CPU threshold (more conservative)
python run_sequential_backtest.py --cpu-threshold 75

# Longer cooling breaks
python run_sequential_backtest.py --cooling-duration 180

# Combined settings
python run_sequential_backtest.py --cpu-threshold 80 --cooling-duration 150
```

#### Control Strategy Generation
```bash
# Limit strategies per universe (faster, less comprehensive)
python run_sequential_backtest.py --max-strategies 20

# More strategies per universe (slower, more comprehensive)
python run_sequential_backtest.py --max-strategies 100
```

#### Custom Results Directory
```bash
# Use different input directory
python run_sequential_backtest.py --results-dir /path/to/results

# Verbose output for debugging
python run_sequential_backtest.py --verbose
```

### Complete Example
```bash
python run_sequential_backtest.py \
  --universes 1-10,15,20-25 \
  --cpu-threshold 80 \
  --cooling-duration 150 \
  --skip-telegram \
  --max-strategies 75 \
  --verbose
```

## 📊 Output Structure

### Output Directory
```
ultra_necrozma_results/backtest_results/
├── universe_001_5min_5lb_backtest.json      # Individual universe results
├── universe_002_5min_10lb_backtest.json
├── ...
├── consolidated_backtest_results.json       # All universes combined
├── top_strategies_ranked.json               # Ranked top strategies
└── LIGHT_REPORT_YYYYMMDD_HHMMSS.json       # Final comprehensive report
```

### Output Files

#### Individual Universe Backtest Files
- Filename: `universe_NNN_Xmin_Ylb_backtest.json`
- Contains:
  - Universe metadata (interval, lookback, patterns count)
  - Backtest statistics (total/successful/failed strategies)
  - Results array with all strategy performance metrics

#### Consolidated Results
- Filename: `consolidated_backtest_results.json`
- Contains:
  - Summary of all processed universes
  - Best strategies per universe
  - Processing times and statistics

#### Ranked Strategies
- Filename: `top_strategies_ranked.json`
- Contains:
  - Top N strategies (default: 20) ranked by composite score
  - Multi-objective scoring (return, risk, consistency, robustness)
  - Detailed performance metrics for each strategy

#### Light Report
- Filename: `LIGHT_REPORT_YYYYMMDD_HHMMSS.json`
- Contains:
  - Executive summary
  - Top strategies with detailed analysis
  - Feature insights (if available)
  - Regime analysis (if available)
  - Implementation guide
  - Risk management recommendations
  - Warnings and disclaimers

## 🎯 Performance Metrics

Each strategy is evaluated on:

- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside risk-adjusted returns
- **Calmar Ratio**: Return vs maximum drawdown
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss
- **Total Return**: Overall profit/loss percentage
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Expectancy**: Average profit per trade
- **Recovery Factor**: Return / max drawdown
- **Ulcer Index**: Depth and duration of drawdowns

## 🏆 Strategy Ranking

Strategies are ranked using a composite score based on:

1. **Return Score (30%)**: Total return
2. **Risk Score (25%)**: Inverse of drawdown
3. **Consistency Score (25%)**: Win rate + Sharpe + Sortino
4. **Robustness Score (20%)**: Profit factor + Ulcer index

Viable strategies are those with:
- Sharpe Ratio > 1.0
- Minimum number of trades (typically 30+)
- Reasonable risk/reward profile

## ❄️ CPU Management

### Cooling Breaks
- Triggered every 5 universes
- Duration: 120 seconds (configurable)
- Activated when CPU > 85% (configurable)
- Displays real-time CPU and RAM stats during cooling

### Monitoring (with psutil)
```
❄️  COOLING BREAK - CPU too high (87.2%)
   Waiting 120s...
   120s | CPU:  87.2% | RAM:  42.3GB
   110s | CPU:  84.1% | RAM:  41.8GB
   100s | CPU:  82.5% | RAM:  41.5GB
   ...
   ✅ Resumed
```

### Fallback Mode (without psutil)
- Simple time-based pauses
- No real-time monitoring
- Still enforces cooling breaks

## 🔧 Troubleshooting

### No Universe Files Found
```
❌ No universe files found in ultra_necrozma_results
```
**Solution**: Ensure universe processing has been completed first using the discovery pipeline.

### Memory Issues
- Reduce `--max-strategies` to generate fewer strategies
- Process fewer universes at a time using `--universes`
- Increase `--cooling-duration` for more aggressive memory cleanup

### Slow Performance
- Increase `--max-strategies` cap (paradoxically can be faster by reducing overhead)
- Reduce number of universes processed
- Use `--skip-telegram` to disable notifications

### High CPU Usage
- Lower `--cpu-threshold` (e.g., to 75 or 70)
- Increase `--cooling-duration` for longer breaks
- Install `psutil` for better monitoring: `pip install psutil`

## 📝 Example Output

```
═══════════════════════════════════════════════════════════
🌟 ULTRA NECROZMA - Sequential Backtesting
═══════════════════════════════════════════════════════════

📂 Loading universe results...
   Found 25 universe files

──────────────────────────────────────────────────────────
📊 Universe 1/25: universe_001_5min_5lb
──────────────────────────────────────────────────────────
   🏭 Generating strategies...
   📈 Generated 52 strategies
   📊 Backtesting... (CPU: 68.3%)
   ✅ Complete! Best Sharpe: 2.34
   💾 Saved: universe_001_5min_5lb_backtest.json
   ⏱️  Time: 145.2s

... (continues for all 25 universes) ...

═══════════════════════════════════════════════════════════
🎉 BACKTESTING COMPLETE!
═══════════════════════════════════════════════════════════

📊 Summary:
   Total Universes: 25
   Total Strategies Tested: 1,287
   Viable Strategies (Sharpe > 1.0): 342
   Best Overall Sharpe: 3.45
   Total Time: 2.3 hours

🏆 Top 5 Strategies:
   #1 MeanReverter_L20_T2.0 (Sharpe: 3.45, Return: 45.2%)
   #2 TrendFollower_L15_T1.5 (Sharpe: 3.21, Return: 38.7%)
   ...

💾 Results saved to:
   📄 consolidated_backtest_results.json
   📄 top_strategies_ranked.json
   📄 LIGHT_REPORT_20260112_143022.json
```

## 🔗 Integration with Pipeline

This script is part of the ULTRA NECROZMA analysis pipeline:

1. **Discovery Phase**: Process raw data → Generate universe results
   - Script: `run_sequential_discovery.py`
   - Output: `ultra_necrozma_results/universe_*.json`

2. **Backtesting Phase** (this script): Load universes → Backtest strategies
   - Script: `run_sequential_backtest.py`
   - Output: `ultra_necrozma_results/backtest_results/`

3. **Deployment Phase**: Implement top strategies in production
   - Use Light Report recommendations
   - Monitor performance
   - Adapt to regime changes

## 🎨 Theme and Style

The script follows the ULTRA NECROZMA (Pokemon) theme:
- Uses emojis consistently (🌟, 💎, ⚡, 📊, etc.)
- Lore system with deity messages (when Telegram enabled)
- ASCII art and formatted output
- Progress tracking with visual feedback

## ⚠️ Important Notes

1. **Past Performance**: Results do not guarantee future performance
2. **Market Conditions**: Strategies may perform differently in live trading
3. **Risk Management**: Always use proper position sizing and stop losses
4. **Transaction Costs**: Backtest results don't include slippage or commissions
5. **Overfitting**: High in-sample performance may not translate to live trading

## 📚 References

- Backtester: `backtester.py`
- Strategy Factory: `strategy_factory.py`
- Light Finder: `light_finder.py`
- Light Report: `light_report.py`
- Lore System: `lore.py`
