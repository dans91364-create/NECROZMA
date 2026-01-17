#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - EXPORT PAGE 💎🌟⚡

Export filtered results and top strategies
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format, extract_strategy_template
from dashboard.components.filters import create_parquet_filters, show_filter_summary
from dashboard.components.metrics import get_top_strategies, calculate_composite_score

# Page config
st.set_page_config(page_title="Export", page_icon="📤", layout="wide")

st.title("📤 Export Data")
st.markdown("Export filtered results, top strategies, and configuration files")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

# Add template column
if 'strategy_name' in strategies_df.columns:
    strategies_df['template'] = strategies_df['strategy_name'].apply(extract_strategy_template)

st.markdown("---")

# Export Options
st.header("📁 Export Options")

export_option = st.radio(
    "Select Export Type",
    [
        "Export All Results",
        "Export Filtered Results",
        "Export Top N Strategies",
        "Export Strategy Config"
    ]
)

st.markdown("---")

# Apply filters
filtered_df = strategies_df.copy()

if export_option == "Export Filtered Results":
    st.subheader("🔍 Apply Filters")
    
    if data_format == 'parquet':
        filters = create_parquet_filters(strategies_df)
        
        # Apply filters
        if 'lot_size' in filters and filters['lot_size']:
            filtered_df = filtered_df[filtered_df['lot_size'].isin(filters['lot_size'])]
        
        if 'template' in filters and filters['template']:
            filtered_df = filtered_df[filtered_df['template'].isin(filters['template'])]
        
        if 'sharpe_ratio' in filters:
            min_val, max_val = filters['sharpe_ratio']
            filtered_df = filtered_df[(filtered_df['sharpe_ratio'] >= min_val) & (filtered_df['sharpe_ratio'] <= max_val)]
        
        if 'win_rate' in filters:
            min_val, max_val = filters['win_rate']
            filtered_df = filtered_df[(filtered_df['win_rate'] >= min_val) & (filtered_df['win_rate'] <= max_val)]
        
        if 'n_trades' in filters:
            min_val, max_val = filters['n_trades']
            filtered_df = filtered_df[(filtered_df['n_trades'] >= min_val) & (filtered_df['n_trades'] <= max_val)]
    
    show_filter_summary(len(strategies_df), len(filtered_df))

elif export_option == "Export Top N Strategies":
    st.subheader("🏆 Top Strategies Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_n = st.number_input("Number of Strategies", min_value=1, max_value=1000, value=50)
    
    with col2:
        sort_by = st.selectbox(
            "Sort By",
            ['sharpe_ratio', 'total_return', 'win_rate', 'profit_factor', 'net_pnl'],
            index=0
        )
    
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.nlargest(top_n, sort_by)
        st.info(f"📊 Selected top {len(filtered_df)} strategies by {sort_by}")
    else:
        st.warning(f"Column '{sort_by}' not available")

elif export_option == "Export Strategy Config":
    st.subheader("⚙️ Strategy Configuration Export")
    
    st.info("Export strategy configurations for deployment")
    
    # Select top strategies
    top_n = st.number_input("Number of Strategies to Export", min_value=1, max_value=100, value=10)
    
    if 'sharpe_ratio' in strategies_df.columns:
        filtered_df = strategies_df.nlargest(top_n, 'sharpe_ratio')
        st.success(f"Selected top {len(filtered_df)} strategies by Sharpe Ratio")

st.markdown("---")

# Preview
st.header("👀 Preview Export Data")

if not filtered_df.empty:
    st.dataframe(filtered_df.head(300), use_container_width=True)
    st.info(f"Total rows to export: {len(filtered_df)}")
else:
    st.warning("No data to export with current filters")

st.markdown("---")

# Export Buttons
st.header("💾 Download Files")

if not filtered_df.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Export
        st.subheader("CSV Format")
        csv_data = filtered_df.to_csv(index=False)
        
        filename = "necrozma_export.csv"
        if export_option == "Export Top N Strategies":
            filename = f"top_{len(filtered_df)}_strategies.csv"
        elif export_option == "Export Filtered Results":
            filename = "filtered_strategies.csv"
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON Export
        st.subheader("JSON Format")
        json_data = filtered_df.to_json(orient='records', indent=2)
        
        filename_json = filename.replace('.csv', '.json')
        
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=filename_json,
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Parquet Export
        st.subheader("Parquet Format")
        
        # Create parquet bytes
        parquet_buffer = filtered_df.to_parquet(index=False)
        
        filename_parquet = filename.replace('.csv', '.parquet')
        
        st.download_button(
            label="📥 Download Parquet",
            data=parquet_buffer,
            file_name=filename_parquet,
            mime="application/octet-stream",
            use_container_width=True
        )

st.markdown("---")

# Strategy Config Export
if export_option == "Export Strategy Config":
    st.header("⚙️ Strategy Configuration Files")
    
    st.info("Generate configuration files for top strategies")
    
    if 'strategy_name' in filtered_df.columns:
        # Create config dictionary
        config_data = {
            'version': '1.0',
            'generated_by': 'NECROZMA Dashboard',
            'total_strategies': len(filtered_df),
            'strategies': []
        }
        
        for _, row in filtered_df.iterrows():
            strategy_config = {
                'name': row.get('strategy_name', ''),
                'template': row.get('template', ''),
            }
            
            # Add available parameters
            if 'lot_size' in row:
                strategy_config['lot_size'] = float(row['lot_size'])
            
            # Add performance metrics
            metrics = {}
            for metric in ['sharpe_ratio', 'total_return', 'win_rate', 'max_drawdown', 'profit_factor', 'n_trades']:
                if metric in row and pd.notna(row[metric]):
                    metrics[metric] = float(row[metric])
            
            if metrics:
                strategy_config['metrics'] = metrics
            
            config_data['strategies'].append(strategy_config)
        
        # Display preview
        st.subheader("Config Preview (First 3 Strategies)")
        preview_config = config_data.copy()
        preview_config['strategies'] = preview_config['strategies'][:3]
        st.json(preview_config)
        
        # Download button
        config_json = json.dumps(config_data, indent=2)
        
        st.download_button(
            label="📥 Download Strategy Config",
            data=config_json,
            file_name="strategy_config.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("---")

# Export Statistics
st.header("📊 Export Statistics")

if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Strategies to Export", len(filtered_df))
    
    with col2:
        if 'sharpe_ratio' in filtered_df.columns:
            st.metric("Avg Sharpe", f"{filtered_df['sharpe_ratio'].mean():.2f}")
    
    with col3:
        if 'win_rate' in filtered_df.columns:
            wr = filtered_df['win_rate'].mean()
            if wr <= 1:
                wr = wr * 100
            st.metric("Avg Win Rate", f"{wr:.1f}%")
    
    with col4:
        if 'net_pnl' in filtered_df.columns:
            st.metric("Total Net PnL", f"${filtered_df['net_pnl'].sum():,.2f}")

st.markdown("---")

# Export Summary
st.header("📝 Export Summary")

st.markdown("""
### Files Available for Download:

1. **CSV** - Universal format, compatible with Excel, Python, R
2. **JSON** - Structured format for APIs and web applications
3. **Parquet** - Efficient binary format for data analysis
4. **Strategy Config** - Deployment-ready configuration file

### Next Steps:

- 📊 Analyze exported data in your preferred tool
- 🚀 Deploy top strategies to live trading
- 📈 Track performance over time
- 🔄 Re-run analysis with updated filters
""")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Export filtered results regularly to track strategy performance evolution")
