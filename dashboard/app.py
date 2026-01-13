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

This interactive dashboard provides comprehensive analysis of backtesting results across multiple strategies and universes.

### 📊 Available Pages

Navigate using the sidebar to explore:

- **📊 Overview**: Global performance summary and top strategies
- **🌍 Universe Analysis**: Compare performance across 25 universes
- **🎯 Strategy Deep Dive**: Detailed analysis of individual strategies
- **🔧 SL/TP Optimization**: Optimize stop-loss and take-profit parameters
- **⚠️ Risk Analysis**: Analyze risk-adjusted returns and drawdowns
- **💰 Trade Analysis**: Examine best and worst trades with market context
- **🏆 Composite Ranking**: Multi-factor composite score analysis (NEW!)
- **💰 Max Profit Ranking**: Five profit-focused perspectives (NEW!)

### 🚀 Getting Started

1. Ensure you have run backtests to generate results in `ultra_necrozma_results/backtest_results/`
2. Select a page from the sidebar
3. Use filters to drill down into specific strategies or conditions
4. Export data and charts as needed

### 📈 Features

- **Interactive Charts**: Zoom, pan, and hover for details
- **Dynamic Filtering**: Filter by metrics, universes, patterns, and more
- **Data Export**: Download filtered data as CSV
- **Real-time Updates**: Charts update instantly with filter changes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Multi-Factor Analysis**: Composite scores across 4 key dimensions
- **Profit Perspectives**: 5 different ways to analyze profitability

### 💡 Tips

- Use the **Overview** page to identify top performers
- Explore **Universe Analysis** to find optimal timeframes
- Deep dive into specific strategies with **Strategy Deep Dive**
- Optimize parameters with **SL/TP Optimization**
- Assess risk with **Risk Analysis**
- Learn from winning/losing trades in **Trade Analysis**
- Find balanced strategies with **Composite Ranking**
- Discover profit leaders with **Max Profit Ranking**

---

**Need help?** Check out [README_DASHBOARD.md](../README_DASHBOARD.md) for detailed documentation.
""")

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **NECROZMA Dashboard**
    
    Version: 1.0.0
    
    Built with:
    - Streamlit
    - Plotly
    - Pandas
    
    © 2024 NECROZMA Project
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("""
    - [Documentation](../README_DASHBOARD.md)
    - [GitHub](https://github.com/dans91364-create/NECROZMA)
    """)
