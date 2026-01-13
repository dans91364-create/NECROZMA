# 🎨 NECROZMA Dashboard

Interactive Streamlit dashboard for analyzing backtesting results.

## Features

- 📊 **Overview**: Global performance summary across all strategies
- 🌍 **Universe Analysis**: Compare 25 universes side-by-side
- 🎯 **Strategy Deep Dive**: Detailed strategy metrics and equity curves
- 🔧 **SL/TP Optimization**: Find optimal risk/reward parameters
- ⚠️ **Risk Analysis**: Return vs drawdown visualization
- 💰 **Trade Analysis**: Best/worst trades with market context

## Installation

```bash
pip install -r requirements-dashboard.txt
```

## Usage

1. First, run backtests to generate results:
```bash
python run_sequential_backtest.py
```

2. Launch the dashboard:
```bash
streamlit run dashboard/app.py
```

3. Open your browser to http://localhost:8501

## Navigation

Use the sidebar to navigate between pages. Each page has:
- Interactive filters
- Zoomable/pannable Plotly charts
- Exportable data tables
- Real-time updates

## Data Sources

The dashboard loads data from:
- `ultra_necrozma_results/backtest_results/*.json` - Individual universe backtest results
- `ultra_necrozma_results/backtest_results/consolidated_backtest_results.json` - Aggregated results

## Export

Each page includes download buttons to export:
- CSV files of filtered data
- PNG images of charts
- Summary statistics

## Tips

- **Performance**: The dashboard caches data for fast navigation
- **Filtering**: Use multi-select and sliders to drill down
- **Comparison**: Open multiple strategies in tabs for side-by-side comparison
- **Mobile**: Dashboard is responsive and works on tablets

## Requirements

- Python 3.8+
- Streamlit 1.28+
- Plotly 5.17+
- Pandas 2.0+

## Troubleshooting

**Dashboard won't start:**
- Ensure `requirements-dashboard.txt` dependencies are installed
- Check that backtest results exist in `ultra_necrozma_results/`

**No data showing:**
- Run `run_sequential_backtest.py` first to generate results
- Verify JSON files exist in `backtest_results/` directory

**Charts not rendering:**
- Update Plotly: `pip install --upgrade plotly`
- Clear browser cache and refresh

## Development

To add new pages:
1. Create file in `dashboard/pages/` with format: `N_🔷_Page_Name.py`
2. Import necessary utilities from `dashboard/utils/`
3. Follow existing page structure
4. Use `@st.cache_data` for expensive computations
