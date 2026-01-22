#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate GBPUSD candidates from screening results.
Combines Round 2 + Round 3 results and filters best candidates.
"""

import pandas as pd
from pathlib import Path


def load_screening_results(screening_dir="screening_results"):
    """Load all round CSV files."""
    screening_path = Path(screening_dir)
    
    dfs = []
    for csv_file in screening_path.glob("round*.csv"):
        print(f"📖 Loading {csv_file.name}...")
        df = pd.read_csv(csv_file)
        df['source_file'] = csv_file.name
        dfs.append(df)
    
    if not dfs:
        raise FileNotFoundError("No round*.csv files found")
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"✅ Loaded {len(combined):,} total results")
    return combined


def filter_candidates(df, min_sharpe=0, min_pf=1.0, min_trades=50, max_trades=50000):
    """Filter candidates based on criteria."""
    
    # Remove bad templates (in case they still exist in old CSV files)
    bad_templates = ['BreakoutTrader', 'SessionBreakout', 'ScalpingStrategy', 'PatternRecognition',
                     'CorrelationTrader', 'PairDivergence', 'LeadLagStrategy', 
                     'RiskSentiment', 'USDStrength', 'RegimeAdapter']
    
    filtered = df[~df['template'].isin(bad_templates)].copy()
    print(f"   After removing bad templates: {len(filtered):,}")
    
    # Filter by metrics
    filtered = filtered[
        (filtered['sharpe_ratio'] > min_sharpe) &
        (filtered['profit_factor'] > min_pf) &
        (filtered['n_trades'] >= min_trades) &
        (filtered['n_trades'] <= max_trades)
    ]
    print(f"   After metric filters: {len(filtered):,}")
    
    return filtered


def categorize_by_frequency(df):
    """Categorize strategies by trading frequency."""
    
    df = df.copy()
    
    def get_frequency_band(trades):
        if trades < 500:
            return 'SWING'  # 0-2 trades/day
        elif trades < 5000:
            return 'DAY_TRADE'  # 2-20 trades/day
        else:
            return 'SCALPING'  # 20+ trades/day
    
    df['frequency_band'] = df['n_trades'].apply(get_frequency_band)
    
    return df


def select_portfolio_mix(df, swing_count=5, day_count=10, scalp_count=10):
    """Select balanced portfolio mix."""
    
    df = categorize_by_frequency(df)
    
    selected = []
    
    # Top Swing (low frequency, high Sharpe)
    swing = df[df['frequency_band'] == 'SWING'].nlargest(swing_count, 'sharpe_ratio')
    selected.append(swing)
    print(f"   SWING: {len(swing)} strategies (Sharpe: {swing['sharpe_ratio'].mean():.2f})")
    
    # Top Day Trade (medium frequency)
    day = df[df['frequency_band'] == 'DAY_TRADE'].nlargest(day_count, 'sharpe_ratio')
    selected.append(day)
    print(f"   DAY_TRADE: {len(day)} strategies (Sharpe: {day['sharpe_ratio'].mean():.2f})")
    
    # Top Scalping (high frequency)
    scalp = df[df['frequency_band'] == 'SCALPING'].nlargest(scalp_count, 'sharpe_ratio')
    selected.append(scalp)
    print(f"   SCALPING: {len(scalp)} strategies (Sharpe: {scalp['sharpe_ratio'].mean():.2f})")
    
    return pd.concat(selected, ignore_index=True)


def main():
    print("⚡🌟💎 ULTRA NECROZMA - GBPUSD CANDIDATES GENERATOR 💎🌟⚡")
    print("=" * 60)
    
    # Load data
    df = load_screening_results()
    
    # Filter candidates
    print("\n📊 Filtering candidates...")
    candidates = filter_candidates(df, min_sharpe=0, min_pf=1.0, min_trades=50)
    
    # Select portfolio mix
    print("\n🎯 Selecting portfolio mix...")
    portfolio = select_portfolio_mix(candidates, swing_count=5, day_count=15, scalp_count=30)
    
    # Save results
    output_path = Path("screening_results/gbpusd_candidates.csv")
    portfolio.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved {len(portfolio)} candidates to {output_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PORTFOLIO MIX SUMMARY")
    print("=" * 60)
    print(f"Total candidates: {len(portfolio)}")
    print(f"Average Sharpe: {portfolio['sharpe_ratio'].mean():.2f}")
    print(f"Average PF: {portfolio['profit_factor'].mean():.2f}")
    print(f"Trade range: {portfolio['n_trades'].min()} - {portfolio['n_trades'].max()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
