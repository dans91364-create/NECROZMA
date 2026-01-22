#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FREQUENCY ANALYSIS 💎🌟⚡

Analyzes screening results separated by trade frequency bands.
Filters strategies with statistical significance and practical operability.

Frequency Bands:
- DISCARDED: < 50 trades (no statistical significance)
- FAIXA 1: 50-500 trades/ano (Low Frequency - Swing/Position Trading)
- FAIXA 2: 500-5000 trades/ano (Medium Frequency - Day Trading)
- FAIXA 3: 5000-50000 trades/ano (High Frequency - Scalping)
- IMPRACTICAL: > 50000 trades/ano (too many to operate)
"""

import pandas as pd
import json
import numpy as np
import re
from pathlib import Path
from collections import Counter
import warnings

warnings.filterwarnings("ignore")


def load_screening_data(screening_dir):
    """Load all CSV files from screening_results directory."""
    screening_path = Path(screening_dir)
    
    if not screening_path.exists():
        raise FileNotFoundError(f"Directory {screening_dir} does not exist")
    
    csv_files = list(screening_path.glob("*.csv"))
    csv_files = [f for f in csv_files if not f.name.startswith(("screening_summary", "frequency_analysis"))]
    
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
    """
    Extract base strategy name without lot_size parameter.
    Example: TrendFollower_L5_T0.5_SL10_TP20 -> TrendFollower_T0.5_SL10_TP20
    """
    # Remove lot_size pattern (e.g., _L5, _L10, etc.)
    base_name = re.sub(r'_L\d+', '', strategy_name)
    return base_name


def group_by_base_strategy(df):
    """
    Group strategies by base name (ignoring lot_size) and keep the best performer.
    Uses Sharpe Ratio as the primary metric.
    """
    print("\n🎯 Grouping by base strategy (ignoring lot_size)...")
    
    df['base_strategy'] = df['strategy_name'].apply(extract_base_strategy_name)
    
    # For each base strategy, keep the one with highest Sharpe Ratio
    # Use sort_values + groupby.first() for more robust handling
    grouped = df.sort_values('sharpe_ratio', ascending=False).groupby('base_strategy', as_index=False).first()
    
    print(f"   Original strategies: {len(df):,}")
    print(f"   Unique base strategies: {len(grouped):,}")
    
    return grouped


def categorize_by_frequency(df):
    """Categorize strategies into frequency bands based on n_trades."""
    print("\n📊 Categorizing by frequency bands...")
    
    def get_band(n_trades):
        if n_trades < 50:
            return 'DISCARDED'
        elif n_trades < 500:
            return 'FAIXA_1_LOW'
        elif n_trades < 5000:
            return 'FAIXA_2_MEDIUM'
        elif n_trades < 50000:
            return 'FAIXA_3_HIGH'
        else:
            return 'IMPRACTICAL'
    
    df['frequency_band'] = df['n_trades'].apply(get_band)
    
    # Count per band
    for band in ['DISCARDED', 'FAIXA_1_LOW', 'FAIXA_2_MEDIUM', 'FAIXA_3_HIGH', 'IMPRACTICAL']:
        count = len(df[df['frequency_band'] == band])
        pct = count / len(df) * 100
        print(f"   {band:<20}: {count:>6,} ({pct:>5.1f}%)")
    
    return df


def get_top_n(df, metric, n=10, ascending=False):
    """Get top N strategies by specified metric."""
    sorted_df = df.sort_values(by=metric, ascending=ascending)
    top = sorted_df.head(n)
    
    results = []
    for _, row in top.iterrows():
        results.append({
            'strategy_name': row['strategy_name'],
            'base_strategy': row['base_strategy'],
            'template': row.get('template', 'Unknown'),
            'lot_size': float(row['lot_size']),
            'sharpe_ratio': float(row['sharpe_ratio']),
            'sortino_ratio': float(row['sortino_ratio']),
            'profit_factor': float(row['profit_factor']),
            'win_rate': float(row['win_rate']),
            'n_trades': int(row['n_trades']),
            'total_return': float(row['total_return']),
            'max_drawdown': float(row['max_drawdown']),
            'net_pnl': float(row['net_pnl']),
        })
    
    return results


def calculate_aggregate_stats(df):
    """Calculate aggregate statistics for a dataframe."""
    if len(df) == 0:
        return None
    
    metrics = ['sharpe_ratio', 'sortino_ratio', 'profit_factor', 'win_rate', 'n_trades', 'total_return', 'max_drawdown']
    stats = {}
    
    for metric in metrics:
        stats[metric] = {
            'mean': float(df[metric].mean()),
            'median': float(df[metric].median()),
            'max': float(df[metric].max()),
            'min': float(df[metric].min()),
            'std': float(df[metric].std()),
        }
    
    return stats


def analyze_frequency_band(df, band_name):
    """Analyze a single frequency band."""
    print(f"\n📈 Analyzing {band_name}...")
    
    band_df = df[df['frequency_band'] == band_name]
    
    if len(band_df) == 0:
        return None
    
    analysis = {
        'count': len(band_df),
        'top_10_sharpe': get_top_n(band_df, 'sharpe_ratio', n=10),
        'top_10_profit_factor': get_top_n(band_df, 'profit_factor', n=10),
        'top_10_win_rate': get_top_n(band_df, 'win_rate', n=10),
        'aggregate_stats': calculate_aggregate_stats(band_df),
    }
    
    return analysis


def generate_comparison(band_analyses):
    """Generate comparison between frequency bands."""
    print("\n🔍 Generating band comparison...")
    
    comparison = {}
    
    for metric in ['sharpe_ratio', 'profit_factor', 'win_rate', 'total_return']:
        comparison[metric] = {}
        
        for band_name, analysis in band_analyses.items():
            if analysis and 'aggregate_stats' in analysis:
                comparison[metric][band_name] = analysis['aggregate_stats'][metric]['mean']
    
    # Find best band for each metric
    best_bands = {}
    for metric, band_values in comparison.items():
        if band_values:
            best_band = max(band_values.items(), key=lambda x: x[1])
            best_bands[metric] = best_band[0]
    
    return {
        'metric_comparison': comparison,
        'best_bands': best_bands,
    }


def get_final_candidates(band_analyses):
    """Get top 5 from each valid band for final candidate list."""
    print("\n🏆 Selecting final candidates...")
    
    candidates = {}
    valid_bands = ['FAIXA_1_LOW', 'FAIXA_2_MEDIUM', 'FAIXA_3_HIGH']
    
    for band in valid_bands:
        if band in band_analyses and band_analyses[band]:
            # Get top 5 by Sharpe Ratio
            top_10 = band_analyses[band]['top_10_sharpe']
            candidates[band] = top_10[:5] if len(top_10) >= 5 else top_10
    
    return candidates


def generate_analysis(screening_dir="screening_results"):
    """Main function to generate frequency analysis."""
    print("⚡🌟💎 ULTRA NECROZMA - FREQUENCY ANALYSIS 💎🌟⚡")
    print("=" * 80)
    
    # Load and clean data
    df = load_screening_data(screening_dir)
    df = clean_data(df)
    
    # Group by base strategy
    df = group_by_base_strategy(df)
    
    # Categorize by frequency
    df = categorize_by_frequency(df)
    
    # Analyze each band
    band_analyses = {}
    
    # Valid bands (1, 2, 3)
    for band in ['FAIXA_1_LOW', 'FAIXA_2_MEDIUM', 'FAIXA_3_HIGH']:
        band_analyses[band] = analyze_frequency_band(df, band)
    
    # Impractical band (statistics only, no rankings)
    impractical_df = df[df['frequency_band'] == 'IMPRACTICAL']
    if len(impractical_df) > 0:
        band_analyses['IMPRACTICAL'] = {
            'count': len(impractical_df),
            'aggregate_stats': calculate_aggregate_stats(impractical_df),
        }
    
    # Discarded band (count only)
    discarded_count = len(df[df['frequency_band'] == 'DISCARDED'])
    
    # Generate comparison
    comparison = generate_comparison({k: v for k, v in band_analyses.items() if k != 'IMPRACTICAL'})
    
    # Get final candidates
    final_candidates = get_final_candidates(band_analyses)
    
    # Build complete analysis
    analysis = {
        'general_summary': {
            'total_strategies': len(df),
            'discarded_count': discarded_count,
            'band_counts': {
                'FAIXA_1_LOW': band_analyses.get('FAIXA_1_LOW', {}).get('count', 0) if band_analyses.get('FAIXA_1_LOW') else 0,
                'FAIXA_2_MEDIUM': band_analyses.get('FAIXA_2_MEDIUM', {}).get('count', 0) if band_analyses.get('FAIXA_2_MEDIUM') else 0,
                'FAIXA_3_HIGH': band_analyses.get('FAIXA_3_HIGH', {}).get('count', 0) if band_analyses.get('FAIXA_3_HIGH') else 0,
                'IMPRACTICAL': band_analyses.get('IMPRACTICAL', {}).get('count', 0) if band_analyses.get('IMPRACTICAL') else 0,
            },
            'band_percentages': {},
        },
        'band_analyses': band_analyses,
        'comparison': comparison,
        'final_candidates': final_candidates,
    }
    
    # Calculate percentages
    total_valid = len(df) - discarded_count
    if total_valid > 0:
        for band, count in analysis['general_summary']['band_counts'].items():
            analysis['general_summary']['band_percentages'][band] = (count / total_valid) * 100
    
    # Save JSON
    json_path = Path(screening_dir) / "frequency_analysis.json"
    print(f"\n💾 Saving JSON analysis to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Generate text report
    print(f"📝 Generating text report...")
    txt_path = Path(screening_dir) / "frequency_analysis.txt"
    generate_text_report(analysis, txt_path)
    
    print("\n" + "=" * 80)
    print("✅ Frequency analysis complete!")
    print(f"📄 JSON: {json_path}")
    print(f"📄 TXT:  {txt_path}")
    print("=" * 80)


def generate_text_report(analysis, output_path):
    """Generate human-readable text report."""
    
    lines = []
    lines.append("⚡🌟💎 ULTRA NECROZMA - FREQUENCY ANALYSIS REPORT 💎🌟⚡")
    lines.append("=" * 100)
    lines.append("")
    
    # Band Descriptions
    lines.append("📊 FREQUENCY BANDS DEFINITION")
    lines.append("-" * 100)
    lines.append("❌ DISCARDED:   < 50 trades       - No statistical significance")
    lines.append("📊 FAIXA 1:     50-500 trades     - Low Frequency (Swing/Position Trading) ~0.2-2 trades/day")
    lines.append("📊 FAIXA 2:     500-5000 trades   - Medium Frequency (Day Trading) ~2-20 trades/day")
    lines.append("📊 FAIXA 3:     5000-50000 trades - High Frequency (Scalping) ~20-200 trades/day")
    lines.append("⚠️  IMPRACTICAL: > 50000 trades    - Too many to operate (>200 trades/day)")
    lines.append("")
    
    # General Summary
    lines.append("📈 GENERAL SUMMARY")
    lines.append("-" * 100)
    gs = analysis['general_summary']
    lines.append(f"Total Strategies Analyzed:  {gs['total_strategies']:,}")
    lines.append(f"Discarded (< 50 trades):    {gs['discarded_count']:,}")
    lines.append("")
    
    lines.append("Distribution by Band:")
    for band in ['FAIXA_1_LOW', 'FAIXA_2_MEDIUM', 'FAIXA_3_HIGH', 'IMPRACTICAL']:
        count = gs['band_counts'][band]
        pct = gs['band_percentages'].get(band, 0)
        band_label = band.replace('_', ' ')
        lines.append(f"  {band_label:<20}: {count:>6,} ({pct:>5.1f}%)")
    lines.append("")
    
    # Analysis for each valid band
    valid_bands = [
        ('FAIXA_1_LOW', 'FAIXA 1 - LOW FREQUENCY (50-500 trades)'),
        ('FAIXA_2_MEDIUM', 'FAIXA 2 - MEDIUM FREQUENCY (500-5000 trades)'),
        ('FAIXA_3_HIGH', 'FAIXA 3 - HIGH FREQUENCY (5000-50000 trades)'),
    ]
    
    for band_key, band_title in valid_bands:
        band_data = analysis['band_analyses'].get(band_key)
        
        if not band_data:
            lines.append(f"📊 {band_title}")
            lines.append("-" * 100)
            lines.append("No strategies in this band.")
            lines.append("")
            continue
        
        lines.append(f"📊 {band_title}")
        lines.append("-" * 100)
        lines.append(f"Total Strategies: {band_data['count']:,}")
        lines.append("")
        
        # Aggregate Statistics
        lines.append("📈 Aggregate Statistics:")
        stats = band_data['aggregate_stats']
        lines.append(f"  {'Metric':<20} {'Mean':>12} {'Median':>12} {'Max':>12} {'Min':>12}")
        lines.append("  " + "-" * 68)
        
        for metric in ['sharpe_ratio', 'profit_factor', 'win_rate', 'n_trades', 'total_return', 'max_drawdown']:
            metric_stats = stats[metric]
            metric_label = metric.replace('_', ' ').title()
            
            if metric == 'win_rate':
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>11.1%} {metric_stats['median']:>11.1%} "
                           f"{metric_stats['max']:>11.1%} {metric_stats['min']:>11.1%}")
            elif metric == 'n_trades':
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>12,.0f} {metric_stats['median']:>12,.0f} "
                           f"{metric_stats['max']:>12,.0f} {metric_stats['min']:>12,.0f}")
            else:
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>12.3f} {metric_stats['median']:>12.3f} "
                           f"{metric_stats['max']:>12.3f} {metric_stats['min']:>12.3f}")
        lines.append("")
        
        # Top 10 by Sharpe Ratio
        lines.append("🏆 Top 10 by Sharpe Ratio:")
        lines.append(f"  {'#':<4} {'Strategy':<55} {'Sharpe':>10} {'PF':>10} {'WinRate':>10} {'Trades':>10}")
        lines.append("  " + "-" * 99)
        
        for i, strat in enumerate(band_data['top_10_sharpe'], 1):
            name = strat['base_strategy']
            if len(name) > 55:
                name = name[:52] + "..."
            lines.append(f"  {i:<4} {name:<55} {strat['sharpe_ratio']:>10.3f} {strat['profit_factor']:>10.3f} "
                       f"{strat['win_rate']:>10.1%} {strat['n_trades']:>10,}")
        lines.append("")
        
        # Top 10 by Profit Factor
        lines.append("💰 Top 10 by Profit Factor:")
        lines.append(f"  {'#':<4} {'Strategy':<55} {'PF':>10} {'Sharpe':>10} {'WinRate':>10} {'Trades':>10}")
        lines.append("  " + "-" * 99)
        
        for i, strat in enumerate(band_data['top_10_profit_factor'], 1):
            name = strat['base_strategy']
            if len(name) > 55:
                name = name[:52] + "..."
            lines.append(f"  {i:<4} {name:<55} {strat['profit_factor']:>10.3f} {strat['sharpe_ratio']:>10.3f} "
                       f"{strat['win_rate']:>10.1%} {strat['n_trades']:>10,}")
        lines.append("")
        
        # Top 10 by Win Rate
        lines.append("🎯 Top 10 by Win Rate:")
        lines.append(f"  {'#':<4} {'Strategy':<55} {'WinRate':>10} {'Sharpe':>10} {'PF':>10} {'Trades':>10}")
        lines.append("  " + "-" * 99)
        
        for i, strat in enumerate(band_data['top_10_win_rate'], 1):
            name = strat['base_strategy']
            if len(name) > 55:
                name = name[:52] + "..."
            lines.append(f"  {i:<4} {name:<55} {strat['win_rate']:>10.1%} {strat['sharpe_ratio']:>10.3f} "
                       f"{strat['profit_factor']:>10.3f} {strat['n_trades']:>10,}")
        lines.append("")
        lines.append("")
    
    # Impractical Band
    impractical = analysis['band_analyses'].get('IMPRACTICAL')
    if impractical:
        lines.append("⚠️  IMPRACTICAL BAND (> 50000 trades)")
        lines.append("-" * 100)
        lines.append(f"Total Strategies: {impractical['count']:,}")
        lines.append("")
        lines.append("⚠️  NOTE: These strategies have too many trades to be practically operated (>200 trades/day).")
        lines.append("         While they may show good metrics, they are not recommended for manual trading.")
        lines.append("")
        
        # Show only aggregate statistics
        lines.append("📈 Aggregate Statistics:")
        stats = impractical['aggregate_stats']
        lines.append(f"  {'Metric':<20} {'Mean':>12} {'Median':>12} {'Max':>12}")
        lines.append("  " + "-" * 56)
        
        for metric in ['sharpe_ratio', 'profit_factor', 'win_rate', 'n_trades']:
            metric_stats = stats[metric]
            metric_label = metric.replace('_', ' ').title()
            
            if metric == 'win_rate':
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>11.1%} {metric_stats['median']:>11.1%} {metric_stats['max']:>11.1%}")
            elif metric == 'n_trades':
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>12,.0f} {metric_stats['median']:>12,.0f} {metric_stats['max']:>12,.0f}")
            else:
                lines.append(f"  {metric_label:<20} {metric_stats['mean']:>12.3f} {metric_stats['median']:>12.3f} {metric_stats['max']:>12.3f}")
        lines.append("")
        lines.append("")
    
    # Discarded Note
    lines.append("❌ DISCARDED STRATEGIES (< 50 trades)")
    lines.append("-" * 100)
    lines.append(f"Total Discarded: {analysis['general_summary']['discarded_count']:,}")
    lines.append("")
    lines.append("ℹ️  NOTE: Strategies with fewer than 50 trades lack statistical significance.")
    lines.append("        They often show extreme Sharpe Ratios (e.g., 1e+17) due to low variance.")
    lines.append("        These have been excluded from all rankings and analysis.")
    lines.append("")
    lines.append("")
    
    # Comparison Between Bands
    lines.append("🔍 COMPARISON BETWEEN BANDS")
    lines.append("-" * 100)
    
    comp = analysis['comparison']
    lines.append("Average Performance by Band:")
    lines.append(f"  {'Metric':<20} {'FAIXA 1':>15} {'FAIXA 2':>15} {'FAIXA 3':>15}")
    lines.append("  " + "-" * 65)
    
    for metric in ['sharpe_ratio', 'profit_factor', 'win_rate', 'total_return']:
        metric_label = metric.replace('_', ' ').title()
        values = comp['metric_comparison'][metric]
        
        f1 = values.get('FAIXA_1_LOW', 0)
        f2 = values.get('FAIXA_2_MEDIUM', 0)
        f3 = values.get('FAIXA_3_HIGH', 0)
        
        if metric == 'win_rate':
            lines.append(f"  {metric_label:<20} {f1:>14.1%} {f2:>14.1%} {f3:>14.1%}")
        else:
            lines.append(f"  {metric_label:<20} {f1:>15.3f} {f2:>15.3f} {f3:>15.3f}")
    
    lines.append("")
    lines.append("Best Band by Metric:")
    for metric, best_band in comp['best_bands'].items():
        metric_label = metric.replace('_', ' ').title()
        band_label = best_band.replace('_', ' ')
        lines.append(f"  {metric_label:<20}: {band_label}")
    lines.append("")
    
    # Recommendation
    lines.append("💡 RECOMMENDATION:")
    # Find which band appears most in best_bands
    band_counts = Counter(comp['best_bands'].values())
    if band_counts:
        best_overall = band_counts.most_common(1)[0][0]
        best_label = best_overall.replace('_', ' ')
        lines.append(f"   Based on average performance, {best_label} shows the strongest overall metrics.")
        lines.append(f"   However, consider your trading style and time availability when choosing.")
    lines.append("")
    lines.append("")
    
    # Final Candidates List
    lines.append("🏆 FINAL CANDIDATE STRATEGIES")
    lines.append("-" * 100)
    lines.append("Top 5 from each valid band (ordered by Sharpe Ratio):")
    lines.append("")
    
    total_candidates = 0
    for band_key, band_label in [
        ('FAIXA_1_LOW', 'FAIXA 1 - LOW FREQUENCY'),
        ('FAIXA_2_MEDIUM', 'FAIXA 2 - MEDIUM FREQUENCY'),
        ('FAIXA_3_HIGH', 'FAIXA 3 - HIGH FREQUENCY'),
    ]:
        candidates = analysis['final_candidates'].get(band_key, [])
        
        if candidates:
            lines.append(f"📊 {band_label}:")
            lines.append(f"  {'#':<4} {'Strategy':<60} {'Sharpe':>10} {'PF':>10} {'WR':>10}")
            lines.append("  " + "-" * 94)
            
            for i, strat in enumerate(candidates, 1):
                total_candidates += 1
                name = strat['strategy_name']
                if len(name) > 60:
                    name = name[:57] + "..."
                lines.append(f"  {i:<4} {name:<60} {strat['sharpe_ratio']:>10.3f} "
                           f"{strat['profit_factor']:>10.3f} {strat['win_rate']:>10.1%}")
            
            lines.append("")
    
    lines.append(f"Total Candidates for GBPUSD Testing: {total_candidates}")
    lines.append("")
    
    # Footer
    lines.append("=" * 100)
    lines.append("END OF FREQUENCY ANALYSIS REPORT")
    lines.append("=" * 100)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    try:
        generate_analysis()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
