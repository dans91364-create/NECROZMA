#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for Round 4 fixes - MeanReverterV3 parameter generation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import StrategyFactory
from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS


def test_meanreverter_v3_combinations():
    """Test that MeanReverterV3 generates all 216 expected combinations"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverterV3 Parameter Combinations")
    print("=" * 70)
    
    # Create factory with only MeanReverterV3
    factory = StrategyFactory(
        templates=['MeanReverterV3'],
        params=STRATEGY_PARAMS
    )
    
    # Generate combinations
    combinations = factory.generate_parameter_combinations('MeanReverterV3')
    
    print(f"\n📊 Results:")
    print(f"   Generated combinations: {len(combinations)}")
    print(f"   Expected combinations: 216")
    
    # Expected: 3 × 2 × 3 × 3 × 2 × 2 = 216
    # threshold_std: [1.8, 2.0, 2.2] = 3
    # adaptive_threshold: [True, False] = 2
    # stop_loss_pips: [25, 30, 35] = 3
    # take_profit_pips: [45, 50, 55] = 3
    # require_confirmation: [True, False] = 2
    # use_session_filter: [True, False] = 2
    
    if len(combinations) == 216:
        print(f"   ✅ PASSED: Correct number of combinations generated!")
        
        # Verify that V3-specific parameters are present
        sample = combinations[0]
        has_v3_params = all(
            param in sample for param in 
            ['threshold_std', 'adaptive_threshold', 'require_confirmation', 'use_session_filter']
        )
        
        if has_v3_params:
            print(f"   ✅ All V3-specific parameters present in combinations")
            return True
        else:
            print(f"   ❌ Missing V3-specific parameters in combinations")
            print(f"      Sample params: {list(sample.keys())}")
            return False
    else:
        print(f"   ❌ FAILED: Expected 216 combinations, got {len(combinations)}")
        if len(combinations) > 0:
            print(f"      Sample combination keys: {list(combinations[0].keys())}")
        return False


def test_meanreverter_v3_strategies():
    """Test that MeanReverterV3 generates 216 unique strategies"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverterV3 Strategy Generation")
    print("=" * 70)
    
    # Create factory with only MeanReverterV3
    factory = StrategyFactory(
        templates=['MeanReverterV3'],
        params=STRATEGY_PARAMS
    )
    
    # Generate strategies
    strategies = factory.generate_strategies()
    
    # Count V3 strategies
    v3_strategies = [s for s in strategies if "MeanReverterV3" in s.name]
    
    print(f"\n📊 Results:")
    print(f"   Generated V3 strategies: {len(v3_strategies)}")
    print(f"   Expected strategies: 216")
    
    if len(v3_strategies) == 216:
        print(f"   ✅ PASSED: Correct number of strategies generated!")
        
        # Verify strategy names include V3 parameters
        sample_name = v3_strategies[0].name
        has_v3_params_in_name = all(
            param in sample_name for param in ['_AT', '_RC', '_SF']
        )
        
        if has_v3_params_in_name:
            print(f"   ✅ Strategy names include V3 parameters")
            print(f"      Sample name: {sample_name}")
            return True
        else:
            print(f"   ❌ Strategy names missing V3 parameters")
            print(f"      Sample name: {sample_name}")
            return False
    else:
        print(f"   ❌ FAILED: Expected 216 strategies, got {len(v3_strategies)}")
        if len(v3_strategies) > 0:
            print(f"      Sample strategy name: {v3_strategies[0].name}")
        return False


def test_momentum_burst_combinations():
    """Test that MomentumBurst uses Round 5 optimized parameters"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MomentumBurst Config (Round 5 Optimization)")
    print("=" * 70)
    
    # Check config
    mb_config = STRATEGY_PARAMS.get('MomentumBurst', {})
    
    print(f"\n📊 Results:")
    print(f"   lookback_periods: {mb_config.get('lookback_periods', [])}")
    print(f"   threshold_std: {mb_config.get('threshold_std', [])}")
    print(f"   stop_loss_pips: {mb_config.get('stop_loss_pips', [])}")
    print(f"   take_profit_pips: {mb_config.get('take_profit_pips', [])}")
    print(f"   cooldown_minutes: {mb_config.get('cooldown_minutes', [])}")
    
    # Verify Round 5 optimizations
    checks = [
        (5 not in mb_config.get('lookback_periods', []), "L5 removed (too noisy)"),
        (0.5 not in mb_config.get('threshold_std', []), "threshold 0.5 removed"),
        (0.8 not in mb_config.get('threshold_std', []), "threshold 0.8 removed"),
        (1.2 not in mb_config.get('threshold_std', []), "threshold 1.2 removed"),
        (10 not in mb_config.get('stop_loss_pips', []), "SL10 removed (too tight)"),
        (20 not in mb_config.get('take_profit_pips', []), "TP20 removed (too small)"),
        (60 not in mb_config.get('cooldown_minutes', []), "CD60 removed"),
        (90 not in mb_config.get('cooldown_minutes', []), "CD90 removed"),
    ]
    
    all_passed = True
    for check, desc in checks:
        if check:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc}")
            all_passed = False
    
    # Expected: 2 × 2 × 2 × 2 × 2 = 32
    factory = StrategyFactory(
        templates=['MomentumBurst'],
        params=STRATEGY_PARAMS
    )
    combinations = factory.generate_parameter_combinations('MomentumBurst')
    
    print(f"\n   Generated combinations: {len(combinations)}")
    print(f"   Expected combinations: 32")
    
    if len(combinations) == 32:
        print(f"   ✅ Correct number of combinations (Round 5 optimized)")
        return all_passed
    else:
        print(f"   ❌ Expected 32 combinations, got {len(combinations)}")
        return False


def run_all_tests():
    """Run all Round 4 fix tests"""
    print("\n" + "=" * 70)
    print("🧪 ROUND 4 FIXES VALIDATION TESTS")
    print("=" * 70)
    
    results = {
        "MeanReverterV3 Combinations": test_meanreverter_v3_combinations(),
        "MeanReverterV3 Strategies": test_meanreverter_v3_strategies(),
        "MomentumBurst CD30 Removed": test_momentum_burst_combinations(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ ALL {total} TESTS PASSED!")
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
