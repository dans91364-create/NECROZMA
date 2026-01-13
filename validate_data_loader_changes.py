#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation script to verify data_loader changes are backward compatible
"""

import json
import tempfile
from pathlib import Path
import sys

# Mock streamlit module
class MockStreamlit:
    @staticmethod
    def cache_data(func):
        return func
    
    @staticmethod
    def error(msg):
        pass
    
    @staticmethod
    def warning(msg):
        pass

sys.modules['streamlit'] = MockStreamlit()

# Import after mocking
sys.path.insert(0, 'dashboard/utils')
from data_loader import load_all_results


def test_backward_compatibility():
    """Test that the new data_loader is backward compatible"""
    
    print("\n🧪 Testing backward compatibility...\n")
    
    # Create temp directory with mock data
    with tempfile.TemporaryDirectory() as tmp_dir:
        backtest_dir = Path(tmp_dir) / "backtest_results"
        backtest_dir.mkdir(parents=True, exist_ok=True)
        
        # Create consolidated file (old structure without trades_detailed)
        consolidated = {
            "backtest_timestamp": "2025-01-13T12:00:00",
            "total_universes": 1,
            "universes": [
                {
                    "universe_name": "universe_001_5min_5lb",
                    "universe_metadata": {
                        "interval": "5min",
                        "lookback": 5
                    },
                    "results": [
                        {
                            "strategy_name": "TestStrategy",
                            "n_trades": 100,
                            "win_rate": 0.60,
                            "total_return": 0.15,
                            "sharpe_ratio": 1.5
                        }
                    ]
                }
            ]
        }
        
        consolidated_file = backtest_dir / "consolidated_backtest_results.json"
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        # Load data using new loader
        data = load_all_results(str(backtest_dir))
        
        # Verify backward compatibility - old fields should still exist
        print("✅ Checking backward compatible fields...")
        assert 'strategies' in data, "Missing 'strategies' field (backward compatibility)"
        assert 'strategies_df' in data, "Missing 'strategies_df' field (backward compatibility)"
        assert 'total_strategies' in data, "Missing 'total_strategies' field (backward compatibility)"
        assert 'viable_count' in data, "Missing 'viable_count' field (backward compatibility)"
        
        # Verify new fields exist
        print("✅ Checking new fields...")
        assert 'all_results' in data, "Missing 'all_results' field (new)"
        assert 'metadata' in data, "Missing 'metadata' field (new)"
        assert 'has_detailed_trades' in data, "Missing 'has_detailed_trades' field (new)"
        
        # Verify data is correct
        print("✅ Checking data integrity...")
        assert data['total_strategies'] == 1, f"Expected 1 strategy, got {data['total_strategies']}"
        assert data['has_detailed_trades'] == False, "Should not have detailed trades with only consolidated file"
        assert len(data['all_results']) == 1, f"Expected 1 result, got {len(data['all_results'])}"
        
        # Verify strategy data
        strategy = data['all_results'][0]
        assert strategy['strategy_name'] == "TestStrategy"
        assert strategy['n_trades'] == 100
        assert strategy.get('trades_detailed', []) == [], "Should have empty trades_detailed"
        
        print("\n✅ All backward compatibility tests passed!")
        return True


def test_empty_directory():
    """Test handling of non-existent directory"""
    
    print("\n🧪 Testing empty directory handling...\n")
    
    data = load_all_results("/nonexistent/directory")
    
    assert data['total_strategies'] == 0
    assert data['has_detailed_trades'] == False
    assert len(data['all_results']) == 0
    
    print("✅ Empty directory handling test passed!")
    return True


if __name__ == '__main__':
    try:
        print("="*60)
        print("🔍 VALIDATION TESTS")
        print("="*60)
        
        test_backward_compatibility()
        test_empty_directory()
        
        print("\n" + "="*60)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("="*60 + "\n")
        
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
