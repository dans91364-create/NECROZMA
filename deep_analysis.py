#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DEEP ANALYSIS 💎🌟⚡

Performs deep analysis of the 295 operational strategies (50-50,000 trades).
Generates comprehensive reports with metrics, parameter analysis, and recommendations.

Frequency Bands:
- FAIXA 1: 50-500 trades (Swing Trading)
- FAIXA 2: 500-5000 trades (Day Trading)
- FAIXA 3: 5000-50000 trades (Scalping)
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict, Counter
import warnings

warnings.filterwarnings("ignore")


def load_screening_data(screening_dir):
    """Load all CSV files from screening_results directory."""
    screening_path = Path(screening_dir)
    
    if not screening_path.exists():
        raise FileNotFoundError(f"Directory {screening_dir} does not exist")
    
    csv_files = list(screening_path.glob("*.csv"))
    # Exclude output files from this script and previous analyses
    exclude_patterns = [
        "screening_summary", "frequency_analysis", "deep_analysis", 
        "parameter_analysis", "extremes_diagnosis"
    ]
    csv_files = [f for f in csv_files if not any(p in f.name for p in exclude_patterns)]
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {screening_dir}")
    
    print(f"📂 Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"   - {f.name}")
    
    dfs = []
    for csv_file in csv_files:
        print(f"📖 Loading {csv_file.name}...")
        df = pd.read_csv(csv_file)
        dfs.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Loaded {len(combined_df):,} total results")
    
    return combined_df


def clean_data(df):
    """Filter out NaN and Inf values from key metrics."""
    print("\n🧹 Cleaning data...")
    
    initial_count = len(df)
    
    # Replace infinite values with NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Drop rows with NaN in critical metrics
    critical_metrics = ['sharpe_ratio', 'n_trades', 'profit_factor', 'win_rate']
    df = df.dropna(subset=critical_metrics)
    
    removed = initial_count - len(df)
    print(f"   Removed {removed:,} rows with NaN/Inf values ({removed/initial_count*100:.1f}%)")
    print(f"   Remaining: {len(df):,} rows")
    
    return df


def extract_base_strategy_name(strategy_name):
    """Extract base strategy name without lot_size parameter."""
    base_name = re.sub(r'_L\d+', '', strategy_name)
    return base_name


def parse_strategy_params(strategy_name):
    """
    Extract parameters from strategy name.
    Example: MeanReverter_T1.8_SL30_TP50 -> {'T': 1.8, 'SL': 30, 'TP': 50}
    """
    params = {}
    
    # Match patterns like T1.8, SL30, TP50, RSI20-65, CD300
    pattern = r'([A-Z]+)([\d.]+(?:-[\d.]+)?)'
    matches = re.findall(pattern, strategy_name)
    
    for key, value in matches:
        try:
            if '-' in value:  # Handle RSI ranges
                params[key] = value
            elif '.' in value:
                params[key] = float(value)
            else:
                params[key] = int(value)
        except ValueError:
            params[key] = value
    
    return params


def filter_operational_strategies(df):
    """Filter strategies with 50-50,000 trades (operational range)."""
    print("\n🔍 Filtering operational strategies (50-50,000 trades)...")
    
    operational = df[(df['n_trades'] >= 50) & (df['n_trades'] <= 50000)].copy()
    
    # Group by base strategy (ignore lot_size)
    operational['base_strategy'] = operational['strategy_name'].apply(extract_base_strategy_name)
    
    # Keep best performer per base strategy (by Sharpe Ratio)
    operational = operational.sort_values('sharpe_ratio', ascending=False).groupby('base_strategy', as_index=False).first()
    
    print(f"   Total operational strategies: {len(operational):,}")
    
    # Count by frequency band
    faixa1 = operational[(operational['n_trades'] >= 50) & (operational['n_trades'] < 500)]
    faixa2 = operational[(operational['n_trades'] >= 500) & (operational['n_trades'] < 5000)]
    faixa3 = operational[(operational['n_trades'] >= 5000) & (operational['n_trades'] <= 50000)]
    
    print(f"   FAIXA 1 (50-500):     {len(faixa1):,} strategies")
    print(f"   FAIXA 2 (500-5000):   {len(faixa2):,} strategies")
    print(f"   FAIXA 3 (5000-50000): {len(faixa3):,} strategies")
    
    return operational


def assign_frequency_band(n_trades):
    """Assign frequency band based on number of trades."""
    if 50 <= n_trades < 500:
        return "FAIXA 1 (50-500)"
    elif 500 <= n_trades < 5000:
        return "FAIXA 2 (500-5K)"
    elif 5000 <= n_trades <= 50000:
        return "FAIXA 3 (5K-50K)"
    else:
        return "OUT OF RANGE"


def analyze_by_template(df):
    """Analyze strategies by template type."""
    print("\n📊 Analyzing by template...")
    
    template_stats = []
    
    for template in sorted(df['template'].unique()):
        template_df = df[df['template'] == template]
        
        # Count by frequency band
        faixa1 = len(template_df[(template_df['n_trades'] >= 50) & (template_df['n_trades'] < 500)])
        faixa2 = len(template_df[(template_df['n_trades'] >= 500) & (template_df['n_trades'] < 5000)])
        faixa3 = len(template_df[(template_df['n_trades'] >= 5000) & (template_df['n_trades'] <= 50000)])
        
        stats = {
            'template': template,
            'total': len(template_df),
            'faixa1': faixa1,
            'faixa2': faixa2,
            'faixa3': faixa3,
            'sharpe_mean': template_df['sharpe_ratio'].mean(),
            'sharpe_median': template_df['sharpe_ratio'].median(),
            'sharpe_max': template_df['sharpe_ratio'].max(),
            'sharpe_min': template_df['sharpe_ratio'].min(),
            'pf_mean': template_df['profit_factor'].mean(),
            'pf_median': template_df['profit_factor'].median(),
            'wr_mean': template_df['win_rate'].mean() * 100,
            'wr_median': template_df['win_rate'].median() * 100,
            'n_trades_mean': template_df['n_trades'].mean(),
            'n_trades_median': template_df['n_trades'].median(),
        }
        
        # Find best configuration
        best = template_df.loc[template_df['sharpe_ratio'].idxmax()]
        stats['best_config'] = best['strategy_name']
        stats['best_sharpe'] = best['sharpe_ratio']
        
        template_stats.append(stats)
    
    return pd.DataFrame(template_stats)


def analyze_parameters(df):
    """Analyze parameter performance across strategies."""
    print("\n🔧 Analyzing parameter performance...")
    
    param_analysis = []
    
    # Extract parameters for all strategies
    df['params'] = df['strategy_name'].apply(parse_strategy_params)
    
    # Get all unique parameter keys
    all_params = set()
    for params in df['params']:
        all_params.update(params.keys())
    
    # Analyze each parameter
    for param_name in sorted(all_params):
        # Get strategies that have this parameter
        strategies_with_param = df[df['params'].apply(lambda p: param_name in p)]
        
        if len(strategies_with_param) == 0:
            continue
        
        # Get unique values for this parameter
        param_values = strategies_with_param['params'].apply(lambda p: p.get(param_name))
        unique_values = param_values.unique()
        
        for template in strategies_with_param['template'].unique():
            template_df = strategies_with_param[strategies_with_param['template'] == template]
            
            for value in unique_values:
                value_df = template_df[template_df['params'].apply(lambda p: p.get(param_name) == value)]
                
                if len(value_df) == 0:
                    continue
                
                analysis = {
                    'template': template,
                    'parameter': param_name,
                    'value': value,
                    'count': len(value_df),
                    'sharpe_mean': value_df['sharpe_ratio'].mean(),
                    'sharpe_median': value_df['sharpe_ratio'].median(),
                    'pf_mean': value_df['profit_factor'].mean(),
                    'wr_mean': value_df['win_rate'].mean() * 100,
                }
                
                param_analysis.append(analysis)
    
    return pd.DataFrame(param_analysis)


def create_parameter_heatmaps(df):
    """Create text-based heatmaps for parameter combinations."""
    print("\n🗺️  Creating parameter heatmaps...")
    
    df['params'] = df['strategy_name'].apply(parse_strategy_params)
    
    heatmaps = []
    
    # T vs SL -> Sharpe
    heatmap_text = "\n" + "="*80 + "\n"
    heatmap_text += "HEATMAP: T (Threshold) vs SL (Stop Loss) → Average Sharpe Ratio\n"
    heatmap_text += "="*80 + "\n\n"
    
    t_values = sorted(set([p.get('T') for p in df['params'] if 'T' in p and p.get('T') is not None]))
    sl_values = sorted(set([p.get('SL') for p in df['params'] if 'SL' in p and p.get('SL') is not None]))
    
    if t_values and sl_values:
        # Create matrix
        matrix = {}
        for t in t_values:
            for sl in sl_values:
                subset = df[df['params'].apply(lambda p: p.get('T') == t and p.get('SL') == sl)]
                if len(subset) > 0:
                    matrix[(t, sl)] = subset['sharpe_ratio'].mean()
        
        # Print header
        heatmap_text += "      "
        for sl in sl_values:
            heatmap_text += f" SL{sl:>3} "
        heatmap_text += "\n"
        
        # Print rows
        for t in t_values:
            heatmap_text += f"T{t:<5} "
            for sl in sl_values:
                value = matrix.get((t, sl), np.nan)
                if np.isnan(value):
                    heatmap_text += "   -   "
                else:
                    heatmap_text += f"{value:6.2f} "
            heatmap_text += "\n"
    
    heatmaps.append(heatmap_text)
    
    # T vs TP -> Sharpe
    heatmap_text = "\n" + "="*80 + "\n"
    heatmap_text += "HEATMAP: T (Threshold) vs TP (Take Profit) → Average Sharpe Ratio\n"
    heatmap_text += "="*80 + "\n\n"
    
    tp_values = sorted(set([p.get('TP') for p in df['params'] if 'TP' in p and p.get('TP') is not None]))
    
    if t_values and tp_values:
        matrix = {}
        for t in t_values:
            for tp in tp_values:
                subset = df[df['params'].apply(lambda p: p.get('T') == t and p.get('TP') == tp)]
                if len(subset) > 0:
                    matrix[(t, tp)] = subset['sharpe_ratio'].mean()
        
        heatmap_text += "      "
        for tp in tp_values:
            heatmap_text += f" TP{tp:>3} "
        heatmap_text += "\n"
        
        for t in t_values:
            heatmap_text += f"T{t:<5} "
            for tp in tp_values:
                value = matrix.get((t, tp), np.nan)
                if np.isnan(value):
                    heatmap_text += "   -   "
                else:
                    heatmap_text += f"{value:6.2f} "
            heatmap_text += "\n"
    
    heatmaps.append(heatmap_text)
    
    # SL vs TP -> Win Rate
    heatmap_text = "\n" + "="*80 + "\n"
    heatmap_text += "HEATMAP: SL (Stop Loss) vs TP (Take Profit) → Average Win Rate (%)\n"
    heatmap_text += "="*80 + "\n\n"
    
    if sl_values and tp_values:
        matrix = {}
        for sl in sl_values:
            for tp in tp_values:
                subset = df[df['params'].apply(lambda p: p.get('SL') == sl and p.get('TP') == tp)]
                if len(subset) > 0:
                    matrix[(sl, tp)] = subset['win_rate'].mean() * 100
        
        heatmap_text += "      "
        for tp in tp_values:
            heatmap_text += f" TP{tp:>3} "
        heatmap_text += "\n"
        
        for sl in sl_values:
            heatmap_text += f"SL{sl:<3} "
            for tp in tp_values:
                value = matrix.get((sl, tp), np.nan)
                if np.isnan(value):
                    heatmap_text += "   -   "
                else:
                    heatmap_text += f"{value:6.1f} "
            heatmap_text += "\n"
    
    heatmaps.append(heatmap_text)
    
    return "".join(heatmaps)


def apply_quality_filters(df):
    """Apply quality tier filters to strategies."""
    print("\n⭐ Applying quality filters...")
    
    tier1 = df[(df['sharpe_ratio'] > 1.0) & (df['profit_factor'] > 1.2) & (df['win_rate'] > 0.3)]
    tier2 = df[(df['sharpe_ratio'] > 0.5) & (df['profit_factor'] > 1.1) & (df['win_rate'] > 0.25)]
    tier3 = df[(df['sharpe_ratio'] > 0) & (df['profit_factor'] > 1.0)]
    
    print(f"   TIER 1 (Sharpe>1.0, PF>1.2, WR>30%):  {len(tier1):,} strategies")
    print(f"   TIER 2 (Sharpe>0.5, PF>1.1, WR>25%):  {len(tier2):,} strategies")
    print(f"   TIER 3 (Sharpe>0, PF>1.0):            {len(tier3):,} strategies")
    
    return {'tier1': tier1, 'tier2': tier2, 'tier3': tier3}


def calculate_weighted_score(df):
    """Calculate weighted ranking score for strategies."""
    print("\n📊 Calculating weighted scores...")
    
    # Normalize metrics to 0-1 scale
    df = df.copy()
    
    # Sharpe normalization
    sharpe_min, sharpe_max = df['sharpe_ratio'].min(), df['sharpe_ratio'].max()
    df['sharpe_norm'] = (df['sharpe_ratio'] - sharpe_min) / (sharpe_max - sharpe_min) if sharpe_max > sharpe_min else 0
    
    # Profit Factor normalization
    pf_min, pf_max = df['profit_factor'].min(), df['profit_factor'].max()
    df['pf_norm'] = (df['profit_factor'] - pf_min) / (pf_max - pf_min) if pf_max > pf_min else 0
    
    # Win Rate normalization
    wr_min, wr_max = df['win_rate'].min(), df['win_rate'].max()
    df['wr_norm'] = (df['win_rate'] - wr_min) / (wr_max - wr_min) if wr_max > wr_min else 0
    
    # Weighted score
    df['weighted_score'] = (df['sharpe_norm'] * 0.4) + (df['pf_norm'] * 0.3) + (df['wr_norm'] * 0.3)
    
    return df


def generate_recommendations(df):
    """Generate top 10 recommendations for GBPUSD."""
    print("\n💎 Generating final recommendations...")
    
    # Calculate weighted scores
    df = calculate_weighted_score(df)
    
    # Sort by weighted score
    top_candidates = df.sort_values('weighted_score', ascending=False).head(50)
    
    # Ensure diversity in templates and frequency bands
    recommendations = []
    selected_templates = set()
    
    for _, row in top_candidates.iterrows():
        # Try to get diverse templates
        if len(recommendations) < 10:
            recommendations.append(row)
            selected_templates.add(row['template'])
        elif row['template'] not in selected_templates and len(recommendations) < 20:
            recommendations.append(row)
            selected_templates.add(row['template'])
    
    return pd.DataFrame(recommendations[:10])


def generate_report(df, template_stats, param_analysis, heatmaps, tiers, recommendations, output_dir):
    """Generate comprehensive text report."""
    print("\n📝 Generating report...")
    
    report = []
    
    # Header
    report.append("="*100)
    report.append("⚡🌟💎 ULTRA NECROZMA - DEEP ANALYSIS REPORT 💎🌟⚡")
    report.append("="*100)
    report.append("")
    report.append(f"Total Operational Strategies Analyzed: {len(df):,}")
    report.append("")
    
    # 1. COMPLETE LISTING
    report.append("="*100)
    report.append(f"1. COMPLETE LISTING - ALL {len(df)} OPERATIONAL STRATEGIES")
    report.append("="*100)
    report.append("")
    
    # Add frequency band
    df['frequency_band'] = df['n_trades'].apply(assign_frequency_band)
    
    # Sort by frequency band and sharpe ratio
    df_sorted = df.sort_values(['frequency_band', 'sharpe_ratio'], ascending=[True, False])
    
    for band in ["FAIXA 1 (50-500)", "FAIXA 2 (500-5K)", "FAIXA 3 (5K-50K)"]:
        band_df = df_sorted[df_sorted['frequency_band'] == band]
        
        if len(band_df) > 0:
            report.append("")
            report.append(f"{'='*100}")
            report.append(f"{band} - {len(band_df)} strategies")
            report.append(f"{'='*100}")
            report.append("")
            report.append(f"{'#':<4} {'Strategy Name':<60} {'Sharpe':>8} {'PF':>6} {'WR':>7} {'Trades':>8}")
            report.append("-"*100)
            
            for idx, (_, row) in enumerate(band_df.iterrows(), 1):
                report.append(
                    f"{idx:<4} {row['strategy_name']:<60} "
                    f"{row['sharpe_ratio']:>8.3f} "
                    f"{row['profit_factor']:>6.3f} "
                    f"{row['win_rate']*100:>6.1f}% "
                    f"{int(row['n_trades']):>8,}"
                )
    
    # 2. TEMPLATE ANALYSIS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("2. ANALYSIS BY TEMPLATE")
    report.append("="*100)
    report.append("")
    
    for _, row in template_stats.iterrows():
        report.append(f"\n{'='*100}")
        report.append(f"TEMPLATE: {row['template']}")
        report.append(f"{'='*100}")
        report.append(f"Total Strategies: {row['total']}")
        report.append(f"Distribution: FAIXA1={row['faixa1']}, FAIXA2={row['faixa2']}, FAIXA3={row['faixa3']}")
        report.append("")
        report.append(f"Sharpe Ratio:   Mean={row['sharpe_mean']:>7.3f}  Median={row['sharpe_median']:>7.3f}  "
                     f"Max={row['sharpe_max']:>7.3f}  Min={row['sharpe_min']:>7.3f}")
        report.append(f"Profit Factor:  Mean={row['pf_mean']:>7.3f}  Median={row['pf_median']:>7.3f}")
        report.append(f"Win Rate:       Mean={row['wr_mean']:>6.1f}%  Median={row['wr_median']:>6.1f}%")
        report.append(f"N Trades:       Mean={row['n_trades_mean']:>8,.0f}  Median={row['n_trades_median']:>8,.0f}")
        report.append("")
        report.append(f"Best Configuration: {row['best_config']}")
        report.append(f"Best Sharpe: {row['best_sharpe']:.3f}")
    
    # 3. PARAMETER ANALYSIS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("3. PARAMETER ANALYSIS")
    report.append("="*100)
    report.append("")
    
    # Group by template and parameter
    for template in sorted(param_analysis['template'].unique()):
        template_params = param_analysis[param_analysis['template'] == template]
        
        report.append(f"\n{'='*100}")
        report.append(f"TEMPLATE: {template}")
        report.append(f"{'='*100}")
        
        for param in sorted(template_params['parameter'].unique()):
            param_data = template_params[template_params['parameter'] == param].sort_values('sharpe_mean', ascending=False)
            
            if len(param_data) > 0:
                report.append(f"\nParameter: {param}")
                report.append(f"{'Value':<10} {'Count':>6} {'Sharpe':>8} {'PF':>6} {'WR':>7}")
                report.append("-"*45)
                
                for _, row in param_data.iterrows():
                    report.append(
                        f"{str(row['value']):<10} {row['count']:>6} "
                        f"{row['sharpe_mean']:>8.3f} "
                        f"{row['pf_mean']:>6.3f} "
                        f"{row['wr_mean']:>6.1f}%"
                    )
    
    # 4. HEATMAPS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("4. PARAMETER HEATMAPS")
    report.append("="*100)
    report.append(heatmaps)
    
    # 5. QUALITY FILTERS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("5. QUALITY TIER FILTERS")
    report.append("="*100)
    report.append("")
    
    for tier_name, tier_df in [("TIER 1", tiers['tier1']), ("TIER 2", tiers['tier2']), ("TIER 3", tiers['tier3'])]:
        report.append(f"\n{'-'*100}")
        report.append(f"{tier_name}")
        report.append(f"{'-'*100}")
        report.append(f"Total: {len(tier_df)} strategies")
        report.append("")
        
        if len(tier_df) > 0:
            tier_sorted = tier_df.sort_values('sharpe_ratio', ascending=False).head(20)
            report.append(f"{'#':<4} {'Strategy Name':<60} {'Sharpe':>8} {'PF':>6} {'WR':>7} {'Trades':>8}")
            report.append("-"*100)
            
            for idx, (_, row) in enumerate(tier_sorted.iterrows(), 1):
                report.append(
                    f"{idx:<4} {row['strategy_name']:<60} "
                    f"{row['sharpe_ratio']:>8.3f} "
                    f"{row['profit_factor']:>6.3f} "
                    f"{row['win_rate']*100:>6.1f}% "
                    f"{int(row['n_trades']):>8,}"
                )
    
    # 6. WEIGHTED RANKING
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("6. WEIGHTED RANKING - TOP 50")
    report.append("="*100)
    report.append("")
    report.append("Score = (Sharpe_norm × 0.4) + (PF_norm × 0.3) + (WR_norm × 0.3)")
    report.append("")
    
    df_scored = calculate_weighted_score(df)
    top50 = df_scored.sort_values('weighted_score', ascending=False).head(50)
    
    report.append(f"{'#':<4} {'Strategy Name':<55} {'Score':>7} {'Sharpe':>8} {'PF':>6} {'WR':>7} {'Band':<15}")
    report.append("-"*110)
    
    for idx, (_, row) in enumerate(top50.iterrows(), 1):
        report.append(
            f"{idx:<4} {row['strategy_name']:<55} "
            f"{row['weighted_score']:>7.4f} "
            f"{row['sharpe_ratio']:>8.3f} "
            f"{row['profit_factor']:>6.3f} "
            f"{row['win_rate']*100:>6.1f}% "
            f"{row['frequency_band']:<15}"
        )
    
    # 7. FINAL RECOMMENDATIONS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("7. FINAL RECOMMENDATIONS - TOP 10 FOR GBPUSD")
    report.append("="*100)
    report.append("")
    report.append("Selected for diversity across templates and frequency bands")
    report.append("")
    
    report.append(f"{'#':<4} {'Strategy Name':<55} {'Score':>7} {'Sharpe':>8} {'PF':>6} {'WR':>7} {'Trades':>8} {'Template':<20}")
    report.append("-"*120)
    
    for idx, (_, row) in enumerate(recommendations.iterrows(), 1):
        report.append(
            f"{idx:<4} {row['strategy_name']:<55} "
            f"{row['weighted_score']:>7.4f} "
            f"{row['sharpe_ratio']:>8.3f} "
            f"{row['profit_factor']:>6.3f} "
            f"{row['win_rate']*100:>6.1f}% "
            f"{int(row['n_trades']):>8,} "
            f"{row['template']:<20}"
        )
    
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("END OF REPORT")
    report.append("="*100)
    
    # Write report
    report_path = Path(output_dir) / "deep_analysis.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Report saved to {report_path}")


def main():
    """Main execution function."""
    print("⚡🌟💎 ULTRA NECROZMA - DEEP ANALYSIS 💎🌟⚡")
    print("="*100)
    print()
    
    # Configuration
    screening_dir = "screening_results"
    output_dir = "screening_results"
    
    # Load data
    df = load_screening_data(screening_dir)
    
    # Clean data
    df = clean_data(df)
    
    # Filter operational strategies (50-50,000 trades)
    operational = filter_operational_strategies(df)
    
    # Template analysis
    template_stats = analyze_by_template(operational)
    
    # Parameter analysis
    param_analysis = analyze_parameters(operational)
    
    # Heatmaps
    heatmaps = create_parameter_heatmaps(operational)
    
    # Quality filters
    tiers = apply_quality_filters(operational)
    
    # Recommendations
    recommendations = generate_recommendations(operational)
    
    # Generate outputs
    print("\n💾 Saving outputs...")
    
    # Save deep_analysis.csv
    csv_path = Path(output_dir) / "deep_analysis.csv"
    operational.to_csv(csv_path, index=False)
    print(f"✅ Saved {csv_path}")
    
    # Save parameter_analysis.csv
    param_csv_path = Path(output_dir) / "parameter_analysis.csv"
    param_analysis.to_csv(param_csv_path, index=False)
    print(f"✅ Saved {param_csv_path}")
    
    # Generate and save report
    generate_report(operational, template_stats, param_analysis, heatmaps, tiers, recommendations, output_dir)
    
    print("\n" + "="*100)
    print("✅ DEEP ANALYSIS COMPLETE!")
    print("="*100)
    print(f"\nGenerated files:")
    print(f"  - {csv_path}")
    print(f"  - {param_csv_path}")
    print(f"  - {Path(output_dir) / 'deep_analysis.txt'}")


if __name__ == "__main__":
    main()
