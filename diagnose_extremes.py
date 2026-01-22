#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - EXTREME DIAGNOSIS 💎🌟⚡

Diagnoses strategies outside operational ranges:
- < 50 trades: 1,357 strategies (insufficient statistical significance)
- > 50,000 trades: 592 strategies (impractical to operate)

Analyzes patterns, identifies issues, and provides recommendations.
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
    # Exclude output files
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


def filter_extreme_strategies(df):
    """Separate strategies into low and high trade extremes."""
    print("\n🔍 Filtering extreme strategies...")
    
    # Group by base strategy (ignore lot_size)
    df['base_strategy'] = df['strategy_name'].apply(extract_base_strategy_name)
    df_unique = df.sort_values('sharpe_ratio', ascending=False).groupby('base_strategy', as_index=False).first()
    
    # Low trades (< 50)
    low_trades = df_unique[df_unique['n_trades'] < 50].copy()
    
    # High trades (> 50,000)
    high_trades = df_unique[df_unique['n_trades'] > 50000].copy()
    
    print(f"   Strategies with < 50 trades:     {len(low_trades):,}")
    print(f"   Strategies with > 50,000 trades: {len(high_trades):,}")
    
    return low_trades, high_trades


def analyze_low_trade_strategies(df):
    """Analyze strategies with < 50 trades."""
    print("\n📊 Analyzing low trade strategies...")
    
    analysis = {
        'total': len(df),
        'by_template': {},
        'by_param': {},
        'patterns': [],
        'examples': {}
    }
    
    # Breakdown by template
    template_counts = df['template'].value_counts().to_dict()
    analysis['by_template'] = template_counts
    
    # Extract parameters
    df['params'] = df['strategy_name'].apply(parse_strategy_params)
    
    # Analyze common parameter values
    param_values = defaultdict(list)
    for params in df['params']:
        for key, value in params.items():
            param_values[key].append(value)
    
    # Get most common values for each parameter
    for param, values in param_values.items():
        counter = Counter(values)
        analysis['by_param'][param] = {
            'most_common': counter.most_common(5),
            'total_unique': len(set(values))
        }
    
    # Identify patterns
    # Pattern 1: High T threshold
    high_t = df[df['params'].apply(lambda p: p.get('T', 0) > 2.0)]
    if len(high_t) > 0:
        pct = len(high_t) / len(df) * 100
        analysis['patterns'].append(f"{pct:.1f}% of strategies with < 50 trades have T > 2.0")
    
    # Pattern 2: RSI range
    rsi_strategies = df[df['params'].apply(lambda p: 'RSI' in p)]
    if len(rsi_strategies) > 0:
        pct = len(rsi_strategies) / len(df) * 100
        analysis['patterns'].append(f"{pct:.1f}% of strategies with < 50 trades use RSI filters")
    
    # Get examples by trade count ranges
    analysis['examples']['zero_trades'] = df[df['n_trades'] == 0].head(10)
    analysis['examples']['1-10_trades'] = df[(df['n_trades'] >= 1) & (df['n_trades'] <= 10)].head(10)
    analysis['examples']['10-49_trades'] = df[(df['n_trades'] >= 10) & (df['n_trades'] < 50)].head(10)
    
    return analysis


def analyze_high_trade_strategies(df):
    """Analyze strategies with > 50,000 trades."""
    print("\n📊 Analyzing high trade strategies...")
    
    analysis = {
        'total': len(df),
        'by_template': {},
        'by_param': {},
        'patterns': [],
        'distribution': {}
    }
    
    # Breakdown by template
    template_counts = df['template'].value_counts().to_dict()
    analysis['by_template'] = template_counts
    
    # Extract parameters
    df['params'] = df['strategy_name'].apply(parse_strategy_params)
    
    # Analyze common parameter values
    param_values = defaultdict(list)
    for params in df['params']:
        for key, value in params.items():
            param_values[key].append(value)
    
    # Get most common values for each parameter
    for param, values in param_values.items():
        counter = Counter(values)
        analysis['by_param'][param] = {
            'most_common': counter.most_common(5),
            'total_unique': len(set(values))
        }
    
    # Identify patterns
    # Pattern 1: Low T threshold
    low_t = df[df['params'].apply(lambda p: p.get('T', 999) < 1.0)]
    if len(low_t) > 0:
        pct = len(low_t) / len(df) * 100
        analysis['patterns'].append(f"{pct:.1f}% of strategies with > 50k trades have T < 1.0")
    
    # Pattern 2: Low or no cooldown
    no_cd = df[df['params'].apply(lambda p: p.get('CD', 999) <= 30)]
    if len(no_cd) > 0:
        pct = len(no_cd) / len(df) * 100
        analysis['patterns'].append(f"{pct:.1f}% of strategies with > 50k trades have CD ≤ 30 or no CD")
    
    # Distribution by trade count
    analysis['distribution']['50k-100k'] = len(df[(df['n_trades'] >= 50000) & (df['n_trades'] < 100000)])
    analysis['distribution']['100k-500k'] = len(df[(df['n_trades'] >= 100000) & (df['n_trades'] < 500000)])
    analysis['distribution']['500k-1M'] = len(df[(df['n_trades'] >= 500000) & (df['n_trades'] < 1000000)])
    analysis['distribution']['>1M'] = len(df[df['n_trades'] >= 1000000])
    
    return analysis


def analyze_non_functioning_templates(df):
    """Identify templates that produce 0 trades."""
    print("\n🔍 Analyzing non-functioning templates...")
    
    # Group by base strategy
    df['base_strategy'] = df['strategy_name'].apply(extract_base_strategy_name)
    df_unique = df.sort_values('sharpe_ratio', ascending=False).groupby('base_strategy', as_index=False).first()
    
    # Find strategies with 0 trades
    zero_trades = df_unique[df_unique['n_trades'] == 0]
    
    # Group by template
    template_analysis = {}
    
    for template in zero_trades['template'].unique():
        template_df = zero_trades[zero_trades['template'] == template]
        total_template = len(df_unique[df_unique['template'] == template])
        
        template_analysis[template] = {
            'zero_trades_count': len(template_df),
            'total_strategies': total_template,
            'percentage': len(template_df) / total_template * 100 if total_template > 0 else 0,
            'all_zero': len(template_df) == total_template
        }
    
    return template_analysis, zero_trades


def generate_recommendations(low_analysis, high_analysis, template_analysis):
    """Generate recommendations for parameter adjustments and template actions."""
    print("\n💡 Generating recommendations...")
    
    recommendations = {
        'low_trades': [],
        'high_trades': [],
        'templates': []
    }
    
    # Recommendations for low trade strategies
    for param, data in low_analysis['by_param'].items():
        if param == 'T':
            most_common = data['most_common'][0][0] if data['most_common'] else None
            if most_common and most_common > 2.0:
                recommendations['low_trades'].append(
                    f"Reduce T (Threshold) from {most_common} to 0.5-1.5 range for Round 3"
                )
        elif param == 'RSI':
            recommendations['low_trades'].append(
                "Consider wider RSI ranges or removing RSI filter entirely"
            )
    
    # Recommendations for high trade strategies
    for param, data in high_analysis['by_param'].items():
        if param == 'T':
            most_common = data['most_common'][0][0] if data['most_common'] else None
            if most_common and most_common < 1.0:
                recommendations['high_trades'].append(
                    f"Increase T (Threshold) from {most_common} to 1.5-2.5 range"
                )
        elif param == 'CD':
            most_common = data['most_common'][0][0] if data['most_common'] else None
            if most_common and most_common <= 30:
                recommendations['high_trades'].append(
                    f"Add or increase CD (Cooldown) from {most_common} to 300-600 seconds"
                )
    
    # Recommendations for templates
    for template, data in template_analysis.items():
        if data['all_zero']:
            recommendations['templates'].append({
                'template': template,
                'action': 'REMOVE',
                'justification': 'All variations produce 0 trades - logic issue or incompatible with data'
            })
        elif data['percentage'] > 80:
            recommendations['templates'].append({
                'template': template,
                'action': 'REVIEW',
                'justification': f'{data["percentage"]:.1f}% of variations produce 0 trades - likely configuration issue'
            })
        else:
            recommendations['templates'].append({
                'template': template,
                'action': 'ADJUST',
                'justification': f'{data["percentage"]:.1f}% produce 0 trades - consider parameter adjustments'
            })
    
    return recommendations


def generate_report(low_df, high_df, low_analysis, high_analysis, template_analysis, recommendations, output_dir):
    """Generate comprehensive diagnosis report."""
    print("\n📝 Generating diagnosis report...")
    
    report = []
    
    # Header
    report.append("="*100)
    report.append("⚡🌟💎 ULTRA NECROZMA - EXTREME DIAGNOSIS REPORT 💎🌟⚡")
    report.append("="*100)
    report.append("")
    
    # 1. LOW TRADE STRATEGIES
    report.append("="*100)
    report.append("1. STRATEGIES WITH < 50 TRADES (Insufficient Statistical Significance)")
    report.append("="*100)
    report.append("")
    report.append(f"Total: {low_analysis['total']:,} strategies")
    report.append("")
    
    # Breakdown by template
    report.append("BREAKDOWN BY TEMPLATE:")
    report.append("-"*100)
    report.append(f"{'Template':<30} {'Count':>10} {'% of Low Trades':>15}")
    report.append("-"*100)
    
    sorted_templates = sorted(low_analysis['by_template'].items(), key=lambda x: x[1], reverse=True)
    for template, count in sorted_templates[:20]:
        pct = count / low_analysis['total'] * 100
        report.append(f"{template:<30} {count:>10,} {pct:>14.1f}%")
    
    # Parameter analysis
    report.append("")
    report.append("BREAKDOWN BY PARAMETER:")
    report.append("-"*100)
    
    for param, data in sorted(low_analysis['by_param'].items()):
        report.append(f"\nParameter: {param}")
        report.append(f"  Unique values tested: {data['total_unique']}")
        report.append(f"  Most common values:")
        for value, count in data['most_common']:
            pct = count / low_analysis['total'] * 100
            report.append(f"    {value}: {count:,} ({pct:.1f}%)")
    
    # Patterns
    report.append("")
    report.append("PATTERNS IDENTIFIED:")
    report.append("-"*100)
    for pattern in low_analysis['patterns']:
        report.append(f"  • {pattern}")
    
    # Examples
    report.append("")
    report.append("EXAMPLES:")
    report.append("-"*100)
    
    for category, examples in low_analysis['examples'].items():
        if len(examples) > 0:
            report.append(f"\n{category.replace('_', ' ').title()} ({len(examples)} examples):")
            report.append(f"{'Strategy Name':<60} {'Template':<25} {'Trades':>8}")
            report.append("-"*100)
            
            for _, row in examples.iterrows():
                report.append(f"{row['strategy_name']:<60} {row['template']:<25} {int(row['n_trades']):>8}")
    
    # 2. HIGH TRADE STRATEGIES
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("2. STRATEGIES WITH > 50,000 TRADES (Impractical to Operate)")
    report.append("="*100)
    report.append("")
    report.append(f"Total: {high_analysis['total']:,} strategies")
    report.append("")
    
    # Breakdown by template
    report.append("BREAKDOWN BY TEMPLATE:")
    report.append("-"*100)
    report.append(f"{'Template':<30} {'Count':>10} {'% of High Trades':>15}")
    report.append("-"*100)
    
    sorted_templates = sorted(high_analysis['by_template'].items(), key=lambda x: x[1], reverse=True)
    for template, count in sorted_templates[:20]:
        pct = count / high_analysis['total'] * 100
        report.append(f"{template:<30} {count:>10,} {pct:>14.1f}%")
    
    # Parameter analysis
    report.append("")
    report.append("BREAKDOWN BY PARAMETER:")
    report.append("-"*100)
    
    for param, data in sorted(high_analysis['by_param'].items()):
        report.append(f"\nParameter: {param}")
        report.append(f"  Unique values tested: {data['total_unique']}")
        report.append(f"  Most common values:")
        for value, count in data['most_common']:
            pct = count / high_analysis['total'] * 100
            report.append(f"    {value}: {count:,} ({pct:.1f}%)")
    
    # Patterns
    report.append("")
    report.append("PATTERNS IDENTIFIED:")
    report.append("-"*100)
    for pattern in high_analysis['patterns']:
        report.append(f"  • {pattern}")
    
    # Distribution
    report.append("")
    report.append("DISTRIBUTION BY TRADE COUNT:")
    report.append("-"*100)
    for range_name, count in high_analysis['distribution'].items():
        pct = count / high_analysis['total'] * 100 if high_analysis['total'] > 0 else 0
        report.append(f"  {range_name:<15} {count:>10,} ({pct:>5.1f}%)")
    
    # 3. NON-FUNCTIONING TEMPLATES
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("3. ANALYSIS OF NON-FUNCTIONING TEMPLATES (0 Trades)")
    report.append("="*100)
    report.append("")
    
    report.append(f"{'Template':<30} {'Zero Trades':>12} {'Total':>10} {'% Zero':>10} {'Status':<15}")
    report.append("-"*100)
    
    for template, data in sorted(template_analysis.items(), key=lambda x: x[1]['percentage'], reverse=True):
        status = "ALL ZERO" if data['all_zero'] else "PARTIAL"
        report.append(
            f"{template:<30} {data['zero_trades_count']:>12,} {data['total_strategies']:>10,} "
            f"{data['percentage']:>9.1f}% {status:<15}"
        )
    
    # 4. RECOMMENDATIONS
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("4. RECOMMENDATIONS")
    report.append("="*100)
    report.append("")
    
    report.append("FOR STRATEGIES WITH LOW TRADES (<50):")
    report.append("-"*100)
    if recommendations['low_trades']:
        for rec in recommendations['low_trades']:
            report.append(f"  • {rec}")
    else:
        report.append("  • No specific parameter adjustments recommended")
        report.append("  • Consider discarding these strategies due to insufficient activity")
    
    report.append("")
    report.append("FOR STRATEGIES WITH HIGH TRADES (>50,000):")
    report.append("-"*100)
    if recommendations['high_trades']:
        for rec in recommendations['high_trades']:
            report.append(f"  • {rec}")
    else:
        report.append("  • Consider discarding these strategies as impractical to operate")
    
    report.append("")
    report.append("FOR NON-FUNCTIONING TEMPLATES:")
    report.append("-"*100)
    report.append(f"{'Template':<30} {'Action':<15} {'Justification':<50}")
    report.append("-"*100)
    
    for rec in recommendations['templates']:
        report.append(f"{rec['template']:<30} {rec['action']:<15} {rec['justification']:<50}")
    
    # 5. FINAL DECISION
    report.append("")
    report.append("")
    report.append("="*100)
    report.append("5. FINAL DECISION SUMMARY")
    report.append("="*100)
    report.append("")
    
    report.append(f"{'Category':<30} {'Total':>10} {'Recommendation':<50}")
    report.append("-"*100)
    
    report.append(f"{'Low Trades (<50)':<30} {low_analysis['total']:>10,} "
                 f"{'DISCARD - Insufficient statistical significance':<50}")
    
    report.append(f"{'High Trades (>50k)':<30} {high_analysis['total']:>10,} "
                 f"{'DISCARD - Impractical to operate':<50}")
    
    remove_templates = [r for r in recommendations['templates'] if r['action'] == 'REMOVE']
    report.append(f"{'Templates to Remove':<30} {len(remove_templates):>10,} "
                 f"{'REMOVE - Logic issues or incompatible':<50}")
    
    review_templates = [r for r in recommendations['templates'] if r['action'] == 'REVIEW']
    report.append(f"{'Templates to Review':<30} {len(review_templates):>10,} "
                 f"{'REVIEW - Configuration issues':<50}")
    
    adjust_templates = [r for r in recommendations['templates'] if r['action'] == 'ADJUST']
    report.append(f"{'Templates to Adjust':<30} {len(adjust_templates):>10,} "
                 f"{'ADJUST - Parameter tuning for Round 3':<50}")
    
    report.append("")
    report.append("CONCLUSION:")
    report.append("-"*100)
    report.append(f"  • {low_analysis['total']:,} strategies with < 50 trades should be DISCARDED")
    report.append(f"  • {high_analysis['total']:,} strategies with > 50k trades should be DISCARDED")
    report.append(f"  • {len(remove_templates)} templates should be REMOVED from future screenings")
    report.append(f"  • {len(review_templates)} templates need CODE REVIEW")
    report.append(f"  • {len(adjust_templates)} templates can be ADJUSTED for Round 3")
    
    report.append("")
    report.append("="*100)
    report.append("END OF DIAGNOSIS REPORT")
    report.append("="*100)
    
    # Write report
    report_path = Path(output_dir) / "extremes_diagnosis.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Report saved to {report_path}")


def main():
    """Main execution function."""
    print("⚡🌟💎 ULTRA NECROZMA - EXTREME DIAGNOSIS 💎🌟⚡")
    print("="*100)
    print()
    
    # Configuration
    screening_dir = "screening_results"
    output_dir = "screening_results"
    
    # Load data
    df = load_screening_data(screening_dir)
    
    # Clean data
    df = clean_data(df)
    
    # Filter extreme strategies
    low_trades, high_trades = filter_extreme_strategies(df)
    
    # Analyze low trade strategies
    low_analysis = analyze_low_trade_strategies(low_trades)
    
    # Analyze high trade strategies
    high_analysis = analyze_high_trade_strategies(high_trades)
    
    # Analyze non-functioning templates
    template_analysis, zero_trades = analyze_non_functioning_templates(df)
    
    # Generate recommendations
    recommendations = generate_recommendations(low_analysis, high_analysis, template_analysis)
    
    # Save CSV outputs
    print("\n💾 Saving outputs...")
    
    # Combine extreme strategies for CSV
    extreme_df = pd.concat([low_trades, high_trades], ignore_index=True)
    extreme_df['category'] = extreme_df['n_trades'].apply(
        lambda x: 'LOW (<50)' if x < 50 else 'HIGH (>50k)'
    )
    
    csv_path = Path(output_dir) / "extremes_diagnosis.csv"
    extreme_df.to_csv(csv_path, index=False)
    print(f"✅ Saved {csv_path}")
    
    # Generate and save report
    generate_report(low_trades, high_trades, low_analysis, high_analysis, 
                   template_analysis, recommendations, output_dir)
    
    print("\n" + "="*100)
    print("✅ EXTREME DIAGNOSIS COMPLETE!")
    print("="*100)
    print(f"\nGenerated files:")
    print(f"  - {csv_path}")
    print(f"  - {Path(output_dir) / 'extremes_diagnosis.txt'}")


if __name__ == "__main__":
    main()
