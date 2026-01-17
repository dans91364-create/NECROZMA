# 🎯 NECROZMA Dashboard 2.0 - Batch Processing Edition

## Overview

The NECROZMA Dashboard has been completely upgraded to support the new batch processing data format. This version can analyze **13,860+ strategies** efficiently using parquet files while maintaining backward compatibility with legacy JSON format.

## 🚀 What's New in 2.0

### Data Format Support
- ✅ **Parquet Support**: Fast loading of batch processing results (13,860+ rows, 0.44 MB)
- ✅ **Automatic Detection**: Seamlessly switches between parquet and JSON formats
- ✅ **Backward Compatible**: Legacy JSON format still fully supported

### New Pages

#### 1. 📈 Performance Matrix (NEW)
- Heatmap visualization of strategy templates vs lot sizes
- Identify best performing template/lot size combinations
- Template and lot size impact analysis
- Visual performance comparison across dimensions

#### 2. 🎯 Strategy Explorer (Enhanced)
- Search and filter strategies by name
- **Compare up to 5 strategies** side-by-side
- Detailed metrics breakdown
- Parameter extraction from strategy names
- Visual metric comparison charts

#### 3. 💰 Profitability Analysis (NEW)
- Net PnL ranking and distribution
- Gross PnL vs Commission analysis
- Profit Factor distribution
- Expectancy analysis
- Top performers by profitability metrics

#### 4. 🔧 Lot Size Analysis (NEW)
- Compare same strategy across lot sizes (0.01, 0.1, 1.0)
- Optimal lot size recommendations
- PnL scaling analysis
- Commission impact by lot size
- Interactive lot size comparison charts

#### 5. 📊 Strategy Templates (NEW)
- Performance by template type (TrendFollower, MeanReverter, etc.)
- Best parameters per template
- Template comparison and ranking
- Risk-return profiles by template
- Consistency and peak performance analysis

#### 6. 📤 Export (NEW)
- Export filtered results to CSV, JSON, or Parquet
- Export top N strategies for deployment
- Generate strategy configuration files
- Customizable export criteria

### Enhanced Pages

#### 📊 Overview (Enhanced)
- Parquet data format support
- Advanced filtering (lot size, template, metrics)
- Distribution charts for all metrics
- Enhanced top strategies table
- Viable strategy percentage tracking

#### ⚠️ Risk Analysis (Enhanced)
- Risk tier classification (Low/Medium/High)
- Sortino vs Calmar comparison
- Enhanced efficient frontier visualization
- Distribution analysis for risk metrics
- Risk-adjusted return scatter plots

## 📊 Data Format Details

### Parquet Format (Batch Processing)
```
Columns:
- strategy_name: Strategy identifier
- lot_size: Position size (0.01, 0.1, 1.0)
- sharpe_ratio: Risk-adjusted return metric
- sortino_ratio: Downside risk-adjusted metric
- calmar_ratio: Drawdown-adjusted metric
- total_return: Total return percentage
- max_drawdown: Maximum drawdown percentage
- win_rate: Win rate (0-1)
- n_trades: Number of trades
- profit_factor: Profit/Loss ratio
- avg_win: Average winning trade
- avg_loss: Average losing trade
- expectancy: Expected value per trade
- gross_pnl: Gross profit/loss
- net_pnl: Net profit/loss (after commission)
- total_commission: Total commission paid

Scale: 4,620 strategies × 3 lot sizes = 13,860 rows
File size: ~0.44 MB
```

### Legacy JSON Format
- Supports existing `all_strategies_metrics.json`
- Supports `universe_*_backtest.json` files
- Automatically fills missing columns for compatibility

## 🔧 Installation & Setup

### Requirements
```bash
pip install -r requirements-dashboard.txt
```

Required packages:
- streamlit >= 1.28.0
- plotly >= 5.17.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- pyarrow >= 14.0.0 (NEW for parquet support)
- seaborn >= 0.12.0

### Running the Dashboard
```bash
streamlit run dashboard/app.py
```

The dashboard will automatically detect and load:
1. Parquet files from `ultra_necrozma_results/EURUSD_2025_backtest_results_merged.parquet`
2. JSON files from `ultra_necrozma_results/backtest_results/all_strategies_metrics.json`
3. Legacy universe files from `ultra_necrozma_results/backtest_results/universe_*_backtest.json`

## 📖 User Guide

### Navigation
The dashboard has 9+ pages accessible from the sidebar:

1. **Overview** - Start here for global summary
2. **Performance Matrix** - Analyze template vs lot size performance
3. **Strategy Explorer** - Search and compare specific strategies
4. **Risk Analysis** - Assess risk-adjusted returns
5. **Profitability** - Analyze PnL and commission impact
6. **Lot Size Analysis** - Optimize position sizing
7. **Strategy Templates** - Compare strategy types
8. **Top Performers** - Multi-criteria rankings
9. **Export** - Download results and configs

### Filtering System

Available on parquet-enabled pages:

**Lot Size Filter**
- Multi-select: 0.01, 0.1, 1.0
- Filter strategies by position size

**Strategy Template Filter**
- Auto-extracted from strategy names
- Examples: TrendFollower, MeanReverter, BreakoutTrader

**Performance Filters**
- Min Sharpe Ratio: 0-5 (slider)
- Min Win Rate: 0-100% (slider)
- Max Drawdown: 0-50% (slider)
- Min Trades: 0-1000 (slider)

**Reset Button**
- Quickly reset all filters to defaults

### Key Metrics Cards

Displayed prominently on all pages:
- **Total Strategies**: Total count in dataset
- **Viable Strategies**: Count with Sharpe > 1.0 and WR > 50%
- **Best Sharpe**: Highest Sharpe ratio
- **Best Return**: Highest total return
- **Average Win Rate**: Mean win rate
- **Average Drawdown**: Mean maximum drawdown

### Visualizations

All charts are interactive (Plotly-based):
- **Zoom**: Click and drag to zoom
- **Pan**: Hold and drag to pan
- **Hover**: View detailed tooltips
- **Export**: Download charts as PNG
- **Reset**: Double-click to reset view

Chart types:
- Heatmaps (Performance Matrix)
- Bar charts (Rankings, distributions)
- Scatter plots (Risk-return analysis)
- Box plots (Distribution analysis)
- Line charts (Trend analysis)
- Pie charts (Category breakdowns)

### Export Features

**Export Formats**
- CSV: Universal format (Excel, Python, R)
- JSON: API and web application ready
- Parquet: Efficient binary format
- Config: Deployment-ready strategy configs

**Export Options**
1. All results (complete dataset)
2. Filtered results (current filter settings)
3. Top N strategies (by selected metric)
4. Strategy configurations (for deployment)

## 🎨 Design Features

### NECROZMA Theme
- Purple/gold gradient headers
- Pokemon-inspired design elements
- Dark mode compatible
- Responsive layout (desktop, tablet, mobile)

### Performance Optimizations
- Streamlit caching (`@st.cache_data`, TTL=300s)
- Efficient parquet loading (~0.44 MB for 13,860 rows)
- Lazy loading of detailed data
- Pagination for large result sets

## 🔍 Strategy Template Extraction

The dashboard automatically extracts strategy templates from strategy names:

```python
Strategy Name Format:
TrendFollower_L5_T0.5_SL10_TP50
    ↓
Template: TrendFollower

MeanReverter_params_lot_0.1
    ↓
Template: MeanReverter
```

Supported templates:
- TrendFollower
- MeanReverter
- BreakoutTrader
- ScalpingStrategy
- MomentumStrategy
- (and any custom templates)

## 💡 Usage Examples

### Example 1: Find Best Template/Lot Size Combination
1. Go to **Performance Matrix**
2. Select metric: Sharpe Ratio
3. View heatmap to identify best combinations
4. Note highest values (green cells)

### Example 2: Compare Strategies
1. Go to **Strategy Explorer**
2. Search for keywords (e.g., "TrendFollower")
3. Select up to 5 strategies
4. View side-by-side comparison
5. Export comparison as CSV

### Example 3: Optimize Lot Size
1. Go to **Lot Size Analysis**
2. Select a strategy from dropdown
3. View performance across lot sizes
4. Check optimal lot size recommendations
5. Analyze commission impact

### Example 4: Export Top Performers
1. Go to **Export**
2. Select "Export Top N Strategies"
3. Choose number (e.g., 50) and metric (e.g., Sharpe Ratio)
4. Download CSV, JSON, or Parquet
5. Optional: Download strategy config for deployment

## 🐛 Troubleshooting

### Dashboard shows "No backtest results found"
- Ensure parquet or JSON files exist in expected locations
- Check file permissions
- Verify data format with validation script:
  ```bash
  python validate_dashboard_structure.py
  ```

### Charts not displaying
- Clear browser cache
- Reload page (Ctrl+R or Cmd+R)
- Check browser console for errors

### Filters not working
- Click "Reset All Filters" button
- Refresh the page
- Ensure data has the required columns

### Performance issues
- Reduce number of strategies displayed
- Use pagination on large datasets
- Close unused browser tabs
- Increase cache TTL if data doesn't change often

## 📝 Technical Details

### Architecture
```
dashboard/
├── app.py                          # Main entry point
├── utils/
│   ├── data_loader.py              # Parquet/JSON loading
│   ├── formatters.py               # Display formatting
│   └── trade_analyzer.py           # Trade analysis
├── components/
│   ├── charts.py                   # Plotly chart creation
│   ├── filters.py                  # Filter components
│   ├── metrics.py                  # Metric calculations
│   └── tables.py                   # Table components
└── pages/
    ├── 1_📊_Overview.py
    ├── 2_📈_Performance_Matrix.py
    ├── 3_🎯_Strategy_Explorer.py
    ├── 4_⚠️_Risk_Analysis.py
    ├── 5_💰_Profitability.py
    ├── 6_🔧_Lot_Size_Analysis.py
    ├── 7_📊_Strategy_Templates.py
    ├── 8_🏆_Top_Performers.py
    └── 9_📤_Export.py
```

### Data Loading Priority
1. **Parquet** (fastest): `ultra_necrozma_results/EURUSD_2025_backtest_results_merged.parquet`
2. **Smart Storage**: `backtest_results/all_strategies_metrics.json`
3. **Legacy**: `backtest_results/universe_*_backtest.json`

### Caching Strategy
- All data loading functions use `@st.cache_data(ttl=300)`
- Cache refreshes every 5 minutes
- Manual refresh: Restart dashboard

## 🚀 Future Enhancements

Potential improvements for future versions:
- [ ] Real-time data updates
- [ ] Custom metric calculations
- [ ] Advanced statistical analysis
- [ ] Machine learning insights
- [ ] Portfolio optimization
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Parameter sensitivity analysis

## 📄 Version History

### Version 2.0.0 (Batch Processing Edition)
- Added parquet file support
- Created 5 new analysis pages
- Enhanced 3 existing pages
- Added comprehensive filtering system
- Added multi-format export
- Improved performance for large datasets
- Added strategy template analysis
- Added lot size optimization

### Version 1.0.0
- Initial release
- JSON format support
- Basic analysis pages
- Simple filtering

## 📧 Support

For issues or questions:
1. Check this README
2. Review the validation script output
3. Check the main NECROZMA documentation
4. Submit an issue on GitHub

---

**Built with ❤️ for the NECROZMA Project**

© 2024-2026 NECROZMA - "The Light That Burns The Sky - Visualized"
