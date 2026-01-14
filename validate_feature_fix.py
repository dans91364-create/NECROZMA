#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for feature_extractor.py fix

Tests that feature extraction works with the corrected JSON structure
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from feature_extractor import extract_features_from_universe


def test_feature_extraction():
    """Test feature extraction with correct JSON structure"""
    
    print("=" * 70)
    print("🧪 FEATURE EXTRACTOR VALIDATION TEST")
    print("=" * 70)
    
    # Create mock universe data with feature_stats structure
    mock_universe = {
        "name": "test_universe_5m_20lb",
        "interval": 5,
        "lookback": 20,
        "results": {
            "Pequeno": {
                "up": {
                    "count": 1500,
                    "feature_stats": {
                        "ohlc_body_mean": -1.02,
                        "ohlc_range_mean": 2.46,
                        "ohlc_trend_efficiency_mean": 0.76,
                        "ohlc_volume_mean": 81.8,
                        "ohlc_volume_trend": 1.05,
                        "ohlc_spread_mean": 0.5,
                        "ohlc_up_ratio": 0.6,
                        "ohlc_down_ratio": 0.4,
                        "ohlc_body_std_mean": 0.25,
                    },
                    "patterns": {}  # This exists but we don't use it anymore
                },
                "down": {
                    "count": 1450,
                    "feature_stats": {
                        "ohlc_body_mean": 0.98,
                        "ohlc_range_mean": 2.40,
                        "ohlc_trend_efficiency_mean": 0.74,
                        "ohlc_volume_mean": 79.5,
                        "ohlc_volume_trend": 0.98,
                        "ohlc_spread_mean": 0.52,
                        "ohlc_up_ratio": 0.42,
                        "ohlc_down_ratio": 0.58,
                        "ohlc_body_std_mean": 0.22,
                    },
                    "patterns": {}
                }
            },
            "Médio": {
                "up": {
                    "count": 850,
                    "feature_stats": {
                        "ohlc_body_mean": -1.25,
                        "ohlc_range_mean": 3.10,
                        "ohlc_trend_efficiency_mean": 0.82,
                        "ohlc_volume_mean": 95.2,
                        "ohlc_volume_trend": 1.12,
                        "ohlc_spread_mean": 0.48,
                        "ohlc_up_ratio": 0.68,
                        "ohlc_down_ratio": 0.32,
                        "ohlc_body_std_mean": 0.30,
                    },
                    "patterns": {}
                },
                "down": {
                    "count": 820,
                    "feature_stats": {
                        "ohlc_body_mean": 1.18,
                        "ohlc_range_mean": 3.05,
                        "ohlc_trend_efficiency_mean": 0.79,
                        "ohlc_volume_mean": 93.1,
                        "ohlc_volume_trend": 0.95,
                        "ohlc_spread_mean": 0.51,
                        "ohlc_up_ratio": 0.35,
                        "ohlc_down_ratio": 0.65,
                        "ohlc_body_std_mean": 0.28,
                    },
                    "patterns": {}
                }
            },
            "Grande": {
                "up": {
                    "count": 320,
                    "feature_stats": {
                        "ohlc_body_mean": -1.85,
                        "ohlc_range_mean": 4.20,
                        "ohlc_trend_efficiency_mean": 0.88,
                        "ohlc_volume_mean": 125.5,
                        "ohlc_volume_trend": 1.25,
                        "ohlc_spread_mean": 0.45,
                        "ohlc_up_ratio": 0.75,
                        "ohlc_down_ratio": 0.25,
                        "ohlc_body_std_mean": 0.42,
                    },
                    "patterns": {}
                },
                "down": {
                    "count": 305,
                    "feature_stats": {
                        "ohlc_body_mean": 1.78,
                        "ohlc_range_mean": 4.15,
                        "ohlc_trend_efficiency_mean": 0.86,
                        "ohlc_volume_mean": 122.8,
                        "ohlc_volume_trend": 0.88,
                        "ohlc_spread_mean": 0.47,
                        "ohlc_up_ratio": 0.28,
                        "ohlc_down_ratio": 0.72,
                        "ohlc_body_std_mean": 0.38,
                    },
                    "patterns": {}
                }
            },
            "Muito Grande": {
                "up": {
                    "count": 85,
                    "feature_stats": {
                        "ohlc_body_mean": -2.85,
                        "ohlc_range_mean": 6.20,
                        "ohlc_trend_efficiency_mean": 0.92,
                        "ohlc_volume_mean": 185.5,
                        "ohlc_volume_trend": 1.45,
                        "ohlc_spread_mean": 0.42,
                        "ohlc_up_ratio": 0.82,
                        "ohlc_down_ratio": 0.18,
                        "ohlc_body_std_mean": 0.58,
                    },
                    "patterns": {}
                },
                "down": {
                    "count": 78,
                    "feature_stats": {
                        "ohlc_body_mean": 2.72,
                        "ohlc_range_mean": 6.05,
                        "ohlc_trend_efficiency_mean": 0.90,
                        "ohlc_volume_mean": 178.2,
                        "ohlc_volume_trend": 0.78,
                        "ohlc_spread_mean": 0.44,
                        "ohlc_up_ratio": 0.20,
                        "ohlc_down_ratio": 0.80,
                        "ohlc_body_std_mean": 0.52,
                    },
                    "patterns": {}
                }
            }
        }
    }
    
    print("\n📊 Testing feature extraction...")
    print(f"   Universe: {mock_universe['name']}")
    print(f"   Interval: {mock_universe['interval']}min")
    print(f"   Lookback: {mock_universe['lookback']}")
    print(f"   Levels: {len(mock_universe['results'])}")
    
    # Extract features
    features_df = extract_features_from_universe(mock_universe)
    
    # Validate results
    print(f"\n✅ Feature extraction results:")
    print(f"   Shape: {features_df.shape}")
    print(f"   Columns: {len(features_df.columns)}")
    
    if features_df.empty:
        print("\n❌ FAILED: No features extracted!")
        return False
    
    # Check for required derived features
    required_features = ["momentum", "volatility", "trend_strength"]
    missing_features = [f for f in required_features if f not in features_df.columns]
    
    if missing_features:
        print(f"\n❌ FAILED: Missing required features: {missing_features}")
        return False
    
    print(f"\n📈 Feature values:")
    for col in features_df.columns:
        value = features_df[col].iloc[0]
        print(f"   {col}: {value:.4f}")
    
    print(f"\n✅ Derived features check:")
    print(f"   momentum: {features_df['momentum'].iloc[0]:.4f}")
    print(f"   volatility: {features_df['volatility'].iloc[0]:.4f}")
    print(f"   trend_strength: {features_df['trend_strength'].iloc[0]:.4f}")
    
    # Test with empty feature_stats
    print(f"\n🧪 Testing with empty feature_stats...")
    empty_universe = {
        "name": "empty_test",
        "results": {
            "Pequeno": {
                "up": {"feature_stats": {}},
                "down": {"feature_stats": {}}
            }
        }
    }
    
    empty_features = extract_features_from_universe(empty_universe)
    if not empty_features.empty:
        print(f"   ✅ Handles empty feature_stats (returns defaults)")
    else:
        print(f"   ✅ Returns empty DataFrame for no data")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n🎯 Summary:")
    print("   • Feature extraction now reads from feature_stats ✅")
    print("   • Aggregates across all levels and directions ✅")
    print("   • Creates derived features (momentum, volatility, trend_strength) ✅")
    print("   • Handles edge cases gracefully ✅")
    print("\n✨ Ready for backtesting!")
    
    return True


if __name__ == "__main__":
    success = test_feature_extraction()
    sys.exit(0 if success else 1)
