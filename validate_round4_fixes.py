#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script as mentioned in problem statement
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import StrategyFactory
from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS


def validate_fixes():
    """Validate all Round 4 fixes"""
    print("\n" + "=" * 70)
    print("🧪 ROUND 4 FIXES VALIDATION")
    print("=" * 70)
    
    factory = StrategyFactory()
    strategies = factory.generate_strategies()
    
    # Count strategies by template
    v3_count = sum(1 for s in strategies if "MeanReverterV3" in s.name)
    mb_count = sum(1 for s in strategies if "MomentumBurst" in s.name)
    
    print(f"\n📊 Strategy Counts:")
    print(f"   MeanReverterV3: {v3_count} (expected: 216)")
    print(f"   MomentumBurst: {mb_count}")
    
    # Verify V3 strategies have correct lookback
    v3_strategies = [s for s in strategies if "MeanReverterV3" in s.name]
    if v3_strategies:
        sample_v3 = v3_strategies[0]
        print(f"\n📋 Sample V3 Strategy:")
        print(f"   Name: {sample_v3.name}")
        print(f"   Lookback: {sample_v3.lookback} (should be 5)")
        
        # Check if name includes V3 parameters
        has_at = "_AT" in sample_v3.name
        has_rc = "_RC" in sample_v3.name
        has_sf = "_SF" in sample_v3.name
        
        print(f"\n🏷️  V3 Parameter Naming:")
        print(f"   Adaptive Threshold (AT) in name: {'✅' if has_at else '❌'}")
        print(f"   Require Confirmation (RC) in name: {'✅' if has_rc else '❌'}")
        print(f"   Session Filter (SF) in name: {'✅' if has_sf else '❌'}")
    
    # Verify MomentumBurst doesn't have CD30
    mb_strategies = [s for s in strategies if "MomentumBurst" in s.name]
    cd30_count = sum(1 for s in mb_strategies if "CD30" in s.name)
    
    print(f"\n🔍 MomentumBurst Analysis:")
    print(f"   Total MB strategies: {mb_count}")
    print(f"   Strategies with CD30: {cd30_count}")
    print(f"   CD30 removed: {'✅' if cd30_count == 0 else '❌'}")
    
    if mb_strategies:
        sample_mb = mb_strategies[0]
        print(f"\n📋 Sample MB Strategy:")
        print(f"   Name: {sample_mb.name}")
        print(f"   Max trades per day: {sample_mb.max_trades_per_day} (should be 10)")
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 VALIDATION SUMMARY")
    print("=" * 70)
    
    checks = {
        "MeanReverterV3 count": v3_count == 216,
        "V3 uses L5": v3_strategies[0].lookback == 5 if v3_strategies else False,
        "V3 names include params": has_at and has_rc and has_sf if v3_strategies else False,
        "CD30 removed": cd30_count == 0,
        "MB max_trades_per_day": mb_strategies[0].max_trades_per_day == 10 if mb_strategies else False,
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    passed = sum(checks.values())
    total = len(checks)
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ ALL {total} VALIDATION CHECKS PASSED!")
        print("=" * 70)
        return True
    else:
        print(f"⚠️  {passed}/{total} VALIDATION CHECKS PASSED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = validate_fixes()
    sys.exit(0 if success else 1)
