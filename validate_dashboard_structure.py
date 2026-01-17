#!/usr/bin/env python3
"""
Simple validation script to check dashboard file structure
"""

import os
from pathlib import Path

def check_dashboard_structure():
    """Validate dashboard structure and files"""
    
    base_dir = Path(__file__).parent
    dashboard_dir = base_dir / "dashboard"
    
    print("=" * 60)
    print("NECROZMA Dashboard Structure Validation")
    print("=" * 60)
    
    # Check main files
    print("\n📁 Main Files:")
    main_files = ['app.py', '__init__.py']
    for file in main_files:
        path = dashboard_dir / file
        status = "✅" if path.exists() else "❌"
        print(f"{status} {file}")
    
    # Check utils
    print("\n📁 Utils:")
    utils_files = ['data_loader.py', 'formatters.py', 'trade_analyzer.py']
    for file in utils_files:
        path = dashboard_dir / "utils" / file
        status = "✅" if path.exists() else "❌"
        print(f"{status} utils/{file}")
    
    # Check components
    print("\n📁 Components:")
    component_files = [
        'charts.py', 'filters.py', 'metrics.py', 'tables.py',
        'drawdown_chart.py', 'equity_curve.py', 'monte_carlo.py'
    ]
    for file in component_files:
        path = dashboard_dir / "components" / file
        status = "✅" if path.exists() else "❌"
        print(f"{status} components/{file}")
    
    # Check pages
    print("\n📁 Pages:")
    expected_pages = [
        '1_📊_Overview.py',
        '2_📈_Performance_Matrix.py',
        '3_🎯_Strategy_Explorer.py',
        '4_⚠️_Risk_Analysis.py',
        '5_💰_Profitability.py',
        '6_🔧_Lot_Size_Analysis.py',
        '7_📊_Strategy_Templates.py',
        '8_🏆_Top_Performers.py',
        '9_📤_Export.py'
    ]
    
    pages_dir = dashboard_dir / "pages"
    
    # Check if pages directory exists
    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return
    
    for page in expected_pages:
        path = pages_dir / page
        status = "✅" if path.exists() else "❌"
        print(f"{status} pages/{page}")
    
    # Check for old pages that should be removed/renamed
    print("\n🗑️  Deprecated Pages (should not exist):")
    old_pages = [
        '3_🎯_Strategy_Deep_Dive.py',
        '5_⚠️_Risk_Analysis.py',
        '7_🏆_Composite_Ranking.py'
    ]
    
    for page in old_pages:
        path = pages_dir / page
        if path.exists():
            print(f"⚠️  {page} still exists (should be removed)")
        else:
            print(f"✅ {page} properly removed/renamed")
    
    # Check requirements
    print("\n📄 Requirements:")
    req_file = base_dir / "requirements-dashboard.txt"
    if req_file.exists():
        with open(req_file) as f:
            content = f.read()
            status = "✅" if "pyarrow" in content else "❌"
            print(f"{status} pyarrow in requirements-dashboard.txt")
    else:
        print("❌ requirements-dashboard.txt not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Complete!")
    print("=" * 60)
    
    # Count files
    total_pages = len(list(pages_dir.glob("*.py")))
    print(f"\n📊 Total pages: {total_pages}")
    print(f"📊 Expected pages: {len(expected_pages)}")
    
    if total_pages == len(expected_pages):
        print("✅ Page count matches expected!")
    else:
        print(f"⚠️  Page count mismatch: {total_pages} found, {len(expected_pages)} expected")

if __name__ == "__main__":
    check_dashboard_structure()
