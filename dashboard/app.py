#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Interactive Dashboard 💎🌟⚡

Streamlit-based interactive dashboard for analyzing backtest results

"The Light That Burns The Sky - Visualized"
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="NECROZMA Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">⚡🌟💎 NECROZMA Dashboard 💎🌟⚡</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">"The Light That Burns The Sky - Visualized"</p>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
## Welcome to NECROZMA Dashboard

This interactive dashboard provides comprehensive analysis of backtesting results across multiple strategies and configurations.

### 📊 Available Pages

Navigate using the sidebar to explore:

- **📊 Overview**: Global performance summary and top strategies with filtering
- **📈 Performance Matrix**: Heatmap analysis of templates vs lot sizes
- **🎯 Strategy Explorer**: Search, filter, and compare up to 5 strategies side-by-side
- **⚠️ Risk Analysis**: Analyze risk-adjusted returns, drawdowns, and risk tiers
- **💰 Profitability**: Net PnL analysis, commission impact, and expectancy
- **🔧 Lot Size Analysis**: Compare strategies across different lot sizes
- **📊 Strategy Templates**: Performance by template type with parameter analysis
- **🏆 Top Performers**: Multi-criteria ranking and composite scores
- **📤 Export**: Download filtered results, top strategies, and config files

### 🚀 Getting Started

1. Ensure you have backtest results (parquet or JSON format)
2. Select a page from the sidebar to begin analysis
3. Use filters to drill down into specific strategies or conditions
4. Export data and charts as needed

### 📈 Features

- **Parquet Support**: Fast loading of batch processing results (13,860+ rows)
- **Interactive Charts**: Zoom, pan, and hover for details (Plotly)
- **Advanced Filtering**: Filter by lot size, template, Sharpe, win rate, and more
- **Data Export**: Download CSV, JSON, or Parquet formats
- **Real-time Updates**: Charts update instantly with filter changes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Template Analysis**: Identify best-performing strategy templates
- **Lot Size Optimization**: Find optimal position sizing

### 💡 Tips

- Use **Overview** to identify top performers quickly
- Explore **Performance Matrix** to find optimal template/lot size combinations
- **Strategy Explorer** lets you compare multiple strategies side-by-side
- Assess risk with **Risk Analysis** and classify strategies by risk tier
- Analyze profitability with **Profitability** page (PnL, commission impact)
- Use **Lot Size Analysis** to optimize position sizing
- Find best templates with **Strategy Templates** page
- Export top strategies for deployment with **Export** page

### 🎯 Data Format Support

- ✅ **Parquet** (batch processing): Optimized for 13,860+ strategies
- ✅ **JSON** (legacy): Backward compatible with existing results
- ✅ **Smart Storage**: Automatic format detection

---

**Need help?** Check out [README_DASHBOARD.md](../README_DASHBOARD.md) for detailed documentation.
""")

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **NECROZMA Dashboard**
    
    Version: 2.0.0 (Batch Processing Edition)
    
    Built with:
    - Streamlit
    - Plotly
    - Pandas
    - PyArrow (Parquet support)
    
    © 2024-2026 NECROZMA Project
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("""
    - [Documentation](../README_DASHBOARD.md)
    - [GitHub](https://github.com/dans91364-create/NECROZMA)
    """)
