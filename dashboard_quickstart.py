#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Dashboard Quick Start Guide 💎🌟⚡

Quick start script to help users get started with the dashboard
"""

import subprocess
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*70)
    print("⚡🌟💎 NECROZMA DASHBOARD - QUICK START 💎🌟⚡")
    print("="*70 + "\n")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['streamlit', 'plotly', 'pandas', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package} (not installed)")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nTo install, run:")
        print("   pip install -r requirements-dashboard.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_data():
    """Check if backtest results exist"""
    print("\n🔍 Checking for backtest results...")
    
    results_dir = Path("ultra_necrozma_results/backtest_results")
    
    if not results_dir.exists():
        print(f"   ❌ Results directory not found: {results_dir}")
        print("\n💡 To generate backtest results, run:")
        print("   python run_sequential_backtest.py")
        return False
    
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        print(f"   ❌ No JSON result files found in {results_dir}")
        print("\n💡 To generate backtest results, run:")
        print("   python run_sequential_backtest.py")
        return False
    
    print(f"   ✅ Found {len(json_files)} result files")
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n🚀 Launching dashboard...")
    print("\n" + "="*70)
    print("Dashboard will open in your browser at: http://localhost:8501")
    print("="*70)
    print("\nPress Ctrl+C to stop the dashboard\n")
    
    try:
        subprocess.run(['streamlit', 'run', 'dashboard/app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Thanks for using NECROZMA!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching dashboard: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ Streamlit not found. Install it with:")
        print("   pip install streamlit")
        return False
    
    return True

def show_usage():
    """Show usage instructions"""
    print("\n📖 USAGE INSTRUCTIONS")
    print("="*70)
    print("""
The dashboard has 6 main pages:

1. 📊 Overview
   - Global performance summary
   - Top 20 strategies
   - Viable vs non-viable breakdown

2. 🌍 Universe Analysis
   - Compare 25 universes
   - Performance heatmaps
   - Interval/lookback optimization

3. 🎯 Strategy Deep Dive
   - Detailed strategy metrics
   - Trade statistics
   - Risk metrics

4. 🔧 SL/TP Optimization
   - Stop-loss/take-profit analysis
   - Risk/reward optimization
   - Performance matrix

5. ⚠️ Risk Analysis
   - Return vs drawdown analysis
   - Efficient frontier
   - Risk metrics distribution

6. 💰 Trade Analysis
   - Best/worst trades
   - Pattern analysis
   - Market condition insights

Use the sidebar to navigate between pages.
Each page has interactive filters and downloadable data.
    """)
    print("="*70)

def main():
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first")
        sys.exit(1)
    
    # Check data
    has_data = check_data()
    
    if not has_data:
        print("\n⚠️  No backtest results found.")
        response = input("\nWould you like to see usage instructions anyway? (y/n): ")
        if response.lower() == 'y':
            show_usage()
        sys.exit(1)
    
    # Show usage
    print("\n✅ Everything is ready!")
    
    response = input("\nLaunch dashboard now? (y/n): ")
    
    if response.lower() == 'y':
        launch_dashboard()
    else:
        show_usage()
        print("\nTo launch the dashboard later, run:")
        print("   streamlit run dashboard/app.py")
        print("\nor run this script again:")
        print("   python dashboard_quickstart.py")

if __name__ == "__main__":
    main()
