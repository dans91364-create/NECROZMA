#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - REGIME ANALYSIS PAGE 💎🌟⚡

Market regime analysis from Light That Burns The Sky
DFA, Hurst, Lyapunov, and other chaos metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Regime Analysis", page_icon="🔮", layout="wide")

st.title("🔮 Market Regime Analysis")
st.markdown("DFA, Hurst, Lyapunov analysis from Light That Burns The Sky")

st.info("""
📌 **Market Regime Metrics Explained**

These advanced metrics reveal the underlying structure and dynamics of the market:

- **🌊 DFA Alpha**: Detrended Fluctuation Analysis - measures long-term correlations
  - > 0.6: Strongly persistent (trending)
  - 0.5-0.6: Persistent (weak trends)
  - < 0.5: Anti-persistent (mean reverting)

- **🌀 Hurst Exponent**: Measures long-term memory in time series
  - > 0.55: Long memory, persistent trends
  - 0.45-0.55: Random walk behavior
  - < 0.45: Anti-persistent, mean reverting

- **⚡ Lyapunov Exponent**: Quantifies chaos and sensitivity to initial conditions
  - > 0.05: High chaos, very sensitive
  - 0.02-0.05: Moderate chaos
  - < 0.02: Low chaos, stable

- **📐 Fractal Dimension**: Complexity of price patterns
  - > 1.6: Very complex, intricate patterns
  - 1.4-1.6: High complexity
  - < 1.4: Moderate complexity

- **🔮 Shannon Entropy**: Randomness and unpredictability
  - > 3.0: High randomness
  - 2.0-3.0: Moderate randomness
  - < 2.0: Low randomness (more predictable)
""")

# Load the final judgment JSON if it exists
judgment_path = Path(__file__).parent.parent.parent / "ultra_necrozma_results" / "final_judgment.json"

if judgment_path.exists():
    try:
        with open(judgment_path) as f:
            judgment = json.load(f)
        
        regime_data = judgment.get("market_regime", {})
        
        # Display regime metrics
        st.header("📊 Market Regime Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            regime = regime_data.get("regime", "Unknown")
            st.metric("🎯 Market Regime", regime)
            
            dfa_alpha = regime_data.get("dfa_alpha", 0)
            st.metric("🌊 DFA Alpha", f"{dfa_alpha:.3f}")
        
        with col2:
            hurst = regime_data.get("hurst_exponent", 0)
            st.metric("🌀 Hurst Exponent", f"{hurst:.3f}")
            
            lyapunov = regime_data.get("lyapunov_exponent", 0)
            st.metric("⚡ Lyapunov", f"{lyapunov:.4f}")
        
        with col3:
            fractal = regime_data.get("fractal_dimension", 0)
            st.metric("📐 Fractal Dimension", f"{fractal:.3f}")
            
            entropy = regime_data.get("shannon_entropy", 0)
            st.metric("🔮 Shannon Entropy", f"{entropy:.3f}")
        
        st.markdown("---")
        
        # Chaos and Complexity indicators
        st.header("⚡ Market Characteristics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chaos = regime_data.get("chaos_level", "Unknown")
            if chaos == "HIGH":
                color = "🔴"
                level_desc = "High sensitivity to initial conditions"
            elif chaos == "MODERATE":
                color = "🟡"
                level_desc = "Moderate sensitivity"
            else:
                color = "🟢"
                level_desc = "Stable, low sensitivity"
            
            st.info(f"{color} **Chaos Level:** {chaos}\n\n{level_desc}")
        
        with col2:
            complexity = regime_data.get("complexity", "Unknown")
            if complexity == "VERY_HIGH":
                color = "🔴"
                comp_desc = "Very intricate patterns"
            elif complexity == "HIGH":
                color = "🟡"
                comp_desc = "Complex patterns"
            else:
                color = "🟢"
                comp_desc = "Simpler patterns"
            
            st.info(f"{color} **Complexity:** {complexity}\n\n{comp_desc}")
        
        st.markdown("---")
        
        # Recommendations
        if "recommendations" in judgment:
            st.header("📋 Trading Recommendations")
            
            recs = judgment["recommendations"]
            
            st.success(f"**Primary Strategy:** {recs.get('primary_strategy', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Confidence:** {recs.get('confidence', 'N/A')}")
            with col2:
                st.warning(f"**Risk Level:** {recs.get('risk_level', 'N/A')}")
            
            st.subheader("🎯 Key Points")
            key_points = recs.get("key_points", [])
            if key_points:
                for point in key_points:
                    st.markdown(f"• {point}")
            else:
                st.info("No specific key points available")
        
        st.markdown("---")
        
        # Visualization - Radar chart of regime metrics
        st.header("📊 Regime Metrics Visualization")
        
        categories = ['DFA Alpha', 'Hurst', 'Fractal Dim', 'Entropy (scaled)']
        values = [
            regime_data.get('dfa_alpha', 0.5),
            regime_data.get('hurst_exponent', 0.5),
            regime_data.get('fractal_dimension', 1.5) / 2,  # Scale to 0-1
            regime_data.get('shannon_entropy', 2.0) / 4,   # Scale to 0-1
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name='Regime Metrics',
            line=dict(color='rgb(99, 110, 250)', width=2),
            fillcolor='rgba(99, 110, 250, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    showticklabels=True,
                    ticks='outside'
                )
            ),
            showlegend=False,
            title="Market Regime Profile",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Interpretation Guide
        st.header("📖 Interpretation Guide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 DFA Alpha Interpretation")
            dfa = regime_data.get('dfa_alpha', 0.5)
            if dfa > 0.6:
                st.success("**STRONGLY PERSISTENT** - Market shows powerful trending behavior")
                st.markdown("✅ Favor trend-following strategies")
            elif dfa > 0.52:
                st.info("**PERSISTENT** - Market exhibits trending behavior")
                st.markdown("✅ Trend strategies may work well")
            elif dfa < 0.48:
                st.warning("**ANTI-PERSISTENT** - Market shows mean reversion")
                st.markdown("✅ Consider mean-reversion strategies")
            else:
                st.info("**RANDOM WALK** - Market is efficient/neutral")
                st.markdown("⚠️ Be cautious with directional strategies")
        
        with col2:
            st.subheader("🌀 Hurst Exponent Interpretation")
            hurst_val = regime_data.get('hurst_exponent', 0.5)
            if hurst_val > 0.55:
                st.success("**STRONG LONG MEMORY** - Persistent trends likely")
                st.markdown("✅ Long-term positions may be favorable")
            elif hurst_val < 0.45:
                st.warning("**ANTI-PERSISTENT** - Mean reversion expected")
                st.markdown("✅ Short-term reversions likely")
            else:
                st.info("**WEAK LONG MEMORY** - Short-term patterns only")
                st.markdown("⚠️ Focus on short-term timeframes")
        
        st.markdown("---")
        
        # Best Configuration
        if "best_configuration" in judgment and judgment["best_configuration"]:
            st.header("💎 Optimal Configuration")
            
            best_config = judgment["best_configuration"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Universe", best_config.get('name', 'N/A'))
            with col2:
                st.metric("Interval", f"{best_config.get('interval', 'N/A')} min")
            with col3:
                st.metric("Lookback", f"{best_config.get('lookback', 'N/A')} periods")
            with col4:
                st.metric("Score", f"{best_config.get('score', 0):.1f}")
            
            st.success(f"🏆 This configuration identified {best_config.get('total_patterns', 0)} patterns")
        
        st.markdown("---")
        
        # Summary Statistics
        if "summary" in judgment:
            st.header("📈 Analysis Summary")
            
            summary = judgment["summary"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Universes Analyzed", summary.get('universes_analyzed', 0))
            with col2:
                st.metric("Total Patterns", f"{summary.get('total_patterns', 0):,}")
            with col3:
                st.metric("Evolution Stage", summary.get('evolution_stage', 'N/A'))
            with col4:
                st.metric("Light Power", f"{summary.get('light_power', 0):.1f}%")
    
    except Exception as e:
        st.error(f"❌ Error loading regime analysis data: {str(e)}")
        st.info("The data file may be corrupted or in an unexpected format.")
else:
    st.warning("⚠️ No regime analysis data found.")
    st.info("""
    **To generate regime analysis data:**
    
    1. Run the full analysis without `--strategy-discovery` flag
    2. The system will run `light_that_burns_the_sky` which performs regime analysis
    3. Regime data will be saved to `ultra_necrozma_results/final_judgment.json`
    
    **Command:**
    ```bash
    python main.py
    ```
    
    **Note:** Strategy discovery mode uses a different pipeline and doesn't generate this regime data.
    """)

# Footer
st.markdown("---")
st.markdown("""
💡 **Tips:**
- Regime analysis reveals the fundamental market structure
- Use these metrics to select appropriate strategy types
- Combine regime analysis with strategy performance for best results
- Persistent markets favor trend following, anti-persistent favor mean reversion
""")
