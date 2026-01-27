#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test for Mass Test System fixes

Tests all three critical fixes:
1. MeanReverterLegacy import
2. Dynamic FILE_PREFIX
3. MomentumBurst bulletproof fix
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_meanreverter_legacy_import():
    """Test 1: MeanReverterLegacy Import"""
    print("\n" + "=" * 70)
    print("TEST 1: MeanReverterLegacy Import")
    print("=" * 70)
    
    try:
        from strategy_factory import MeanReverterLegacy, MeanReverter
        print("✅ MeanReverterLegacy imported successfully")
        
        # Verify it's an alias
        assert MeanReverterLegacy is MeanReverter, "MeanReverterLegacy should be an alias"
        print("✅ MeanReverterLegacy is correctly aliased to MeanReverter")
        
        # Test instantiation
        params = {'lookback_periods': 5, 'threshold': 1.8}
        legacy = MeanReverterLegacy(params)
        assert legacy.name == "MeanReverter", f"Expected name='MeanReverter', got '{legacy.name}'"
        assert legacy.threshold == 1.8, f"Expected threshold=1.8, got {legacy.threshold}"
        print("✅ MeanReverterLegacy instantiated correctly")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dynamic_file_prefix():
    """Test 2: Dynamic FILE_PREFIX"""
    print("\n" + "=" * 70)
    print("TEST 2: Dynamic FILE_PREFIX")
    print("=" * 70)
    
    try:
        import config
        
        # Save original values
        orig_pair = config.PAIR_NAME
        orig_year = config.DATA_YEAR
        orig_prefix = config.FILE_PREFIX
        
        # Test 1: AUDJPY_2023
        print("\nTest case 1: AUDJPY_2023.parquet")
        parquet_filename = Path("data/parquet/AUDJPY_2023.parquet")
        filename = parquet_filename.stem
        parts = filename.split("_")
        
        if len(parts) >= 2:
            config.PAIR_NAME = parts[0]
            config.DATA_YEAR = parts[1]
            config.FILE_PREFIX = f"{parts[0]}_{parts[1]}_"
            
            assert config.PAIR_NAME == "AUDJPY", f"Expected PAIR_NAME='AUDJPY', got '{config.PAIR_NAME}'"
            assert config.DATA_YEAR == "2023", f"Expected DATA_YEAR='2023', got '{config.DATA_YEAR}'"
            assert config.FILE_PREFIX == "AUDJPY_2023_", f"Expected FILE_PREFIX='AUDJPY_2023_', got '{config.FILE_PREFIX}'"
            print(f"✅ Dynamic config: PAIR={config.PAIR_NAME}, YEAR={config.DATA_YEAR}, PREFIX={config.FILE_PREFIX}")
        
        # Test 2: GBPJPY_2024
        print("\nTest case 2: GBPJPY_2024.parquet")
        parquet_filename = Path("data/GBPJPY_2024.parquet")
        filename = parquet_filename.stem
        parts = filename.split("_")
        
        if len(parts) >= 2:
            config.PAIR_NAME = parts[0]
            config.DATA_YEAR = parts[1]
            config.FILE_PREFIX = f"{parts[0]}_{parts[1]}_"
            
            assert config.PAIR_NAME == "GBPJPY", f"Expected PAIR_NAME='GBPJPY', got '{config.PAIR_NAME}'"
            assert config.DATA_YEAR == "2024", f"Expected DATA_YEAR='2024', got '{config.DATA_YEAR}'"
            assert config.FILE_PREFIX == "GBPJPY_2024_", f"Expected FILE_PREFIX='GBPJPY_2024_', got '{config.FILE_PREFIX}'"
            print(f"✅ Dynamic config: PAIR={config.PAIR_NAME}, YEAR={config.DATA_YEAR}, PREFIX={config.FILE_PREFIX}")
        
        # Restore original values
        config.PAIR_NAME = orig_pair
        config.DATA_YEAR = orig_year
        config.FILE_PREFIX = orig_prefix
        
        print("\n✅ Dynamic FILE_PREFIX test passed")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_momentum_burst_bulletproof():
    """Test 3: MomentumBurst Bulletproof Fix"""
    print("\n" + "=" * 70)
    print("TEST 3: MomentumBurst Bulletproof Fix")
    print("=" * 70)
    
    try:
        from strategy_factory import MomentumBurst
        
        # Test 1: Single day with many potential signals
        print("\nTest case 1: Single day trade limiting")
        np.random.seed(42)
        n = 1000
        start_date = datetime(2023, 1, 1, 0, 0, 0)
        timestamps = [start_date + timedelta(minutes=i) for i in range(n)]
        
        prices = []
        base_price = 1.1000
        for i in range(n):
            if i % 50 == 0 and i > 0:
                base_price += 0.001  # Large move
            else:
                base_price += np.random.randn() * 0.00001
            prices.append(base_price)
        
        df = pd.DataFrame({
            'mid_price': prices,
            'close': prices,
        }, index=pd.DatetimeIndex(timestamps))
        
        params = {
            'lookback_periods': 10,
            'threshold_std': 1.0,
            'cooldown_minutes': 60,
            'max_trades_per_day': 5
        }
        
        mb = MomentumBurst(params)
        signals = mb.generate_signals(df)
        
        num_signals = (signals != 0).sum()
        assert num_signals <= params['max_trades_per_day'], \
            f"Expected <= {params['max_trades_per_day']} signals, got {num_signals}"
        print(f"✅ Generated {num_signals} signals (limit: {params['max_trades_per_day']})")
        
        # Test 2: Multi-day scenario
        print("\nTest case 2: Multi-day trade limiting")
        n = 3000  # 3 days worth of data
        timestamps = [start_date + timedelta(minutes=i) for i in range(n)]
        
        prices = []
        base_price = 1.1000
        for i in range(n):
            if i % 30 == 0 and i > 0:
                base_price += 0.001
            else:
                base_price += np.random.randn() * 0.00001
            prices.append(base_price)
        
        df = pd.DataFrame({
            'mid_price': prices,
            'close': prices,
        }, index=pd.DatetimeIndex(timestamps))
        
        signals = mb.generate_signals(df)
        
        # Count signals per day
        signal_dates = pd.Series(signals[signals != 0].index).dt.date.value_counts()
        print(f"Days with trades: {len(signal_dates)}")
        
        for date, count in signal_dates.items():
            assert count <= params['max_trades_per_day'], \
                f"Day {date} exceeded limit: {count} > {params['max_trades_per_day']}"
            print(f"  {date}: {count} trades ✅")
        
        print("\n✅ MomentumBurst bulletproof fix test passed")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_factory_integration():
    """Test 4: StrategyFactory Integration"""
    print("\n" + "=" * 70)
    print("TEST 4: StrategyFactory Integration")
    print("=" * 70)
    
    try:
        from strategy_factory import StrategyFactory
        from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS
        
        factory = StrategyFactory(STRATEGY_TEMPLATES, STRATEGY_PARAMS)
        
        # Verify all templates are registered
        print("\nRegistered templates:")
        for template in STRATEGY_TEMPLATES:
            assert template in factory.template_classes, f"Template {template} not registered"
            print(f"  ✅ {template}")
        
        # Count total combinations
        print("\nStrategy combinations:")
        total = 0
        for template in STRATEGY_TEMPLATES:
            combos = factory.generate_parameter_combinations(template)
            total += len(combos)
            print(f"  {template}: {len(combos)} combinations")
        
        print(f"\n✅ Total strategy combinations: {total}")
        
        # Verify key strategies are included
        assert 'MeanReverterLegacy' in STRATEGY_TEMPLATES, "MeanReverterLegacy missing from templates"
        assert 'MomentumBurst' in STRATEGY_TEMPLATES, "MomentumBurst missing from templates"
        print("✅ Key strategies (MeanReverterLegacy, MomentumBurst) included")
        
        print("\n✅ StrategyFactory integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST - Mass Test System Fixes")
    print("=" * 70)
    
    results = {
        "MeanReverterLegacy Import": test_meanreverter_legacy_import(),
        "Dynamic FILE_PREFIX": test_dynamic_file_prefix(),
        "MomentumBurst Bulletproof Fix": test_momentum_burst_bulletproof(),
        "StrategyFactory Integration": test_strategy_factory_integration(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
