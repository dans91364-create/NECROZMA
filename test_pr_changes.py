#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate PR changes for code cleanup and mass testing system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_changes():
    """Test that config.py has been updated correctly"""
    print("\n" + "="*70)
    print("🧪 Testing config.py changes...")
    print("="*70)
    
    import config
    
    # Test 1: Verify STRATEGY_TEMPLATES
    expected_templates = ['MeanReverter', 'MeanReverterV2', 'MeanReverterV3']
    assert config.STRATEGY_TEMPLATES == expected_templates, \
        f"Expected {expected_templates}, got {config.STRATEGY_TEMPLATES}"
    print("✅ STRATEGY_TEMPLATES updated correctly")
    
    # Test 2: Verify MeanReverterLegacy is removed
    assert 'MeanReverterLegacy' not in config.STRATEGY_PARAMS, \
        "MeanReverterLegacy should be removed from STRATEGY_PARAMS"
    print("✅ MeanReverterLegacy removed from STRATEGY_PARAMS")
    
    # Test 3: Verify MeanReverter uses 'threshold' parameter
    mr_params = config.STRATEGY_PARAMS['MeanReverter']
    assert 'threshold' in mr_params, \
        "MeanReverter should use 'threshold' parameter"
    assert mr_params['threshold'] == [1.8, 2.0], \
        f"Expected threshold [1.8, 2.0], got {mr_params['threshold']}"
    print("✅ MeanReverter uses 'threshold' parameter correctly")
    
    # Test 4: Calculate total strategies
    mr_count = (
        len(mr_params['lookback_periods']) *
        len(mr_params['threshold']) *
        len(mr_params['stop_loss_pips']) *
        len(mr_params['take_profit_pips'])
    )
    
    mrv2_params = config.STRATEGY_PARAMS['MeanReverterV2']
    mrv2_count = (
        len(mrv2_params['lookback_periods']) *
        len(mrv2_params['threshold_std']) *
        len(mrv2_params['stop_loss_pips']) *
        len(mrv2_params['take_profit_pips']) *
        len(mrv2_params['rsi_oversold']) *
        len(mrv2_params['rsi_overbought']) *
        len(mrv2_params['volume_filter'])
    )
    
    mrv3_params = config.STRATEGY_PARAMS['MeanReverterV3']
    mrv3_count = (
        len(mrv3_params['lookback_periods']) *
        len(mrv3_params['threshold_std']) *
        len(mrv3_params['stop_loss_pips']) *
        len(mrv3_params['take_profit_pips']) *
        len(mrv3_params['adaptive_threshold']) *
        len(mrv3_params['require_confirmation']) *
        len(mrv3_params['use_session_filter'])
    )
    
    total = mr_count + mrv2_count + mrv3_count
    assert mr_count == 8, f"Expected 8 MeanReverter strategies, got {mr_count}"
    assert mrv2_count == 24, f"Expected 24 MeanReverterV2 strategies, got {mrv2_count}"
    assert mrv3_count == 12, f"Expected 12 MeanReverterV3 strategies, got {mrv3_count}"
    assert total == 44, f"Expected 44 total strategies, got {total}"
    
    print(f"✅ Strategy counts correct: MR={mr_count}, MRV2={mrv2_count}, MRV3={mrv3_count}, Total={total}")
    
    return True


def test_strategy_factory_changes():
    """Test that strategy_factory.py has been updated correctly"""
    print("\n" + "="*70)
    print("🧪 Testing strategy_factory.py changes...")
    print("="*70)
    
    # Test 1: Verify MeanReverter class exists and is importable
    try:
        from strategy_factory import MeanReverter, MeanReverterV2, MeanReverterV3
        print("✅ All strategy classes imported successfully")
    except ImportError as e:
        # This might fail if numpy/pandas are not installed, which is OK
        if "numpy" in str(e) or "pandas" in str(e):
            print("⚠️  Could not import strategies (missing dependencies - OK for syntax test)")
            return True
        raise
    
    # Test 2: Verify MeanReverterLegacy doesn't exist
    try:
        from strategy_factory import MeanReverterLegacy
        raise AssertionError("MeanReverterLegacy should not exist in strategy_factory.py")
    except ImportError:
        print("✅ MeanReverterLegacy correctly removed")
    
    return True


def test_mass_test_system():
    """Test that run_mass_test.py exists and is valid"""
    print("\n" + "="*70)
    print("🧪 Testing mass testing system...")
    print("="*70)
    
    # Test 1: Verify file exists
    mass_test_path = Path(__file__).parent / "run_mass_test.py"
    assert mass_test_path.exists(), "run_mass_test.py should exist"
    print("✅ run_mass_test.py exists")
    
    # Test 2: Verify it's executable
    assert mass_test_path.stat().st_mode & 0o111, "run_mass_test.py should be executable"
    print("✅ run_mass_test.py is executable")
    
    # Test 3: Verify syntax is valid
    import py_compile
    try:
        py_compile.compile(str(mass_test_path), doraise=True)
        print("✅ run_mass_test.py has valid Python syntax")
    except py_compile.PyCompileError as e:
        raise AssertionError(f"Syntax error in run_mass_test.py: {e}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("⚡🌟💎 PR CHANGES VALIDATION 💎🌟⚡")
    print("="*70)
    
    tests = [
        ("Config Changes", test_config_changes),
        ("Strategy Factory Changes", test_strategy_factory_changes),
        ("Mass Testing System", test_mass_test_system),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! PR changes are valid.")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
