#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - SCREENING SUMMARIZER 💎🌟⚡

Analyzes screening results and generates compact JSON and text summaries.
"From infinite strategies, the light reveals the chosen ones"

Technical: Standalone script for analyzing CSV screening results
- Loads all CSVs from screening_results/
- Identifies strategy types and generates statistics
- Finds top performers by multiple metrics
- Exports JSON and TXT summaries
"""

import pandas as pd
import json
import re
from pathlib import Path
from collections import defaultdict
import warnings

warnings.filterwarnings("ignore")


def parse_strategy_params(strategy_name):
    """
    Extract parameters from strategy name.
    
    Example: TrendFollower_L5_T0.5_SL10_TP20
    Returns: {'L': 5, 'T': 0.5, 'SL': 10, 'TP': 20}
    """
    params = {}
    
    # Match patterns like L5, T0.5, SL10, TP20, etc.
    pattern = r'([A-Z]+)([\d.]+)'
    matches = re.findall(pattern, strategy_name)
    
    for key, value in matches:
        try:
            # Try to convert to int first, then float if needed
            if '.' in value:
                params[key] = float(value)
            else:
                params[key] = int(value)
        except ValueError:
            params[key] = value
    
    return params


def load_screening_data(screening_dir):
    """Load all CSV files from screening_results directory."""
    screening_path = Path(screening_dir)
    
    if not screening_path.exists():
        raise FileNotFoundError(f"Directory {screening_dir} does not exist")
    
    csv_files = list(screening_path.glob("*.csv"))
    csv_files = [f for f in csv_files if not f.name.startswith("screening_summary")]
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {screening_dir}")
    
    print(f"📂 Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"   - {f.name}")
    
    dfs = []
    file_info = []
    
    for csv_file in csv_files:
        print(f"📖 Loading {csv_file.name}...")
        df = pd.read_csv(csv_file)
        dfs.append(df)
        file_info.append({
            'filename': csv_file.name,
            'rows': len(df),
            'columns': df.columns.tolist()
        })
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Loaded {len(combined_df):,} total results")
    
    return combined_df, file_info


def get_strategy_type_stats(df):
    """Calculate statistics per strategy type/template."""
    print("\n📊 Calculating strategy type statistics...")
    
    if 'template' not in df.columns:
        print("⚠️  Warning: 'template' column not found")
        return {}
    
    stats = {}
    
    for template in df['template'].unique():
        template_df = df[df['template'] == template]
        
        # Helper to safely get float value, handling NaN
        def safe_float(value):
            if pd.isna(value):
                return None
            return float(value)
        
        stats[template] = {
            'count': len(template_df),
            'sharpe_mean': safe_float(template_df['sharpe_ratio'].mean()),
            'sharpe_max': safe_float(template_df['sharpe_ratio'].max()),
            'sharpe_min': safe_float(template_df['sharpe_ratio'].min()),
            'sortino_mean': safe_float(template_df['sortino_ratio'].mean()),
            'sortino_max': safe_float(template_df['sortino_ratio'].max()),
            'win_rate_mean': safe_float(template_df['win_rate'].mean()),
            'win_rate_max': safe_float(template_df['win_rate'].max()),
            'profit_factor_mean': safe_float(template_df['profit_factor'].mean()),
            'profit_factor_max': safe_float(template_df['profit_factor'].max()),
            'avg_trades': safe_float(template_df['n_trades'].mean()),
        }
    
    return stats


def get_top_strategies(df, metric, n=20, min_trades=None, ascending=False):
    """Get top N strategies by specified metric."""
    
    # Filter by minimum trades if specified
    filtered_df = df.copy()
    if min_trades:
        filtered_df = filtered_df[filtered_df['n_trades'] >= min_trades]
    
    # Sort and get top N
    top_df = filtered_df.nlargest(n, metric) if not ascending else filtered_df.nsmallest(n, metric)
    
    # Convert to list of dicts with NaN handling
    top_strategies = []
    for _, row in top_df.iterrows():
        def safe_float(value):
            if pd.isna(value):
                return None
            return float(value)
        
        top_strategies.append({
            'strategy_name': row['strategy_name'],
            'template': row.get('template', 'Unknown'),
            'lot_size': safe_float(row['lot_size']),
            metric: safe_float(row[metric]),
            'sharpe_ratio': safe_float(row['sharpe_ratio']),
            'sortino_ratio': safe_float(row['sortino_ratio']),
            'win_rate': safe_float(row['win_rate']),
            'profit_factor': safe_float(row['profit_factor']),
            'n_trades': int(row['n_trades']) if not pd.isna(row['n_trades']) else 0,
            'net_pnl': safe_float(row['net_pnl'])
        })
    
    return top_strategies


def get_metric_distributions(df):
    """Calculate distribution of strategies across metric thresholds."""
    print("\n📈 Calculating metric distributions...")
    
    distributions = {
        'sharpe_ratio': {
            'total': len(df),
            'above_0': int((df['sharpe_ratio'] > 0).sum()),
            'above_0.5': int((df['sharpe_ratio'] > 0.5).sum()),
            'above_1.0': int((df['sharpe_ratio'] > 1.0).sum()),
            'above_1.5': int((df['sharpe_ratio'] > 1.5).sum()),
            'above_2.0': int((df['sharpe_ratio'] > 2.0).sum()),
        },
        'win_rate': {
            'total': len(df),
            'above_40pct': int((df['win_rate'] > 0.40).sum()),
            'above_50pct': int((df['win_rate'] > 0.50).sum()),
            'above_60pct': int((df['win_rate'] > 0.60).sum()),
            'above_70pct': int((df['win_rate'] > 0.70).sum()),
        },
        'profit_factor': {
            'total': len(df),
            'above_1.0': int((df['profit_factor'] > 1.0).sum()),
            'above_1.5': int((df['profit_factor'] > 1.5).sum()),
            'above_2.0': int((df['profit_factor'] > 2.0).sum()),
            'above_2.5': int((df['profit_factor'] > 2.5).sum()),
        }
    }
    
    return distributions


def analyze_parameters(df):
    """Analyze parameter impact on performance."""
    print("\n🔍 Analyzing parameter impact...")
    
    # Extract parameters from strategy names
    df['params'] = df['strategy_name'].apply(parse_strategy_params)
    
    # Get all unique parameter keys
    all_keys = set()
    for params in df['params']:
        all_keys.update(params.keys())
    
    param_analysis = {}
    
    for key in all_keys:
        # Get rows that have this parameter
        rows_with_param = df[df['params'].apply(lambda x: key in x)]
        
        if len(rows_with_param) == 0:
            continue
        
        # Group by parameter value
        values_dict = defaultdict(list)
        for _, row in rows_with_param.iterrows():
            value = row['params'][key]
            values_dict[value].append({
                'sharpe': row['sharpe_ratio'],
                'sortino': row['sortino_ratio'],
                'win_rate': row['win_rate'],
                'profit_factor': row['profit_factor']
            })
        
        # Calculate averages per value
        param_stats = {}
        for value, records in values_dict.items():
            param_stats[str(value)] = {
                'count': len(records),
                'avg_sharpe': sum(r['sharpe'] for r in records) / len(records),
                'avg_sortino': sum(r['sortino'] for r in records) / len(records),
                'avg_win_rate': sum(r['win_rate'] for r in records) / len(records),
                'avg_profit_factor': sum(r['profit_factor'] for r in records) / len(records),
            }
        
        param_analysis[key] = param_stats
    
    # Remove temporary column
    df.drop('params', axis=1, inplace=True)
    
    return param_analysis


def generate_summary(screening_dir="screening_results"):
    """Main function to generate screening summary."""
    print("⚡🌟💎 ULTRA NECROZMA - SCREENING SUMMARIZER 💎🌟⚡")
    print("=" * 60)
    
    # Load data
    df, file_info = load_screening_data(screening_dir)
    
    # General info
    general_info = {
        'total_results': len(df),
        'files_processed': [f['filename'] for f in file_info],
        'file_details': file_info,
        'columns': df.columns.tolist(),
        'unique_templates': df['template'].unique().tolist() if 'template' in df.columns else []
    }
    
    # Strategy type statistics
    strategy_stats = get_strategy_type_stats(df)
    
    # Top strategies by different metrics
    print("\n🏆 Finding top strategies...")
    top_strategies = {
        'top_20_sharpe': get_top_strategies(df, 'sharpe_ratio', n=20),
        'top_20_sortino': get_top_strategies(df, 'sortino_ratio', n=20),
        'top_20_win_rate': get_top_strategies(df, 'win_rate', n=20, min_trades=100),
        'top_20_profit_factor': get_top_strategies(df, 'profit_factor', n=20, min_trades=100),
    }
    
    # Metric distributions
    distributions = get_metric_distributions(df)
    
    # Parameter analysis
    param_analysis = analyze_parameters(df)
    
    # Build complete summary
    summary = {
        'general_info': general_info,
        'strategy_type_stats': strategy_stats,
        'top_strategies': top_strategies,
        'metric_distributions': distributions,
        'parameter_analysis': param_analysis
    }
    
    # Save JSON
    json_path = Path(screening_dir) / "screening_summary.json"
    print(f"\n💾 Saving JSON summary to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate text report
    print(f"📝 Generating text report...")
    txt_path = Path(screening_dir) / "screening_summary.txt"
    generate_text_report(summary, txt_path)
    
    print("\n" + "=" * 60)
    print("✅ Summary generation complete!")
    print(f"📄 JSON: {json_path}")
    print(f"📄 TXT:  {txt_path}")
    print("=" * 60)


def generate_text_report(summary, output_path):
    """Generate human-readable text report."""
    
    def format_value(value, is_percentage=False, width=10):
        """Format value handling extreme numbers and NaN."""
        if value is None:
            return f"{'N/A':>{width}}"
        if is_percentage:
            return f"{value:>{width}.1%}"
        # Use scientific notation for very large or very small values
        if abs(value) > 1e6 or (abs(value) < 0.001 and value != 0):
            return f"{value:>{width}.2e}"
        return f"{value:>{width}.3f}"
    
    lines = []
    lines.append("⚡🌟💎 ULTRA NECROZMA - SCREENING SUMMARY REPORT 💎🌟⚡")
    lines.append("=" * 80)
    lines.append("")
    
    # General Info
    lines.append("📊 GENERAL INFORMATION")
    lines.append("-" * 80)
    gi = summary['general_info']
    lines.append(f"Total Results:      {gi['total_results']:,}")
    lines.append(f"Files Processed:    {', '.join(gi['files_processed'])}")
    lines.append(f"Unique Templates:   {len(gi['unique_templates'])}")
    lines.append(f"Templates:          {', '.join(gi['unique_templates'])}")
    lines.append("")
    
    # Strategy Type Statistics
    lines.append("🎯 STRATEGY TYPE STATISTICS")
    lines.append("-" * 80)
    lines.append(f"{'Template':<25} {'Count':>8} {'Sharpe':>10} {'Sortino':>10} {'WinRate':>10} {'PF':>10}")
    lines.append("-" * 80)
    
    stats = summary['strategy_type_stats']
    # Sort by count descending
    sorted_templates = sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for template, data in sorted_templates:
        lines.append(
            f"{template:<25} {data['count']:>8,} "
            f"{format_value(data['sharpe_mean'])} {format_value(data['sortino_mean'])} "
            f"{format_value(data['win_rate_mean'], is_percentage=True)} {format_value(data['profit_factor_mean'])}"
        )
    lines.append("")
    
    # Top Strategies
    for metric_key, metric_name, actual_col in [
        ('top_20_sharpe', 'SHARPE RATIO', 'sharpe_ratio'),
        ('top_20_sortino', 'SORTINO RATIO', 'sortino_ratio'),
        ('top_20_win_rate', 'WIN RATE', 'win_rate'),
        ('top_20_profit_factor', 'PROFIT FACTOR', 'profit_factor')
    ]:
        lines.append(f"🏆 TOP 20 STRATEGIES BY {metric_name}")
        lines.append("-" * 80)
        lines.append(f"{'Rank':<6} {'Strategy Name':<50} {'Value':>10} {'Sharpe':>10}")
        lines.append("-" * 80)
        
        top_list = summary['top_strategies'][metric_key]
        metric_col = actual_col
        
        for i, strat in enumerate(top_list, 1):
            value = strat[metric_col]
            sharpe = strat['sharpe_ratio']
            
            # Format value based on metric
            if 'rate' in metric_col:
                value_str = format_value(value, is_percentage=True)
            else:
                value_str = format_value(value)
            
            # Truncate strategy name if too long
            name = strat['strategy_name']
            if len(name) > 50:
                name = name[:47] + "..."
            
            lines.append(f"{i:<6} {name:<50} {value_str} {format_value(sharpe)}")
        
        lines.append("")
    
    # Metric Distributions
    lines.append("📈 METRIC DISTRIBUTIONS")
    lines.append("-" * 80)
    
    dist = summary['metric_distributions']
    
    lines.append("Sharpe Ratio Distribution:")
    for threshold, count in dist['sharpe_ratio'].items():
        if threshold == 'total':
            continue
        pct = count / dist['sharpe_ratio']['total'] * 100
        lines.append(f"  {threshold:<15}: {count:>8,} ({pct:>5.1f}%)")
    lines.append("")
    
    lines.append("Win Rate Distribution:")
    for threshold, count in dist['win_rate'].items():
        if threshold == 'total':
            continue
        pct = count / dist['win_rate']['total'] * 100
        lines.append(f"  {threshold:<15}: {count:>8,} ({pct:>5.1f}%)")
    lines.append("")
    
    lines.append("Profit Factor Distribution:")
    for threshold, count in dist['profit_factor'].items():
        if threshold == 'total':
            continue
        pct = count / dist['profit_factor']['total'] * 100
        lines.append(f"  {threshold:<15}: {count:>8,} ({pct:>5.1f}%)")
    lines.append("")
    
    # Parameter Analysis
    lines.append("🔍 PARAMETER ANALYSIS")
    lines.append("-" * 80)
    
    param_analysis = summary['parameter_analysis']
    for param_key in sorted(param_analysis.keys()):
        param_data = param_analysis[param_key]
        lines.append(f"\nParameter: {param_key}")
        lines.append(f"  {'Value':<15} {'Count':>8} {'Sharpe':>10} {'Sortino':>10} {'WinRate':>10} {'PF':>10}")
        lines.append("  " + "-" * 73)
        
        # Sort by count descending
        sorted_values = sorted(param_data.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for value, stats in sorted_values[:10]:  # Show top 10 values
            lines.append(
                f"  {value:<15} {stats['count']:>8,} "
                f"{format_value(stats['avg_sharpe'])} {format_value(stats['avg_sortino'])} "
                f"{format_value(stats['avg_win_rate'], is_percentage=True)} {format_value(stats['avg_profit_factor'])}"
            )
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    try:
        generate_summary()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
