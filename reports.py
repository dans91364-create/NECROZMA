#!/usr/bin/env python3
# -*- coding:  utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - REPORT GENERATOR 💎🌟⚡

The Final Judgment:  Crystallized Knowledge
"Light transformed into eternal wisdom"

Technical:  Report generation and analysis output
- JSON report generation
- Pattern analysis summaries
- Trading recommendations
- Statistical summaries
"""

import numpy as np
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import time

from config import (
    MOVEMENT_LEVELS, DIRECTIONS, CONFIDENCE_THRESHOLDS,
    TOP_PATTERNS_PER_LEVEL, THEME, get_output_dirs
)


# ═══════════════════════════════════════════════════════════════
# 🌟 Z-MOVE:  LIGHT THAT BURNS THE SKY (Final Judgment)
# ═══════════════════════════════════════════════════════════════

def light_that_burns_the_sky(analyzer):
    """
    Z-MOVE: Light That Burns The Sky (Supreme Judgment)
    Technical: Generate final analysis and recommendations
    
    Args:
        analyzer: UltraNecrozmaAnalyzer instance with results
        
    Returns:
        dict:  Final judgment with recommendations
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⚡💎🌟 Z-MOVE: LIGHT THAT BURNS THE SKY 🌟💎⚡            ║
║                                                              ║
║   "The ultimate attack that illuminates all truth..."        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    judgment_start = time.time()
    
    results = analyzer.results
    
    if not results:
        print("   ⚠️ No results to judge")
        return None
    
    # ═══ PHASE 1: COLLECT DATA ═══
    print("🌟 Phase 1: PHOTON GEYSER - Data Collection")
    print("─" * 60)
    
    all_rankings = analyzer.get_rankings()
    pattern_summary = analyzer.get_pattern_summary()
    
    # Collect all feature stats
    all_feature_stats = defaultdict(list)
    all_patterns_by_level = defaultdict(lambda: defaultdict(list))
    
    for name, result in results.items():
        if not result:
            continue
        
        for level in result["results"]: 
            for direction in result["results"][level]:
                level_data = result["results"][level][direction]
                
                # Collect feature stats
                for key, value in level_data.get("feature_stats", {}).items():
                    if isinstance(value, (int, float)):
                        all_feature_stats[key].append(value)
                
                # Collect patterns
                for pattern, data in level_data. get("patterns", {}).items():
                    if data["count"] >= 2:
                        all_patterns_by_level[level][direction]. append({
                            "pattern": pattern,
                            "count": data["count"],
                            "universe": name
                        })
    
    print(f"   ✅ Collected data from {len(results)} universes")
    print(f"   ✅ {len(all_feature_stats)} unique feature statistics")
    
    # ═══ PHASE 2: SUPREME RANKING ═══
    print(f"\n💎 Phase 2: PRISMATIC LASER - Supreme Ranking")
    print("─" * 60)
    
    if all_rankings:
        print(f"\n🏆 TOP 10 SUPREME CONFIGURATIONS:\n")
        print(f"{'#':<4} {'Universe':<25} {'Int':<5} {'LB':<4} {'Patterns':<10} {'Score':<10}")
        print("─" * 65)
        
        for idx, rank in enumerate(all_rankings[:10], 1):
            emoji = "💎" if idx == 1 else "🌟" if idx <= 3 else "⚡" if idx <= 5 else "✨"
            print(f"{emoji}{idx:<3} {rank['name']:<25} {rank['interval']:<5} {rank['lookback']: <4} "
                  f"{rank['total_patterns']:<10} {rank['score']:<10.1f}")
    
    # ═══ PHASE 3: MARKET REGIME ANALYSIS ═══
    print(f"\n⚡ Phase 3: DIVINE CHARACTERISTICS - Market Regime")
    print("─" * 60)
    
    # Calculate mean values for key features
    dfa_values = all_feature_stats.get("dfa_alpha_mean", [])
    hurst_values = all_feature_stats.get("hurst_mean", [])
    lyapunov_values = all_feature_stats.get("lyapunov_mean", [])
    fractal_values = all_feature_stats.get("fractal_dim_mean", [])
    entropy_values = all_feature_stats.get("entropy_shannon_mean", [])
    
    dfa_mean = np.mean(dfa_values) if dfa_values else 0.5
    hurst_mean = np. mean(hurst_values) if hurst_values else 0.5
    lyapunov_mean = np.mean(lyapunov_values) if lyapunov_values else 0.0
    fractal_mean = np.mean(fractal_values) if fractal_values else 1.5
    entropy_mean = np. mean(entropy_values) if entropy_values else 2.0
    
    # Determine market regime
    regime = determine_market_regime(dfa_mean, hurst_mean, lyapunov_mean)
    
    print(f"\n📊 ULTRA NECROZMA MARKET ANALYSIS:")
    
    print(f"\n   🌊 DFA Alpha:  {dfa_mean:.3f}")
    if dfa_mean > 0.6:
        print(f"      → Market:  STRONGLY PERSISTENT (powerful trends)")
    elif dfa_mean > 0.52:
        print(f"      → Market: PERSISTENT (trending behavior)")
    elif dfa_mean < 0.48:
        print(f"      → Market: ANTI-PERSISTENT (mean reversion)")
    else:
        print(f"      → Market: RANDOM WALK (neutral/efficient)")
    
    print(f"\n   🌀 Hurst Exponent:  {hurst_mean:.3f}")
    if hurst_mean > 0.55:
        print(f"      → Long Memory: STRONG (persistent trends)")
    elif hurst_mean < 0.45:
        print(f"      → Long Memory:  ANTI-PERSISTENT (reversions)")
    else:
        print(f"      → Long Memory:  WEAK (short-term patterns)")
    
    print(f"\n   ⚡ Lyapunov Exponent: {lyapunov_mean:.4f}")
    if abs(lyapunov_mean) > 0.05:
        chaos_level = "HIGH"
        print(f"      → Chaos Level: {chaos_level} (highly sensitive)")
    elif abs(lyapunov_mean) > 0.02:
        chaos_level = "MODERATE"
        print(f"      → Chaos Level: {chaos_level} (moderately sensitive)")
    else:
        chaos_level = "LOW"
        print(f"      → Chaos Level: {chaos_level} (stable)")
    
    print(f"\n   📐 Fractal Dimension: {fractal_mean:.3f}")
    if fractal_mean > 1.6:
        complexity = "VERY_HIGH"
        print(f"      → Complexity: {complexity} (intricate patterns)")
    elif fractal_mean > 1.4:
        complexity = "HIGH"
        print(f"      → Complexity: {complexity} (complex patterns)")
    else:
        complexity = "MODERATE"
        print(f"      → Complexity: {complexity} (simpler patterns)")
    
    print(f"\n   🔮 Shannon Entropy: {entropy_mean:.3f}")
    if entropy_mean > 3.0:
        print(f"      → Randomness: HIGH (unpredictable)")
    elif entropy_mean > 2.0:
        print(f"      → Randomness: MODERATE (semi-predictable)")
    else:
        print(f"      → Randomness: LOW (more predictable)")
    
    # ═══ PHASE 4: LEVEL ANALYSIS ═══
    print(f"\n🔮 Phase 4: PRISMATIC ANALYSIS - Movement Levels")
    print("─" * 60)
    
    level_analysis = {}
    
    for level in MOVEMENT_LEVELS. keys():
        level_analysis[level] = {
            "up":  {"total": 0, "top_patterns": []},
            "down": {"total": 0, "top_patterns": []}
        }
        
        print(f"\n   🎯 {level.upper()} ({MOVEMENT_LEVELS[level]['technical']}):")
        
        for direction in DIRECTIONS:
            total = pattern_summary[level][direction]["total_occurrences"]
            level_analysis[level][direction]["total"] = total
            
            # Get top patterns for this level/direction
            patterns = all_patterns_by_level[level][direction]
            patterns. sort(key=lambda x: x["count"], reverse=True)
            top_patterns = patterns[:5]
            level_analysis[level][direction]["top_patterns"] = top_patterns
            
            dir_emoji = "📈" if direction == "up" else "📉"
            print(f"      {dir_emoji} {direction.upper()}: {total: ,} occurrences")
            
            if top_patterns:
                for i, p in enumerate(top_patterns[:3], 1):
                    print(f"         {i}. {p['pattern'][: 40]}...  (x{p['count']})")
    
    # ═══ PHASE 5: TRADING RECOMMENDATIONS ═══
    print(f"\n🌟 Phase 5: SUPREME RECOMMENDATIONS")
    print("─" * 60)
    
    recommendations = generate_recommendations(
        regime, all_rankings, level_analysis, 
        dfa_mean, hurst_mean, chaos_level
    )
    
    print(f"\n⚡ TRADING STRATEGY RECOMMENDATION:")
    print(f"\n   🎯 Primary Strategy: {recommendations['primary_strategy']}")
    print(f"   📊 Confidence:  {recommendations['confidence']}")
    
    print(f"\n   📋 Key Points:")
    for point in recommendations['key_points']: 
        print(f"      • {point}")
    
    if all_rankings:
        best = all_rankings[0]
        print(f"\n   💎 OPTIMAL CONFIGURATION:")
        print(f"      Universe: {best['name']}")
        print(f"      Interval: {best['interval']} minutes")
        print(f"      Lookback: {best['lookback']} periods")
        print(f"      Score: {best['score']:.1f}")
    
    # ═══ PHASE 6: FINAL SUMMARY ═══
    judgment_time = time.time() - judgment_start
    
    print(f"\n⚡ Phase 6: FINAL JUDGMENT")
    print("═" * 60)
    
    total_patterns = sum(
        pattern_summary[l][d]["total_occurrences"]
        for l in MOVEMENT_LEVELS for d in DIRECTIONS
    )
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   🌌 Universes Analyzed: {len(results)}")
    print(f"   🎯 Total Patterns: {total_patterns:,}")
    print(f"   ⏱️ Judgment Time: {judgment_time:.2f}s")
    
    print(f"\n🌟 ULTRA NECROZMA STATUS:")
    print(f"   Evolution: {analyzer.evolution_stage}")
    print(f"   Light Power: {analyzer.light_power:. 1f}%")
    print(f"   Prismatic Cores: {len(analyzer.prismatic_cores)}/7")
    
    if analyzer.light_power >= 100:
        print(f"\n⚡💎🌟 MAXIMUM POWER ACHIEVED - TRANSCENDENCE COMPLETE!  🌟💎⚡")
    
    # ═══ BUILD FINAL JUDGMENT OBJECT ═══
    final_judgment = {
        "z_move": "LIGHT_THAT_BURNS_THE_SKY",
        "timestamp": datetime.now().isoformat(),
        "judgment_time_seconds": judgment_time,
        
        "summary": {
            "universes_analyzed": len(results),
            "total_patterns": total_patterns,
            "evolution_stage": analyzer.evolution_stage,
            "light_power":  analyzer.light_power,
            "prismatic_cores": analyzer.prismatic_cores
        },
        
        "market_regime": {
            "regime": regime,
            "dfa_alpha":  float(dfa_mean),
            "hurst_exponent": float(hurst_mean),
            "lyapunov_exponent": float(lyapunov_mean),
            "fractal_dimension": float(fractal_mean),
            "shannon_entropy": float(entropy_mean),
            "chaos_level": chaos_level,
            "complexity": complexity
        },
        
        "rankings": all_rankings[: 20],  # Top 20
        
        "level_analysis": level_analysis,
        
        "recommendations": recommendations,
        
        "best_configuration": all_rankings[0] if all_rankings else None
    }
    
    return final_judgment


# ═══════════════════════════════════════════════════════════════
# 📊 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def determine_market_regime(dfa, hurst, lyapunov):
    """
    Determine market regime from key indicators
    Technical:  Classify market behavior based on chaos/persistence metrics
    """
    if dfa > 0.6 and hurst > 0.55: 
        return "STRONG_TRENDING"
    elif dfa > 0.52 or hurst > 0.52:
        return "TRENDING"
    elif dfa < 0.48 or hurst < 0.48:
        return "MEAN_REVERTING"
    else:
        return "RANDOM_WALK"


def generate_recommendations(regime, rankings, level_analysis, dfa, hurst, chaos_level):
    """
    Generate trading recommendations based on analysis
    Technical: Strategy suggestion based on market regime
    """
    recommendations = {
        "primary_strategy": "",
        "confidence": "",
        "key_points": [],
        "risk_level": "",
        "optimal_timeframe": ""
    }
    
    # Determine strategy based on regime
    if regime == "STRONG_TRENDING":
        recommendations["primary_strategy"] = "AGGRESSIVE TREND-FOLLOWING"
        recommendations["confidence"] = "HIGH"
        recommendations["risk_level"] = "MEDIUM-HIGH"
        recommendations["key_points"] = [
            "Enter on breakouts with momentum confirmation",
            "Hold positions for extended moves",
            "Use trailing stops to protect profits",
            "Avoid counter-trend trades",
            "Best for: Grande and Muito Grande movements"
        ]
    
    elif regime == "TRENDING": 
        recommendations["primary_strategy"] = "MODERATE TREND-FOLLOWING"
        recommendations["confidence"] = "MEDIUM-HIGH"
        recommendations["risk_level"] = "MEDIUM"
        recommendations["key_points"] = [
            "Wait for pullbacks to enter trends",
            "Use 2-3 candle confirmation before entry",
            "Set reasonable profit targets",
            "Consider partial position scaling",
            "Best for:  Médio and Grande movements"
        ]
    
    elif regime == "MEAN_REVERTING":
        recommendations["primary_strategy"] = "MEAN-REVERSION / RANGE TRADING"
        recommendations["confidence"] = "MEDIUM-HIGH"
        recommendations["risk_level"] = "MEDIUM"
        recommendations["key_points"] = [
            "Enter at extremes (overbought/oversold)",
            "Quick in-and-out trades",
            "Look for reversal crystal patterns",
            "Tight stop losses near support/resistance",
            "Best for:  Pequeno and Médio movements"
        ]
    
    else:  # RANDOM_WALK
        recommendations["primary_strategy"] = "ADAPTIVE / WAIT FOR CLARITY"
        recommendations["confidence"] = "LOW-MEDIUM"
        recommendations["risk_level"] = "LOW"
        recommendations["key_points"] = [
            "Wait for clear pattern formation",
            "Use tight risk management",
            "Reduce position sizes",
            "Focus on high-confidence setups only",
            "Consider staying out until regime clarifies"
        ]
    
    # Add optimal timeframe from rankings
    if rankings:
        best = rankings[0]
        recommendations["optimal_timeframe"] = f"{best['interval']}min"
        recommendations["key_points"].append(
            f"Optimal timeframe: {best['interval']} minute candles with {best['lookback']} lookback"
        )
    
    # Add chaos-specific advice
    if chaos_level == "HIGH":
        recommendations["key_points"].append(
            "⚠️ High chaos detected - use wider stops and smaller positions"
        )
    
    return recommendations


# ═══════════════════════════════════════════════════════════════
# 💾 REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_full_report(analyzer, final_judgment):
    """
    Generate complete JSON report (Crystal Archive)
    Technical: Serialize all analysis results to JSON files
    
    Args:
        analyzer: UltraNecrozmaAnalyzer instance
        final_judgment: Result from light_that_burns_the_sky
        
    Returns:
        dict:  Paths to generated reports
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         💾 GENERATING CRYSTAL ARCHIVE 💾                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    output_dirs = get_output_dirs()
    reports_dir = output_dirs["reports"]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_paths = {}
    
    # Check if we have results
    if final_judgment is None:
        print("⚠️  No results to generate reports - creating minimal report...")
        
        # Create minimal report for no-results case
        minimal_file = reports_dir / f"no_results_{timestamp}.json"
        minimal_report = {
            "generated_at": datetime.now().isoformat(),
            "status": "No results",
            "message": "Analysis completed but no patterns were found. This may be due to insufficient data.",
            "universes_processed": len(analyzer.results),
            "total_patterns": analyzer.total_patterns
        }
        
        with open(minimal_file, "w", encoding="utf-8") as f:
            json.dump(minimal_report, f, indent=2, ensure_ascii=False, default=str)
        
        report_paths["minimal"] = str(minimal_file)
        print(f"   ✅ Saved: {minimal_file.name}")
        
        return report_paths
    
    # ═══ 1. FINAL JUDGMENT REPORT ═══
    print("📄 Generating Final Judgment Report...")
    
    judgment_file = reports_dir / f"final_judgment_{timestamp}.json"
    with open(judgment_file, "w", encoding="utf-8") as f:
        json.dump(final_judgment, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["final_judgment"] = str(judgment_file)
    print(f"   ✅ Saved:  {judgment_file. name}")
    
    # ═══ 2. RANKINGS REPORT ═══
    print("📄 Generating Rankings Report...")
    
    rankings = analyzer.get_rankings()
    rankings_file = reports_dir / f"rankings_{timestamp}.json"
    
    rankings_report = {
        "generated_at": datetime.now().isoformat(),
        "total_universes": len(rankings),
        "rankings": rankings,
        "top_10_summary": [
            {
                "rank": i + 1,
                "name": r["name"],
                "interval_minutes": r["interval"],
                "lookback_periods":  r["lookback"],
                "total_patterns": r["total_patterns"],
                "score": r["score"]
            }
            for i, r in enumerate(rankings[:10])
        ]
    }
    
    with open(rankings_file, "w", encoding="utf-8") as f:
        json.dump(rankings_report, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["rankings"] = str(rankings_file)
    print(f"   ✅ Saved: {rankings_file. name}")
    
    # ═══ 3. MARKET ANALYSIS REPORT ═══
    print("📄 Generating Market Analysis Report...")
    
    market_file = reports_dir / f"market_analysis_{timestamp}.json"
    
    market_report = {
        "generated_at": datetime.now().isoformat(),
        "regime": final_judgment.get("market_regime", {}),
        "interpretation": get_regime_interpretation(final_judgment.get("market_regime", {})),
        "recommendations": final_judgment.get("recommendations", {})
    }
    
    with open(market_file, "w", encoding="utf-8") as f:
        json.dump(market_report, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["market_analysis"] = str(market_file)
    print(f"   ✅ Saved: {market_file.name}")
    
    # ═══ 4. PATTERN CATALOG ═══
    print("📄 Generating Pattern Catalog...")
    
    catalog_file = reports_dir / f"pattern_catalog_{timestamp}.json"
    
    pattern_catalog = {
        "generated_at": datetime.now().isoformat(),
        "levels": {}
    }
    
    for level in MOVEMENT_LEVELS. keys():
        pattern_catalog["levels"][level] = {
            "technical_name":  MOVEMENT_LEVELS[level]["technical"],
            "pip_range": f"{MOVEMENT_LEVELS[level]['min']}-{MOVEMENT_LEVELS[level]['max']}",
            "directions": final_judgment.get("level_analysis", {}). get(level, {})
        }
    
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(pattern_catalog, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["pattern_catalog"] = str(catalog_file)
    print(f"   ✅ Saved: {catalog_file.name}")
    
    # ═══ 5. EXECUTIVE SUMMARY ═══
    print("📄 Generating Executive Summary...")
    
    summary_file = reports_dir / f"executive_summary_{timestamp}.json"
    
    best_config = final_judgment. get("best_configuration", {})
    
    executive_summary = {
        "generated_at": datetime.now().isoformat(),
        "project":  "Ultra Necrozma Forex Analysis",
        "version": "2.0",
        
        "key_findings": {
            "market_regime": final_judgment.get("market_regime", {}).get("regime", "Unknown"),
            "primary_strategy": final_judgment.get("recommendations", {}).get("primary_strategy", "N/A"),
            "confidence_level": final_judgment.get("recommendations", {}).get("confidence", "N/A"),
            "optimal_configuration": {
                "interval": best_config.get("interval", "N/A"),
                "lookback": best_config.get("lookback", "N/A"),
                "score": best_config.get("score", 0)
            }
        },
        
        "statistics": {
            "universes_analyzed": final_judgment.get("summary", {}).get("universes_analyzed", 0),
            "total_patterns_found": final_judgment.get("summary", {}).get("total_patterns", 0),
            "analysis_power": f"{final_judgment.get('summary', {}).get('light_power', 0)}%"
        },
        
        "market_characteristics": {
            "trend_strength": "Strong" if final_judgment.get("market_regime", {}).get("dfa_alpha", 0.5) > 0.55 else "Weak",
            "memory_type": "Long" if final_judgment.get("market_regime", {}).get("hurst_exponent", 0.5) > 0.55 else "Short",
            "chaos_level": final_judgment.get("market_regime", {}).get("chaos_level", "Unknown"),
            "complexity": final_judgment.get("market_regime", {}).get("complexity", "Unknown")
        },
        
        "action_items": final_judgment.get("recommendations", {}).get("key_points", [])
    }
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(executive_summary, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["executive_summary"] = str(summary_file)
    print(f"   ✅ Saved: {summary_file.name}")
    
    # ═══ 6. COMBINED MASTER REPORT ═══
    print("📄 Generating Master Report...")
    
    master_file = reports_dir / f"ULTRA_NECROZMA_MASTER_REPORT_{timestamp}.json"
    
    master_report = {
        "header": {
            "title": "⚡🌟💎 ULTRA NECROZMA MASTER REPORT 💎🌟⚡",
            "subtitle": "Light That Burns The Sky - Complete Analysis",
            "generated_at": datetime.now().isoformat(),
            "version": "2.0"
        },
        
        "executive_summary": executive_summary,
        "market_analysis": market_report,
        "rankings": rankings_report,
        "pattern_catalog": pattern_catalog,
        "full_judgment": final_judgment,
        
        "footer": {
            "theme":  THEME,
            "evolution_achieved": final_judgment.get("summary", {}).get("evolution_stage", "Unknown"),
            "prismatic_cores_collected": final_judgment.get("summary", {}).get("prismatic_cores", [])
        }
    }
    
    with open(master_file, "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=2, ensure_ascii=False, default=str)
    
    report_paths["master_report"] = str(master_file)
    print(f"   ✅ Saved:  {master_file.name}")
    
    # ═══ SUMMARY ═══
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            💾 CRYSTAL ARCHIVE COMPLETE 💾                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║   📄 Reports Generated: {len(report_paths): <5}                              ║
║   📂 Location: {str(reports_dir):<40} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("📄 Generated Files:")
    for name, path in report_paths.items():
        print(f"   • {name}:  {Path(path).name}")
    
    return report_paths


def get_regime_interpretation(regime_data):
    """
    Get human-readable interpretation of market regime
    Technical: Translate metrics into actionable insights
    """
    regime = regime_data.get("regime", "UNKNOWN")
    dfa = regime_data.get("dfa_alpha", 0.5)
    hurst = regime_data.get("hurst_exponent", 0.5)
    
    interpretations = {
        "STRONG_TRENDING": {
            "description": "Market shows strong trending behavior with persistent price movements",
            "behavior": "Prices tend to continue in the same direction for extended periods",
            "opportunity": "High opportunity for trend-following strategies",
            "risk": "Counter-trend trades are dangerous"
        },
        "TRENDING": {
            "description":  "Market shows moderate trending behavior",
            "behavior": "Prices have a tendency to trend but with regular pullbacks",
            "opportunity":  "Good for trend-following with proper entry timing",
            "risk": "Need to manage pullback risk"
        },
        "MEAN_REVERTING": {
            "description": "Market shows mean-reverting behavior",
            "behavior": "Prices tend to return to average after deviations",
            "opportunity":  "Good for range trading and reversal strategies",
            "risk":  "Breakouts can cause significant losses"
        },
        "RANDOM_WALK": {
            "description": "Market shows random/efficient behavior",
            "behavior": "Price movements are largely unpredictable",
            "opportunity": "Limited edge available",
            "risk": "High risk of false signals"
        }
    }
    
    base = interpretations.get(regime, interpretations["RANDOM_WALK"])
    
    return {
        **base,
        "metrics_summary": f"DFA={dfa:.3f}, Hurst={hurst:.3f}",
        "regime_name": regime
    }


# ═══════════════════════════════════════════════════════════════
# 📊 CONSOLE REPORT
# ═══════════════════════════════════════════════════════════════

def print_final_summary(analyzer, final_judgment, report_paths):
    """
    Print final summary to console (Light Display)
    Technical: Human-readable summary output
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║            ⚡🌟💎 ULTRA NECROZMA - ANALYSIS COMPLETE 💎🌟⚡                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Handle case where no results were found
    if final_judgment is None:
        print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠️  NO RESULTS FOUND                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   The analysis completed but no patterns were found.                         │
│   This may be due to insufficient data or invalid data format.               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
        """)
        if report_paths:
            print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📂 GENERATED REPORTS                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │""")
            from pathlib import Path
            for name, path in report_paths.items():
                filename = Path(path).name
                print(f"│   • {filename:<60}   │")
            print("│                                                                              │")
            print("└─────────────────────────────────────────────────────────────────────────────┘")
        return
    
    # Summary stats with safe get() calls
    summary = final_judgment.get("summary", {})
    regime = final_judgment.get("market_regime", {})
    recommendations = final_judgment.get("recommendations", {})
    best = final_judgment.get("best_configuration", {})
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 ANALYSIS SUMMARY                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   🌌 Universes Analyzed:      {summary.get('universes_analyzed', 0): <10}                                │
│   🎯 Total Patterns Found:   {summary.get('total_patterns', 0):<10,}                                │
│   ⚡ Evolution Stage:        {summary.get('evolution_stage', 'N/A'):<15}                           │
│   💎 Light Power:            {summary.get('light_power', 0):. 1f}%                                       │
│   🌈 Prismatic Cores:        {len(summary.get('prismatic_cores', []))}/7                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 📈 MARKET REGIME                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   🎯 Regime:          {regime.get('regime', 'UNKNOWN'):<20}                              │
│   🌊 DFA Alpha:       {regime.get('dfa_alpha', 0.5):.3f}                                              │
│   🌀 Hurst:            {regime.get('hurst_exponent', 0.5):.3f}                                              │
│   ⚡ Chaos Level:     {regime.get('chaos_level', 'UNKNOWN'): <15}                                   │
│   📐 Complexity:      {regime.get('complexity', 'UNKNOWN'):<15}                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 💡 RECOMMENDATIONS                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   🎯 Strategy:        {recommendations.get('primary_strategy', 'N/A'):<30}         │
│   📊 Confidence:      {recommendations.get('confidence', 'N/A'):<15}                              │
│   ⚠️  Risk Level:      {recommendations.get('risk_level', 'N/A'):<15}                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    """)
    
    if best:
        print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💎 OPTIMAL CONFIGURATION                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   🏆 Universe:        {best. get('name', 'N/A'):<30}                    │
│   ⏱️  Interval:        {best.get('interval', 'N/A')} minutes                                          │
│   🔮 Lookback:        {best.get('lookback', 'N/A')} periods                                          │
│   📊 Score:           {best.get('score', 0):.1f}                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
        """)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📂 GENERATED REPORTS                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │""")
    
    from pathlib import Path
    for name, path in report_paths.items():
        filename = Path(path).name
        print(f"│   • {filename:<60}   │")
    
    print("│                                                                              │")
    print("└─────────────────────────────────────────────────────────────────────────────┘")


