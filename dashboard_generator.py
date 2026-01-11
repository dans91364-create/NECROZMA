#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DASHBOARD GENERATOR 💎🌟⚡

Interactive HTML Dashboard Generator
"Transform crystallized data into brilliant visual light"

Technical: HTML dashboard generation from JSON reports
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class DashboardGenerator:
    """
    ULTRA NECROZMA Dashboard Generator
    
    Creates beautiful, interactive HTML dashboards from JSON analysis reports
    """
    
    def __init__(self, results_dir: str = "ultra_necrozma_results"):
        """
        Initialize dashboard generator
        
        Args:
            results_dir: Directory containing JSON reports
        """
        self.results_dir = Path(results_dir)
        self.reports_dir = self.results_dir / "reports"
        
    def find_latest_reports(self) -> Dict[str, Path]:
        """
        Find the latest set of JSON reports
        
        Returns:
            Dict mapping report type to file path
        """
        if not self.reports_dir.exists():
            return {}
        
        reports = {
            'executive_summary': None,
            'final_judgment': None,
            'rankings': None,
            'market_analysis': None,
            'pattern_catalog': None
        }
        
        # Find most recent files for each report type
        for report_type in reports.keys():
            pattern = f"{report_type}_*.json"
            files = list(self.reports_dir.glob(pattern))
            if files:
                # Sort by modification time, get most recent
                reports[report_type] = max(files, key=lambda p: p.stat().st_mtime)
        
        return {k: v for k, v in reports.items() if v is not None}
    
    def load_report(self, file_path: Path) -> Optional[Dict]:
        """
        Load JSON report from file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict with report data or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load {file_path}: {e}")
            return None
    
    def generate_dashboard(self, output_path: Optional[str] = None) -> str:
        """
        Generate complete HTML dashboard
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to generated HTML file
        """
        # Find and load reports
        print("🔍 Finding latest reports...")
        report_files = self.find_latest_reports()
        
        if not report_files:
            print("⚠️ No reports found!")
            return None
        
        print(f"✅ Found {len(report_files)} report files")
        
        # Load all reports
        reports = {}
        for report_type, file_path in report_files.items():
            print(f"📄 Loading {report_type}...")
            reports[report_type] = self.load_report(file_path)
        
        # Generate HTML
        print("🎨 Generating HTML dashboard...")
        html_content = self._generate_html(reports)
        
        # Determine output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.results_dir / f"dashboard_{timestamp}.html"
        else:
            output_path = Path(output_path)
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard saved to: {output_path}")
        return str(output_path)
    
    def _generate_html(self, reports: Dict[str, Dict]) -> str:
        """
        Generate complete HTML dashboard content
        
        Args:
            reports: Dictionary of loaded reports
            
        Returns:
            Complete HTML string
        """
        # Extract data
        executive = reports.get('executive_summary', {})
        judgment = reports.get('final_judgment', {})
        rankings = reports.get('rankings', {})
        market = reports.get('market_analysis', {})
        patterns = reports.get('pattern_catalog', {})
        
        # Build HTML sections
        html_parts = [
            self._html_header(),
            self._html_styles(),
            self._html_body_start(),
            self._html_header_section(),
            self._html_executive_summary(executive, judgment),
            self._html_market_regime(market, judgment),
            self._html_top_patterns(rankings, judgment),
            self._html_universe_rankings(rankings),
            self._html_pattern_distributions(patterns, judgment),
            self._html_statistics_panel(executive, judgment),
            self._html_footer(),
            self._html_scripts(reports),
            self._html_body_end()
        ]
        
        return '\n'.join(html_parts)
    
    def _html_header(self) -> str:
        """Generate HTML header with meta tags and CDN imports"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 ULTRA NECROZMA Analysis Dashboard</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
</head>'''
    
    def _html_styles(self) -> str:
        """Generate inline CSS styles for dark theme"""
        return '''<style>
    :root {
        --primary-dark: #0a0e27;
        --secondary-dark: #1a1f3a;
        --accent-purple: #a855f7;
        --accent-blue: #3b82f6;
        --accent-gold: #fbbf24;
        --text-light: #e5e7eb;
        --text-muted: #9ca3af;
        --border-color: #374151;
        --card-bg: #1e293b;
        --hover-bg: #2d3748;
    }
    
    body {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        color: var(--text-light);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        min-height: 100vh;
    }
    
    body.light-theme {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
        color: #1a202c;
        --primary-dark: #ffffff;
        --secondary-dark: #f7fafc;
        --card-bg: #ffffff;
        --hover-bg: #edf2f7;
        --text-light: #1a202c;
        --text-muted: #4a5568;
        --border-color: #cbd5e0;
    }
    
    .header-banner {
        background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-blue) 50%, var(--accent-purple) 100%);
        padding: 2rem;
        text-align: center;
        border-bottom: 3px solid var(--accent-gold);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.3);
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 4px 20px rgba(168, 85, 247, 0.3); }
        50% { box-shadow: 0 4px 30px rgba(168, 85, 247, 0.6); }
    }
    
    .header-banner h1 {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        color: white;
    }
    
    .header-banner .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        color: white;
    }
    
    .metric-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-purple);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .regime-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .regime-STRONG_TRENDING { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    .regime-TRENDING { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
    .regime-MEAN_REVERTING { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .regime-RANDOM_WALK { background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); }
    
    .confidence-HIGH { color: #10b981; }
    .confidence-MEDIUM-HIGH { color: #3b82f6; }
    .confidence-MEDIUM { color: #f59e0b; }
    .confidence-LOW-MEDIUM { color: #ef4444; }
    .confidence-LOW { color: #dc2626; }
    
    .data-table {
        background: var(--card-bg);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .data-table table {
        margin: 0;
    }
    
    .data-table thead {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-blue) 100%);
        color: white;
    }
    
    .data-table tbody tr {
        transition: background-color 0.2s ease;
    }
    
    .data-table tbody tr:hover {
        background-color: var(--hover-bg);
    }
    
    .chart-container {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .chart-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: var(--text-light);
    }
    
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--card-bg);
        border: 2px solid var(--accent-purple);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .theme-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(168, 85, 247, 0.5);
    }
    
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        text-align: center;
        background: var(--card-bg);
        border-top: 2px solid var(--accent-purple);
    }
    
    .recommendation-box {
        background: var(--card-bg);
        border-left: 4px solid var(--accent-purple);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .recommendation-box ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    @media print {
        .theme-toggle, .no-print { display: none; }
        body { background: white; color: black; }
        .metric-card, .chart-container { box-shadow: none; border: 1px solid #ccc; }
    }
    
    @media (max-width: 768px) {
        .header-banner h1 { font-size: 1.8rem; }
        .metric-value { font-size: 1.5rem; }
        .section-title { font-size: 1.4rem; }
    }
    
    /* Loading spinner */
    .spinner {
        border: 4px solid rgba(168, 85, 247, 0.3);
        border-top: 4px solid var(--accent-purple);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>'''
    
    def _html_body_start(self) -> str:
        """Start body tag"""
        return '<body>'
    
    def _html_header_section(self) -> str:
        """Generate header banner"""
        return '''
<!-- Theme Toggle -->
<div class="theme-toggle no-print" onclick="toggleTheme()">
    <i class="fas fa-moon" id="theme-icon"></i>
    <span id="theme-text" style="margin-left: 0.5rem;">Dark</span>
</div>

<!-- Header Banner -->
<header class="header-banner">
    <h1>⚡ ULTRA NECROZMA ANALYSIS DASHBOARD ⚡</h1>
    <p class="subtitle">💎 Light That Burns The Sky - Complete Market Analysis 💎</p>
</header>

<div class="container-fluid px-4 py-4">
'''
    
    def _html_executive_summary(self, executive: Dict, judgment: Dict) -> str:
        """Generate executive summary section with key metrics"""
        summary = judgment.get('summary', {})
        regime = judgment.get('market_regime', {})
        
        universes = summary.get('universes_analyzed', 0)
        patterns = summary.get('total_patterns', 0)
        light_power = summary.get('light_power', 0)
        evolution = summary.get('evolution_stage', 'Unknown')
        
        return f'''
<!-- Executive Summary -->
<section id="executive-summary">
    <h2 class="section-title">
        <i class="fas fa-chart-line"></i> Executive Summary
    </h2>
    
    <div class="row">
        <div class="col-md-3 col-sm-6">
            <div class="metric-card text-center">
                <div class="metric-icon">🌌</div>
                <div class="metric-value">{universes}</div>
                <div class="metric-label">Universes Analyzed</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="metric-card text-center">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{patterns:,}</div>
                <div class="metric-label">Total Patterns</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="metric-card text-center">
                <div class="metric-icon">⚡</div>
                <div class="metric-value">{light_power:.1f}%</div>
                <div class="metric-label">Light Power</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="metric-card text-center">
                <div class="metric-icon">💎</div>
                <div class="metric-value">{evolution}</div>
                <div class="metric-label">Evolution Stage</div>
            </div>
        </div>
    </div>
</section>
'''
    
    def _html_market_regime(self, market: Dict, judgment: Dict) -> str:
        """Generate market regime section"""
        regime_data = judgment.get('market_regime', {})
        recommendations = judgment.get('recommendations', {})
        
        regime = regime_data.get('regime', 'UNKNOWN')
        dfa = regime_data.get('dfa_alpha', 0.5)
        hurst = regime_data.get('hurst_exponent', 0.5)
        chaos = regime_data.get('chaos_level', 'UNKNOWN')
        
        strategy = recommendations.get('primary_strategy', 'N/A')
        confidence = recommendations.get('confidence', 'N/A')
        key_points = recommendations.get('key_points', [])
        
        confidence_class = confidence.replace(' ', '-').replace('/', '-')
        
        return f'''
<!-- Market Regime -->
<section id="market-regime">
    <h2 class="section-title">
        <i class="fas fa-chart-area"></i> Market Regime Analysis
    </h2>
    
    <div class="row">
        <div class="col-md-6">
            <div class="metric-card">
                <h3>Current Market Regime</h3>
                <div class="text-center my-4">
                    <span class="regime-badge regime-{regime}">{regime.replace('_', ' ')}</span>
                </div>
                <div class="mt-4">
                    <p><strong>DFA Alpha:</strong> {dfa:.3f}</p>
                    <p><strong>Hurst Exponent:</strong> {hurst:.3f}</p>
                    <p><strong>Chaos Level:</strong> {chaos}</p>
                </div>
                <canvas id="regimeChart" style="max-height: 250px;"></canvas>
            </div>
        </div>
        <div class="col-md-6">
            <div class="metric-card">
                <h3>Trading Recommendations</h3>
                <div class="mt-3">
                    <p><strong>Primary Strategy:</strong> {strategy}</p>
                    <p><strong>Confidence:</strong> <span class="confidence-{confidence_class}">{confidence}</span></p>
                </div>
                <div class="recommendation-box">
                    <h4><i class="fas fa-lightbulb"></i> Key Points:</h4>
                    <ul>
{''.join(f'<li>{point}</li>' for point in key_points[:5])}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</section>
'''
    
    def _html_top_patterns(self, rankings: Dict, judgment: Dict) -> str:
        """Generate top patterns interactive table"""
        top_rankings = judgment.get('rankings', [])[:20]
        
        table_rows = ''
        for i, rank in enumerate(top_rankings, 1):
            emoji = '💎' if i == 1 else '🌟' if i <= 3 else '⚡' if i <= 5 else '✨'
            table_rows += f'''
        <tr>
            <td>{emoji} {i}</td>
            <td>{rank.get('name', 'N/A')}</td>
            <td>{rank.get('interval', 'N/A')}</td>
            <td>{rank.get('lookback', 'N/A')}</td>
            <td>{rank.get('total_patterns', 0):,}</td>
            <td>{rank.get('score', 0):.1f}</td>
        </tr>'''
        
        return f'''
<!-- Top Patterns -->
<section id="top-patterns">
    <h2 class="section-title">
        <i class="fas fa-trophy"></i> Top 20 Universe Configurations
    </h2>
    
    <div class="data-table">
        <table id="patternsTable" class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Universe</th>
                    <th>Interval (min)</th>
                    <th>Lookback</th>
                    <th>Total Patterns</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
{table_rows}
            </tbody>
        </table>
    </div>
</section>
'''
    
    def _html_universe_rankings(self, rankings: Dict) -> str:
        """Generate universe rankings bar chart"""
        return '''
<!-- Universe Rankings -->
<section id="universe-rankings">
    <h2 class="section-title">
        <i class="fas fa-star"></i> Universe Performance Rankings
    </h2>
    
    <div class="chart-container">
        <canvas id="universeChart"></canvas>
    </div>
</section>
'''
    
    def _html_pattern_distributions(self, patterns: Dict, judgment: Dict) -> str:
        """Generate pattern distribution charts"""
        return '''
<!-- Pattern Distributions -->
<section id="pattern-distributions">
    <h2 class="section-title">
        <i class="fas fa-chart-bar"></i> Pattern Distribution Analysis
    </h2>
    
    <div class="row">
        <div class="col-md-6">
            <div class="chart-container">
                <h3 class="chart-title">Movement Level Distribution</h3>
                <canvas id="levelDistChart"></canvas>
            </div>
        </div>
        <div class="col-md-6">
            <div class="chart-container">
                <h3 class="chart-title">Direction Distribution</h3>
                <canvas id="directionChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-12">
            <div class="chart-container">
                <h3 class="chart-title">Pattern Complexity by Universe</h3>
                <canvas id="complexityChart"></canvas>
            </div>
        </div>
    </div>
</section>
'''
    
    def _html_statistics_panel(self, executive: Dict, judgment: Dict) -> str:
        """Generate statistics panel"""
        summary = judgment.get('summary', {})
        regime = judgment.get('market_regime', {})
        best = judgment.get('best_configuration', {})
        
        return f'''
<!-- Statistics Panel -->
<section id="statistics">
    <h2 class="section-title">
        <i class="fas fa-info-circle"></i> Detailed Statistics
    </h2>
    
    <div class="row">
        <div class="col-md-4">
            <div class="metric-card">
                <h4><i class="fas fa-database"></i> Data Analysis</h4>
                <ul class="list-unstyled mt-3">
                    <li><strong>Universes:</strong> {summary.get('universes_analyzed', 0)}</li>
                    <li><strong>Patterns Found:</strong> {summary.get('total_patterns', 0):,}</li>
                    <li><strong>Prismatic Cores:</strong> {len(summary.get('prismatic_cores', []))}/7</li>
                </ul>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metric-card">
                <h4><i class="fas fa-cogs"></i> Market Characteristics</h4>
                <ul class="list-unstyled mt-3">
                    <li><strong>DFA Alpha:</strong> {regime.get('dfa_alpha', 0):.3f}</li>
                    <li><strong>Hurst Exponent:</strong> {regime.get('hurst_exponent', 0):.3f}</li>
                    <li><strong>Lyapunov:</strong> {regime.get('lyapunov_exponent', 0):.4f}</li>
                    <li><strong>Fractal Dim:</strong> {regime.get('fractal_dimension', 0):.3f}</li>
                    <li><strong>Entropy:</strong> {regime.get('shannon_entropy', 0):.3f}</li>
                </ul>
            </div>
        </div>
        <div class="col-md-4">
            <div class="metric-card">
                <h4><i class="fas fa-trophy"></i> Best Configuration</h4>
                <ul class="list-unstyled mt-3">
                    <li><strong>Universe:</strong> {best.get('name', 'N/A')}</li>
                    <li><strong>Interval:</strong> {best.get('interval', 'N/A')} min</li>
                    <li><strong>Lookback:</strong> {best.get('lookback', 'N/A')} periods</li>
                    <li><strong>Score:</strong> {best.get('score', 0):.1f}</li>
                </ul>
            </div>
        </div>
    </div>
</section>
'''
    
    def _html_footer(self) -> str:
        """Generate footer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f'''
<footer class="footer">
    <p>⚡🌟💎 Generated by ULTRA NECROZMA v1.0 💎🌟⚡</p>
    <p>Dashboard created: {timestamp}</p>
    <p class="text-muted">Light That Burns The Sky - Supreme Analysis Engine</p>
</footer>

</div> <!-- Close container -->
'''
    
    def _html_scripts(self, reports: Dict) -> str:
        """Generate JavaScript for charts and interactivity"""
        judgment = reports.get('final_judgment', {})
        rankings = reports.get('rankings', {})
        
        # Extract data for charts
        top_rankings = judgment.get('rankings', [])[:10]
        universe_names = [r.get('name', f'U{i}') for i, r in enumerate(top_rankings)]
        universe_scores = [r.get('score', 0) for r in top_rankings]
        universe_patterns = [r.get('total_patterns', 0) for r in top_rankings]
        
        # Market regime data
        regime_data = judgment.get('market_regime', {})
        dfa = regime_data.get('dfa_alpha', 0.5)
        hurst = regime_data.get('hurst_exponent', 0.5)
        
        # Level analysis
        level_analysis = judgment.get('level_analysis', {})
        levels = ['pequeno', 'medio', 'grande', 'muito_grande']
        level_totals = []
        for level in levels:
            level_data = level_analysis.get(level, {})
            up_total = level_data.get('up', {}).get('total', 0)
            down_total = level_data.get('down', {}).get('total', 0)
            level_totals.append(up_total + down_total)
        
        return f'''
<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- jQuery (for DataTables) -->
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>

<!-- DataTables JS -->
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>

<script>
// Embedded data
const dashboardData = {json.dumps(reports, default=str)};

// Theme toggle
function toggleTheme() {{
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    
    body.classList.toggle('light-theme');
    
    if (body.classList.contains('light-theme')) {{
        icon.className = 'fas fa-sun';
        text.textContent = 'Light';
    }} else {{
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark';
    }}
    
    // Redraw charts with new theme
    updateChartColors();
}}

// Initialize DataTable
$(document).ready(function() {{
    $('#patternsTable').DataTable({{
        pageLength: 10,
        order: [[0, 'asc']],
        language: {{
            search: "Search patterns:",
            lengthMenu: "Show _MENU_ patterns"
        }}
    }});
}});

// Chart colors
function getChartColors() {{
    const isDark = !document.body.classList.contains('light-theme');
    return {{
        textColor: isDark ? '#e5e7eb' : '#1a202c',
        gridColor: isDark ? '#374151' : '#cbd5e0',
        purple: '#a855f7',
        blue: '#3b82f6',
        green: '#10b981',
        orange: '#f59e0b',
        red: '#ef4444',
        yellow: '#fbbf24'
    }};
}}

// Regime Chart
const regimeCtx = document.getElementById('regimeChart');
if (regimeCtx) {{
    const colors = getChartColors();
    new Chart(regimeCtx, {{
        type: 'radar',
        data: {{
            labels: ['DFA Alpha', 'Hurst', 'Persistence', 'Trend Strength', 'Memory'],
            datasets: [{{
                label: 'Market Characteristics',
                data: [{dfa}, {hurst}, {dfa}, {max(dfa, hurst)}, {hurst}],
                backgroundColor: 'rgba(168, 85, 247, 0.2)',
                borderColor: colors.purple,
                borderWidth: 2,
                pointBackgroundColor: colors.purple,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: colors.purple
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                r: {{
                    min: 0,
                    max: 1,
                    ticks: {{
                        color: colors.textColor,
                        backdropColor: 'transparent'
                    }},
                    grid: {{
                        color: colors.gridColor
                    }},
                    pointLabels: {{
                        color: colors.textColor
                    }}
                }}
            }},
            plugins: {{
                legend: {{
                    labels: {{
                        color: colors.textColor
                    }}
                }}
            }}
        }}
    }});
}}

// Universe Rankings Chart
const universeCtx = document.getElementById('universeChart');
if (universeCtx) {{
    const colors = getChartColors();
    new Chart(universeCtx, {{
        type: 'bar',
        data: {{
            labels: {json.dumps(universe_names)},
            datasets: [{{
                label: 'Score',
                data: {json.dumps(universe_scores)},
                backgroundColor: colors.purple,
                borderColor: colors.blue,
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{ color: colors.textColor }},
                    grid: {{ color: colors.gridColor }}
                }},
                x: {{
                    ticks: {{ 
                        color: colors.textColor,
                        maxRotation: 45,
                        minRotation: 45
                    }},
                    grid: {{ color: colors.gridColor }}
                }}
            }},
            plugins: {{
                legend: {{
                    labels: {{ color: colors.textColor }}
                }},
                tooltip: {{
                    callbacks: {{
                        afterLabel: function(context) {{
                            const patterns = {json.dumps(universe_patterns)};
                            return 'Patterns: ' + patterns[context.dataIndex].toLocaleString();
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

// Level Distribution Chart
const levelCtx = document.getElementById('levelDistChart');
if (levelCtx) {{
    const colors = getChartColors();
    new Chart(levelCtx, {{
        type: 'doughnut',
        data: {{
            labels: ['Pequeno', 'Médio', 'Grande', 'Muito Grande'],
            datasets: [{{
                data: {json.dumps(level_totals)},
                backgroundColor: [colors.blue, colors.green, colors.orange, colors.purple],
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            plugins: {{
                legend: {{
                    labels: {{ color: colors.textColor }}
                }}
            }}
        }}
    }});
}}

// Direction Chart
const directionCtx = document.getElementById('directionChart');
if (directionCtx) {{
    const colors = getChartColors();
    
    // Calculate total up and down
    let totalUp = 0;
    let totalDown = 0;
    {json.dumps(list(level_analysis.values()))}.forEach(level => {{
        totalUp += level.up?.total || 0;
        totalDown += level.down?.total || 0;
    }});
    
    new Chart(directionCtx, {{
        type: 'pie',
        data: {{
            labels: ['Up Moves', 'Down Moves'],
            datasets: [{{
                data: [totalUp, totalDown],
                backgroundColor: [colors.green, colors.red],
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            plugins: {{
                legend: {{
                    labels: {{ color: colors.textColor }}
                }}
            }}
        }}
    }});
}}

// Complexity Chart
const complexityCtx = document.getElementById('complexityChart');
if (complexityCtx) {{
    const colors = getChartColors();
    new Chart(complexityCtx, {{
        type: 'line',
        data: {{
            labels: {json.dumps(universe_names)},
            datasets: [{{
                label: 'Pattern Count',
                data: {json.dumps(universe_patterns)},
                borderColor: colors.purple,
                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                fill: true,
                tension: 0.4
            }}]
        }},
        options: {{
            responsive: true,
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{ color: colors.textColor }},
                    grid: {{ color: colors.gridColor }}
                }},
                x: {{
                    ticks: {{ 
                        color: colors.textColor,
                        maxRotation: 45,
                        minRotation: 45
                    }},
                    grid: {{ color: colors.gridColor }}
                }}
            }},
            plugins: {{
                legend: {{
                    labels: {{ color: colors.textColor }}
                }}
            }}
        }}
    }});
}}

// Export to CSV function
function exportToCSV() {{
    const table = document.getElementById('patternsTable');
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let row of rows) {{
        let cols = row.querySelectorAll('td, th');
        let csvRow = [];
        for (let col of cols) {{
            csvRow.push(col.innerText);
        }}
        csv.push(csvRow.join(','));
    }}
    
    const csvString = csv.join('\\n');
    const blob = new Blob([csvString], {{ type: 'text/csv' }});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ultra_necrozma_patterns.csv';
    a.click();
}}

// Print function
function printDashboard() {{
    window.print();
}}

// Update chart colors on theme change
function updateChartColors() {{
    // Reload page to redraw charts with new colors
    location.reload();
}}

console.log('⚡ ULTRA NECROZMA Dashboard loaded successfully!');
</script>
'''
    
    def _html_body_end(self) -> str:
        """Close body and html tags"""
        return '''
</body>
</html>'''


def main():
    """CLI entry point for dashboard generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="⚡🌟💎 ULTRA NECROZMA Dashboard Generator 💎🌟⚡"
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='ultra_necrozma_results',
        help='Directory containing JSON reports'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output HTML file path (default: auto-generated)'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open dashboard in browser after generation'
    )
    
    args = parser.parse_args()
    
    # Generate dashboard
    print("🌟 ULTRA NECROZMA Dashboard Generator")
    print("=" * 60)
    
    generator = DashboardGenerator(results_dir=args.results_dir)
    output_path = generator.generate_dashboard(output_path=args.output)
    
    if output_path:
        print(f"\n✅ Dashboard generated successfully!")
        print(f"📁 Location: {output_path}")
        
        # Open in browser if requested
        if args.open:
            import webbrowser
            print("\n🌐 Opening dashboard in browser...")
            webbrowser.open(f'file://{os.path.abspath(output_path)}')
    else:
        print("\n❌ Failed to generate dashboard")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
