# 📊 Screening Analysis Scripts

Two comprehensive Python scripts for analyzing NECROZMA screening results.

## Scripts Overview

### 1. `deep_analysis.py` - Operational Strategies Analysis
Analyzes the 748 strategies in the operational range (50-50,000 trades).

### 2. `diagnose_extremes.py` - Extreme Cases Diagnosis
Diagnoses strategies outside operational ranges and identifies non-functioning templates.

---

## Usage

### Running the Scripts

```bash
# Analyze operational strategies (50-50,000 trades)
python deep_analysis.py

# Diagnose extreme cases (< 50 or > 50,000 trades)
python diagnose_extremes.py
```

### Prerequisites

```bash
pip install pandas numpy
```

---

## Output Files

### deep_analysis.py Outputs

| File | Description | Size |
|------|-------------|------|
| `deep_analysis.csv` | All 748 operational strategies with metrics | ~292KB |
| `parameter_analysis.csv` | Parameter performance breakdown by template | ~11KB |
| `deep_analysis.txt` | Comprehensive report with 7 sections | ~103KB |

### diagnose_extremes.py Outputs

| File | Description | Size |
|------|-------------|------|
| `extremes_diagnosis.csv` | 1,949 extreme strategies (low + high) | ~540KB |
| `extremes_diagnosis.txt` | Diagnostic report with recommendations | ~14KB |

---

## deep_analysis.py Report Sections

### 1. Complete Listing
All 748 strategies organized by frequency band:
- **FAIXA 1**: 140 strategies (50-500 trades) - Swing Trading
- **FAIXA 2**: 201 strategies (500-5,000 trades) - Day Trading
- **FAIXA 3**: 407 strategies (5,000-50,000 trades) - Scalping

### 2. Analysis by Template
Statistics for each template:
- Count by frequency band
- Sharpe Ratio (mean, median, max, min)
- Profit Factor, Win Rate, N Trades
- Best configuration

### 3. Parameter Analysis
Performance breakdown by parameter values:
- T (Threshold), SL (Stop Loss), TP (Take Profit)
- RSI ranges, CD (Cooldown), L (Lookback)
- Average Sharpe, PF, WR per value

### 4. Parameter Heatmaps (Text-based)
- T vs SL → Average Sharpe Ratio
- T vs TP → Average Sharpe Ratio
- SL vs TP → Average Win Rate

### 5. Quality Tier Filters
- **TIER 1**: Sharpe > 1.0 AND PF > 1.2 AND WR > 30% (9 strategies)
- **TIER 2**: Sharpe > 0.5 AND PF > 1.1 AND WR > 25% (64 strategies)
- **TIER 3**: Sharpe > 0 AND PF > 1.0 (278 strategies)

### 6. Weighted Ranking - Top 50
Score = (Sharpe_norm × 0.4) + (PF_norm × 0.3) + (WR_norm × 0.3)

### 7. Final Recommendations
Top 10 candidates for GBPUSD with diversity across:
- Templates (MeanReverter, MeanReverterV2, etc.)
- Frequency bands

---

## diagnose_extremes.py Report Sections

### 1. Strategies with < 50 Trades (1,357 total)
- Breakdown by template
- Breakdown by parameter
- Pattern identification
- Examples by trade count (0, 1-10, 10-49)

### 2. Strategies with > 50,000 Trades (592 total)
- Breakdown by template
- Breakdown by parameter
- Pattern identification
- Distribution (50k-100k, 100k-500k, 500k-1M, >1M)

### 3. Non-Functioning Templates
Templates with 100% zero trades:
- CorrelationTrader
- LeadLagStrategy
- PairDivergence
- PatternRecognition
- RegimeAdapter
- RiskSentiment
- ScalpingStrategy
- USDStrength

### 4. Recommendations
- Parameter adjustments for low/high trade strategies
- Template actions (REMOVE, REVIEW, ADJUST)

### 5. Final Decision Table
Summary of actions for each category

---

## Key Findings

### Top Performers (from deep_analysis.py)

| Rank | Strategy | Sharpe | PF | WR |
|------|----------|--------|----|----|
| 1 | MeanReverter_L5_T1.8_SL30_TP50 | 3.400 | 1.633 | 40.9% |
| 2 | MeanReverterV2_L30_T1.5_SL20_TP40 | 3.129 | 1.539 | 44.4% |
| 3 | MeanReverter_L5_T1.8_SL10_TP50 | 2.960 | 1.707 | 22.1% |

### Actions Required (from diagnose_extremes.py)

| Category | Count | Action |
|----------|-------|--------|
| Low trades (< 50) | 1,357 | DISCARD |
| High trades (> 50k) | 592 | DISCARD |
| Non-functioning templates | 8 | REMOVE |
| Templates needing adjustment | 1 | ADJUST |

---

## Round 3 Recommendations

Based on the analysis:

✅ **Focus on:**
- MeanReverter and MeanReverterV2 templates
- T parameter range: 1.5-2.0 for best balance
- SL/TP combinations from heatmap analysis

❌ **Remove:**
- 8 templates with 100% zero trades
- Strategies with < 50 or > 50,000 trades

⚙️ **Adjust:**
- SessionBreakout template (77.8% zero trades)
- Parameter ranges based on extreme analysis

---

## Notes

- Scripts are standalone and only require pandas/numpy
- Robust to NaN/Inf values in data
- Console output shows progress
- All reports use UTF-8 encoding
- Scripts automatically exclude their own output files when loading data

---

## File Locations

```
screening_results/
├── round1.csv                    # Input
├── round2.csv                    # Input
├── deep_analysis.csv             # Output
├── deep_analysis.txt             # Output
├── parameter_analysis.csv        # Output
├── extremes_diagnosis.csv        # Output
└── extremes_diagnosis.txt        # Output
```

---

## Contact

For issues or questions, refer to the main NECROZMA README.md

⚡🌟💎 ULTRA NECROZMA 💎🌟⚡
