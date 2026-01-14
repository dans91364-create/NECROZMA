#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-end test: Analyzer → Backtest workflow
"""

import sys
import tempfile
import shutil
import json
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from analyzer import UltraNecrozmaAnalyzer
from feature_extractor import extract_features_from_universe, combine_ohlc_with_features


def generate_sample_data(n_ticks=5000):
    """Generate sample tick data"""
    np.random.seed(42)
    
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    base_price = 1.10
    noise = np.random.randn(n_ticks) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
        'mid_price': base_price + cumsum,
        'spread_pips': 1.0,
        'pips_change': np.concatenate([[0], np.diff(cumsum) * 10000])
    })
    
    return df


def test_end_to_end():
    """Test complete workflow: analyze → save → load → backtest prep"""
    print("\n" + "="*70)
    print("END-TO-END TEST: Analyzer → Backtest Workflow")
    print("="*70)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Step 1: Generate data
        print("\n📊 Step 1: Generating sample data...")
        df = generate_sample_data()
        print(f"   ✅ Generated {len(df):,} ticks")
        
        # Step 2: Run analyzer
        print("\n⚡ Step 2: Running analyzer...")
        analyzer = UltraNecrozmaAnalyzer(df, output_dir=temp_dir)
        analyzer.configs = analyzer.configs[:2]  # Test with 2 universes
        analyzer._run_sequential()
        print(f"   ✅ Processed {analyzer.universes_processed} universes")
        print(f"   ✅ Found {analyzer.total_patterns:,} total patterns")
        
        # Step 3: Save results
        print("\n💾 Step 3: Saving universe files...")
        save_stats = analyzer.save_results()
        print(f"   ✅ Saved {save_stats['universes_saved']} universe files")
        
        # Step 4: Load and verify
        print("\n📂 Step 4: Loading saved universe files...")
        universes_dir = temp_dir / "universes"
        universe_files = list(universes_dir.glob("universe_*.json"))
        print(f"   ✅ Found {len(universe_files)} universe files")
        
        for filepath in universe_files:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"      - {filepath.name} ({size_mb:.2f} MB)")
        
        # Step 5: Verify file structure for backtesting
        print("\n🔍 Step 5: Verifying backtest compatibility...")
        
        success_count = 0
        for filepath in universe_files:
            with open(filepath, 'r') as f:
                universe_data = json.load(f)
            
            # Check required fields
            required = ["name", "interval", "lookback", "ohlc_data", "results"]
            missing = [f for f in required if f not in universe_data]
            
            if missing:
                print(f"   ❌ {filepath.name}: Missing fields: {missing}")
                continue
            
            # Check OHLC data
            if len(universe_data["ohlc_data"]) == 0:
                print(f"   ❌ {filepath.name}: Empty ohlc_data")
                continue
            
            # Test feature extraction
            try:
                features_df = extract_features_from_universe(universe_data)
                
                # Create mock OHLC for combination test
                ohlc_df = pd.DataFrame(universe_data["ohlc_data"])
                if not ohlc_df.empty:
                    combined_df = combine_ohlc_with_features(ohlc_df, features_df)
                    
                    print(f"   ✅ {filepath.name}:")
                    print(f"      OHLC candles: {len(universe_data['ohlc_data'])}")
                    print(f"      Patterns: {universe_data['total_patterns']}")
                    print(f"      Features extracted: {len(features_df.columns) if not features_df.empty else 0}")
                    print(f"      Combined shape: {combined_df.shape}")
                    
                    success_count += 1
                else:
                    print(f"   ⚠️  {filepath.name}: Could not create OHLC DataFrame")
                    
            except Exception as e:
                print(f"   ❌ {filepath.name}: Feature extraction failed: {e}")
                continue
        
        # Final verdict
        print("\n" + "="*70)
        if success_count == len(universe_files) and success_count > 0:
            print("✅ END-TO-END TEST PASSED!")
            print(f"   All {success_count} universes are ready for backtesting")
            print("="*70 + "\n")
            return True
        else:
            print(f"❌ END-TO-END TEST FAILED!")
            print(f"   {success_count}/{len(universe_files)} universes passed")
            print("="*70 + "\n")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    success = test_end_to_end()
    sys.exit(0 if success else 1)
