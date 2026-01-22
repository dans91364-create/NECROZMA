#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for analyze_by_frequency.py
"""

import os
import json
from pathlib import Path
import pandas as pd


def test_frequency_analysis():
    """Test that frequency analysis generates expected outputs."""
    
    print("Testing frequency analysis script...")
    
    # Check if output files exist
    json_path = Path("screening_results/frequency_analysis.json")
    txt_path = Path("screening_results/frequency_analysis.txt")
    
    assert json_path.exists(), "JSON output file not found"
    assert txt_path.exists(), "TXT output file not found"
    
    print("✓ Output files exist")
    
    # Load and validate JSON structure
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Check main sections
    assert 'general_summary' in data, "Missing general_summary section"
    assert 'band_analyses' in data, "Missing band_analyses section"
    assert 'comparison' in data, "Missing comparison section"
    assert 'final_candidates' in data, "Missing final_candidates section"
    
    print("✓ JSON structure is valid")
    
    # Check general summary
    gs = data['general_summary']
    assert 'total_strategies' in gs, "Missing total_strategies"
    assert 'discarded_count' in gs, "Missing discarded_count"
    assert 'band_counts' in gs, "Missing band_counts"
    assert 'band_percentages' in gs, "Missing band_percentages"
    
    print(f"✓ Total strategies: {gs['total_strategies']}")
    print(f"✓ Discarded: {gs['discarded_count']}")
    
    # Check band counts
    bc = gs['band_counts']
    assert 'FAIXA_1_LOW' in bc, "Missing FAIXA_1_LOW count"
    assert 'FAIXA_2_MEDIUM' in bc, "Missing FAIXA_2_MEDIUM count"
    assert 'FAIXA_3_HIGH' in bc, "Missing FAIXA_3_HIGH count"
    assert 'IMPRACTICAL' in bc, "Missing IMPRACTICAL count"
    
    print(f"✓ FAIXA 1: {bc['FAIXA_1_LOW']}")
    print(f"✓ FAIXA 2: {bc['FAIXA_2_MEDIUM']}")
    print(f"✓ FAIXA 3: {bc['FAIXA_3_HIGH']}")
    print(f"✓ IMPRACTICAL: {bc['IMPRACTICAL']}")
    
    # Check band analyses
    ba = data['band_analyses']
    valid_bands = ['FAIXA_1_LOW', 'FAIXA_2_MEDIUM', 'FAIXA_3_HIGH']
    
    for band in valid_bands:
        if band in ba and ba[band]:
            assert 'count' in ba[band], f"Missing count for {band}"
            assert 'top_10_sharpe' in ba[band], f"Missing top_10_sharpe for {band}"
            assert 'top_10_profit_factor' in ba[band], f"Missing top_10_profit_factor for {band}"
            assert 'top_10_win_rate' in ba[band], f"Missing top_10_win_rate for {band}"
            assert 'aggregate_stats' in ba[band], f"Missing aggregate_stats for {band}"
            
            # Check top lists have items
            assert len(ba[band]['top_10_sharpe']) > 0, f"Empty top_10_sharpe for {band}"
            
            # Check aggregate stats structure
            stats = ba[band]['aggregate_stats']
            for metric in ['sharpe_ratio', 'profit_factor', 'win_rate', 'n_trades']:
                assert metric in stats, f"Missing {metric} in aggregate_stats for {band}"
                assert 'mean' in stats[metric], f"Missing mean for {metric} in {band}"
                assert 'median' in stats[metric], f"Missing median for {metric} in {band}"
                assert 'max' in stats[metric], f"Missing max for {metric} in {band}"
    
    print("✓ Band analyses are valid")
    
    # Check comparison
    comp = data['comparison']
    assert 'metric_comparison' in comp, "Missing metric_comparison"
    assert 'best_bands' in comp, "Missing best_bands"
    
    print("✓ Comparison section is valid")
    
    # Check final candidates
    fc = data['final_candidates']
    total_candidates = 0
    for band in valid_bands:
        if band in fc and fc[band]:
            total_candidates += len(fc[band])
            # Each candidate should have required fields
            for candidate in fc[band]:
                assert 'strategy_name' in candidate, f"Missing strategy_name in {band} candidate"
                assert 'sharpe_ratio' in candidate, f"Missing sharpe_ratio in {band} candidate"
                assert 'profit_factor' in candidate, f"Missing profit_factor in {band} candidate"
                assert 'win_rate' in candidate, f"Missing win_rate in {band} candidate"
                assert 'n_trades' in candidate, f"Missing n_trades in {band} candidate"
    
    print(f"✓ Final candidates: {total_candidates} strategies")
    
    # Check text file content
    with open(txt_path, 'r') as f:
        txt_content = f.read()
    
    # Verify key sections exist in text report
    assert "FREQUENCY BANDS DEFINITION" in txt_content, "Missing frequency bands section"
    assert "GENERAL SUMMARY" in txt_content, "Missing general summary section"
    assert "FAIXA 1 - LOW FREQUENCY" in txt_content, "Missing FAIXA 1 section"
    assert "FAIXA 2 - MEDIUM FREQUENCY" in txt_content, "Missing FAIXA 2 section"
    assert "FAIXA 3 - HIGH FREQUENCY" in txt_content, "Missing FAIXA 3 section"
    assert "IMPRACTICAL BAND" in txt_content, "Missing impractical band section"
    assert "DISCARDED STRATEGIES" in txt_content, "Missing discarded section"
    assert "COMPARISON BETWEEN BANDS" in txt_content, "Missing comparison section"
    assert "FINAL CANDIDATE STRATEGIES" in txt_content, "Missing final candidates section"
    
    print("✓ Text report contains all required sections")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_frequency_analysis()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
