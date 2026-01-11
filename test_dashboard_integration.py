#!/usr/bin/env python3
"""
Complete integration test for ULTRA NECROZMA Dashboard Generator

This script demonstrates the complete workflow:
1. Create sample JSON reports
2. Generate dashboard
3. Validate output
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ⚡🌟💎 ULTRA NECROZMA DASHBOARD INTEGRATION TEST 💎🌟⚡       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

# Step 1: Ensure reports directory exists
print("📁 Step 1: Creating reports directory...")
reports_dir = Path("ultra_necrozma_results/reports")
reports_dir.mkdir(parents=True, exist_ok=True)
print(f"   ✅ Directory ready: {reports_dir}")

# Step 2: Create comprehensive sample data
print("\n📝 Step 2: Creating sample JSON reports...")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Generate realistic sample data
sample_data = {
    'executive_summary': {
        "generated_at": datetime.now().isoformat(),
        "project": "Ultra Necrozma Forex Analysis",
        "version": "2.0",
        "key_findings": {
            "market_regime": "TRENDING",
            "primary_strategy": "MODERATE TREND-FOLLOWING",
            "confidence_level": "MEDIUM-HIGH",
            "optimal_configuration": {
                "interval": 15,
                "lookback": 50,
                "score": 85.5
            }
        },
        "statistics": {
            "universes_analyzed": 42,
            "total_patterns_found": 1250,
            "analysis_power": "95.0%"
        }
    },
    
    'final_judgment': {
        "z_move": "LIGHT_THAT_BURNS_THE_SKY",
        "timestamp": datetime.now().isoformat(),
        "judgment_time_seconds": 45.2,
        "summary": {
            "universes_analyzed": 42,
            "total_patterns": 1250,
            "evolution_stage": "Ultra Necrozma",
            "light_power": 95.0,
            "prismatic_cores": ["Red", "Blue", "Yellow", "Green", "Orange", "Violet", "Pink"]
        },
        "market_regime": {
            "regime": "TRENDING",
            "dfa_alpha": 0.58,
            "hurst_exponent": 0.62,
            "lyapunov_exponent": 0.035,
            "fractal_dimension": 1.45,
            "shannon_entropy": 2.3,
            "chaos_level": "MODERATE",
            "complexity": "HIGH"
        },
        "rankings": [
            {"rank": i, "name": f"Universe_{i*5}min_{i*10}lb", "interval": i*5, 
             "lookback": i*10, "total_patterns": 150-i*5, "score": 100-i*5}
            for i in range(1, 21)
        ],
        "level_analysis": {
            "pequeno": {
                "up": {"total": 320, "top_patterns": []},
                "down": {"total": 315, "top_patterns": []}
            },
            "medio": {
                "up": {"total": 185, "top_patterns": []},
                "down": {"total": 180, "top_patterns": []}
            },
            "grande": {
                "up": {"total": 125, "top_patterns": []},
                "down": {"total": 120, "top_patterns": []}
            },
            "muito_grande": {
                "up": {"total": 35, "top_patterns": []},
                "down": {"total": 30, "top_patterns": []}
            }
        },
        "recommendations": {
            "primary_strategy": "MODERATE TREND-FOLLOWING",
            "confidence": "MEDIUM-HIGH",
            "key_points": [
                "Wait for pullbacks to enter trends",
                "Use 2-3 candle confirmation before entry",
                "Set reasonable profit targets",
                "Consider partial position scaling",
                "Best for: Médio and Grande movements",
                "Optimal timeframe: 15 minute candles with 50 lookback"
            ],
            "risk_level": "MEDIUM",
            "optimal_timeframe": "15min"
        },
        "best_configuration": {
            "name": "Universe_15min_50lb",
            "interval": 15,
            "lookback": 50,
            "total_patterns": 145,
            "score": 95.5
        }
    }
}

# Add remaining reports
sample_data['rankings'] = {
    "generated_at": datetime.now().isoformat(),
    "total_universes": 42,
    "rankings": sample_data['final_judgment']['rankings'],
    "top_10_summary": sample_data['final_judgment']['rankings'][:10]
}

sample_data['market_analysis'] = {
    "generated_at": datetime.now().isoformat(),
    "regime": sample_data['final_judgment']['market_regime'],
    "recommendations": sample_data['final_judgment']['recommendations']
}

sample_data['pattern_catalog'] = {
    "generated_at": datetime.now().isoformat(),
    "levels": {
        "pequeno": {
            "technical_name": "Small Movement (5-15 pips)",
            "pip_range": "5-15",
            "directions": sample_data['final_judgment']['level_analysis']['pequeno']
        },
        "medio": {
            "technical_name": "Medium Movement (15-30 pips)",
            "pip_range": "15-30",
            "directions": sample_data['final_judgment']['level_analysis']['medio']
        },
        "grande": {
            "technical_name": "Large Movement (30-50 pips)",
            "pip_range": "30-50",
            "directions": sample_data['final_judgment']['level_analysis']['grande']
        },
        "muito_grande": {
            "technical_name": "Very Large Movement (50+ pips)",
            "pip_range": "50+",
            "directions": sample_data['final_judgment']['level_analysis']['muito_grande']
        }
    }
}

# Write all reports
for report_type, data in sample_data.items():
    filename = reports_dir / f"{report_type}_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"   ✅ Created {filename.name}")

# Step 3: Generate dashboard
print("\n🎨 Step 3: Generating dashboard...")

from dashboard_generator import DashboardGenerator

generator = DashboardGenerator()
dashboard_path = generator.generate_dashboard()

if not dashboard_path:
    print("   ❌ Dashboard generation failed!")
    sys.exit(1)

print(f"   ✅ Dashboard created: {dashboard_path}")

# Step 4: Validate dashboard
print("\n🔍 Step 4: Validating dashboard...")

with open(dashboard_path, 'r') as f:
    html = f.read()

validation_checks = [
    ('<!DOCTYPE html>' in html, 'Valid HTML5 document'),
    ('ULTRA NECROZMA' in html, 'Title and branding'),
    ('Chart.js' in html, 'Chart.js library'),
    ('Bootstrap' in html, 'Bootstrap framework'),
    ('DataTables' in html, 'DataTables plugin'),
    ('Executive Summary' in html, 'Executive summary section'),
    ('Market Regime' in html, 'Market regime section'),
    ('Top 20' in html, 'Top patterns table'),
    ('Universe Performance' in html, 'Universe rankings'),
    ('Pattern Distribution' in html, 'Distribution charts'),
    ('Detailed Statistics' in html, 'Statistics panel'),
    ('toggleTheme' in html, 'Theme toggle function'),
    ('dashboardData' in html, 'Embedded data'),
    ('@media (max-width: 768px)' in html, 'Responsive design'),
    ('@media print' in html, 'Print styles'),
    ('regime-TRENDING' in html, 'Regime styling'),
    ('42' in html, 'Universe count'),
    ('1,250' in html, 'Pattern count'),
    ('95.0%' in html, 'Light power'),
]

passed = 0
failed = 0

for check, description in validation_checks:
    if check:
        print(f"   ✅ {description}")
        passed += 1
    else:
        print(f"   ❌ {description}")
        failed += 1

# Step 5: File size check
print("\n📊 Step 5: File size analysis...")
size = os.path.getsize(dashboard_path)
size_kb = size / 1024
print(f"   File size: {size:,} bytes ({size_kb:.1f} KB)")

if 10 < size_kb < 100:
    print("   ✅ File size is optimal")
else:
    print(f"   ⚠️  File size is {'too small' if size_kb < 10 else 'large'}")

# Final summary
print("\n" + "="*70)
print("INTEGRATION TEST SUMMARY")
print("="*70)
print(f"Dashboard path: {dashboard_path}")
print(f"Validation: {passed}/{len(validation_checks)} checks passed")
print(f"File size: {size_kb:.1f} KB")

if failed == 0:
    print("\n✅ ALL TESTS PASSED!")
    print("\nTo view the dashboard:")
    print(f"   Open in browser: file://{os.path.abspath(dashboard_path)}")
    print(f"   Or run: python3 dashboard_generator.py --open")
    sys.exit(0)
else:
    print(f"\n❌ {failed} TESTS FAILED")
    sys.exit(1)
