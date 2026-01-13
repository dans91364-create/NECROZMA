"""Test SL/TP extraction from strategy names"""
import sys
sys.path.insert(0, 'dashboard/utils')
from data_loader import extract_sl_tp_from_name

def test_sl_tp_extraction():
    """Test various strategy name formats"""
    
    test_cases = [
        # (strategy_name, expected_sl, expected_tp)
        ('TrendFollower_L5_T0.5_SL10_TP50', 10, 50),
        ('TrendFollower_L5_T0.5_SL15_TP30', 15, 30),
        ('TrendFollower_L5_T0.5_SL10_TP40', 10, 40),
        ('TrendFollower_L5_T0.5_SL20_TP50', 20, 50),
        ('MeanReversion_SL10_TP20', 10, 20),
        ('strategy_sl_20_tp_40', 20, 40),
        ('momentum_sl_15_tp_30', 15, 30),
        ('BreakoutStrategy_sl10tp50', 10, 50),
        ('SL5_TP25_Strategy', 5, 25),
        # Negative tests
        ('NoSLTP_Strategy', None, None),
        ('OnlySL10_NoTP', None, None),
        ('', None, None),
        (None, None, None),
    ]
    
    print("🧪 Testing SL/TP extraction...\n")
    
    passed = 0
    failed = 0
    
    for strategy_name, expected_sl, expected_tp in test_cases:
        sl, tp = extract_sl_tp_from_name(strategy_name)
        
        if sl == expected_sl and tp == expected_tp:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} | '{strategy_name}'")
        print(f"         Expected: SL={expected_sl}, TP={expected_tp}")
        print(f"         Got:      SL={sl}, TP={tp}")
        print()
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    test_sl_tp_extraction()
