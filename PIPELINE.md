# 🔬 NECROZMA - Pipeline de Análise Multi-Par

## 📋 Visão Geral

Pipeline de descoberta de edge através de matemática pura e confirmação multi-par.

**Filosofia:** ZERO indicadores técnicos. Apenas física estatística e teoria do caos.

---

## 🎯 FASE 1: LABELING COMPLETO (2 Pares Base)

### Objetivo
Pré-computar TODOS os outcomes possíveis para grid search posterior.

### Pares
- EURUSD (14.6M ticks)
- GBPUSD

### Configs (210 combinações)
| Parâmetro | Valores |
|-----------|---------|
| TP (pips) | 5, 10, 15, 20, 30 |
| SL (pips) | 5, 10, 15, 20, 30 |
| Horizon   | 1, 5, 15, 30, 60, 240, 1440 min |

### Output
```
labels/
├── T5_S5_H1.parquet      (14.6M rows)
├── T5_S5_H5.parquet      (14.6M rows)
├── ...
└── T30_S30_H1440.parquet (14.6M rows)
```

### Tempo Estimado
~2 horas por par = 4 horas total

---

## 🎯 FASE 2: FEATURES MATEMÁTICAS

### Objetivo
Calcular estado matemático de cada momento. NÃO são indicadores!

### Features (Física Estatística)

| Feature | O Que Mede | Interpretação |
|---------|-----------|---------------|
| **Hurst Exponent** | Persistência da série | H < 0.5: mean-reverting, H = 0.5: random walk, H > 0.5: trending |
| **Lyapunov Exponent** | Caos determinístico | λ < 0: estável, λ > 0: caótico mas previsível curto prazo |
| **Permutation Entropy** | Aleatoriedade | Baixa: padrões detectáveis, Alta: ruído puro |
| **DFA** | Correlações longo prazo | Detecta memória na série temporal |
| **Complexity-Entropy Plane** | Ordem vs Caos | Classifica regime em espaço 2D |

### Output
```
features/
├── EURUSD_features.parquet
└── GBPUSD_features.parquet
```

---

## 🎯 FASE 3: REGIME DETECTION

### Objetivo
Agrupar estados matemáticos similares (clustering não-supervisionado).

### Método
- K-Means / HDBSCAN
- Features: Hurst, Lyapunov, Entropy, DFA, Complexity
- Descoberta automática de número ótimo de clusters

### Output
```
Regime 0: "Trending Previsível"    (Hurst alto, Entropy baixa)
Regime 1: "Random Walk"            (Hurst ~0.5, Entropy alta)
Regime 2: "Mean Reverting"         (Hurst baixo, Entropy média)
Regime 3: "Caos Volátil"           (Lyapunov alto, Entropy alta)
```

---

## 🎯 FASE 4: CRUZAMENTO REGIME × LABEL

### Objetivo
Descobrir qual config funciona melhor em cada regime matemático.

### Query
```
"No Regime 0 (Trending Previsível), qual TP/SL/Horizon
 tem melhor win rate / profit factor / Sharpe?"
```

### Output Exemplo
```
┌─────────────────────────────────────────────────────────────┐
│ REGIME 0 (Trending Previsível)                              │
│                                                             │
│ TOP 5 CONFIGS:                                              │
│ 1. T20_S10_H60  → 73.2% win rate, 2.4 PF, 1.8 Sharpe       │
│ 2. T15_S10_H60  → 71.8% win rate, 2.2 PF, 1.7 Sharpe       │
│ 3. T20_S15_H60  → 70.5% win rate, 2.1 PF, 1.6 Sharpe       │
│ 4. T15_S10_H30  → 69.2% win rate, 2.0 PF, 1.5 Sharpe       │
│ 5. T20_S10_H30  → 68.8% win rate, 1.9 PF, 1.5 Sharpe       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 FASE 5: FILTRO TOP 5-10%

### Objetivo
Reduzir de 210 configs para ~15-20 melhores.

### Critérios de Filtro
1. Win rate > 65%
2. Profit factor > 1.8
3. Sharpe > 1.2
4. Funciona em AMBOS os pares (EURUSD + GBPUSD)
5. p-value < 0.05 (estatisticamente significativo)

### Output
```
TOP_CONFIGS = [
    "T20_S10_H60",
    "T15_S10_H60",
    "T20_S15_H60",
    "T15_S10_H30",
    ...
    # ~15-20 configs total
]
```

### Benefício
- 210 configs → 15-20 configs = 93% redução de processamento
- Próximas fases rodam 10x mais rápido

---

## 🎯 FASE 6: EXPANSÃO PARA 10 PARES

### Objetivo
Validar configs em múltiplos mercados.

### Pares
```
MAJORS:
1. EURUSD  ✅ (Fase 1)
2. GBPUSD  ✅ (Fase 1)
3. USDJPY
4. USDCHF
5. AUDUSD
6. USDCAD
7. NZDUSD

CROSSES:
8. EURJPY
9. GBPJPY
10. EURGBP
```

### Processamento
- 10 pares × 15-20 configs = 150-200 testes
- vs 10 × 210 = 2100 testes (sem filtro)
- ~3 horas total

---

## 🎯 FASE 7: CONFIRMAÇÃO MULTI-PAR

### Objetivo
Detectar quando múltiplos pares confirmam a mesma direção.

### Lógica
```
MOMENTO T:

EURUSD:  Regime=Trending, Label=UP    ✅
GBPUSD:  Regime=Trending, Label=UP    ✅
USDJPY:  Regime=Trending, Label=DOWN  ✅ (USD fraco)
EURJPY:  Regime=Trending, Label=UP    ✅
AUDUSD:  Regime=Trending, Label=UP    ✅

5/5 PARES CONFIRMAM: "USD FRACO"
→ SINAL DE ALTA CONFIANÇA
```

### Níveis de Confiança
| Pares Confirmando | Confiança | Ação |
|-------------------|-----------|------|
| 1 par | 50% | Sinal fraco - posição mínima |
| 2-3 pares | 70% | Sinal médio - posição normal |
| 4-6 pares | 85% | Sinal forte - posição maior |
| 7+ pares | 95%+ | SINAL MÁXIMO - posição máxima |
| Conflito | - | NÃO ENTRA (mercado confuso) |

---

## 🎯 FASE 8: MATRIZ DE FORÇA DE MOEDAS

### Objetivo
Identificar moeda mais forte e mais fraca no momento.

### Cálculo
```
MOMENTO T:

        EUR   GBP   USD   JPY   CHF   AUD   CAD   NZD
EUR      -    UP    UP    UP    UP    UP    UP    UP   → SCORE: +7
GBP    DOWN    -    UP    UP    UP    UP    UP    UP   → SCORE: +5
USD    DOWN  DOWN    -   DOWN  DOWN  DOWN  DOWN  DOWN  → SCORE: -7
JPY    DOWN  DOWN   UP     -   DOWN  DOWN  DOWN   UP   → SCORE: -3
CHF    DOWN  DOWN   UP    UP     -   DOWN   UP    UP   → SCORE: +1
AUD    DOWN  DOWN   UP    UP    UP     -    UP    UP   → SCORE: +3
CAD    DOWN  DOWN   UP    UP   DOWN  DOWN    -    UP   → SCORE: -1
NZD    DOWN  DOWN   UP   DOWN  DOWN  DOWN  DOWN    -   → SCORE: -5

RANKING:
1. EUR (+7) - MAIS FORTE
2. GBP (+5)
3. AUD (+3)
4. CHF (+1)
5. CAD (-1)
6. JPY (-3)
7. NZD (-5)
8. USD (-7) - MAIS FRACO

AÇÃO: Comprar EUR/USD (forte vs fraco)
```

---

## 🎯 FASE 9: ANÁLISE TEMPORAL

### Objetivo
Descobrir relações de liderança entre pares.

### Perguntas
1. **Lag Analysis**: "EURUSD sinaliza X minutos antes de GBPUSD?"
2. **Lead-Lag**: "Quais pares são LÍDERES vs SEGUIDORES?"
3. **Propagação**: "Como sinal se propaga entre pares?"

### Output Exemplo
```
LEAD-LAG MATRIX:

EURUSD lidera GBPUSD em 3.2 min (correlação 0.87)
EURUSD lidera EURGBP em 1.8 min (correlação 0.92)
USDJPY lidera EURJPY em 2.5 min (correlação 0.84)

→ EURUSD é o PAR LÍDER para EUR
→ USDJPY é o PAR LÍDER para JPY
```

---

## 🎯 FASE 10: VALIDAÇÃO FINAL

### Objetivo
Confirmar edge com rigor estatístico.

### Testes
1. **Out-of-Sample**: Train/Test split temporal
2. **Walk-Forward**: Janelas deslizantes
3. **Monte Carlo**: Simulações randomizadas
4. **Bootstrap**: Intervalos de confiança

### Critérios de Aprovação
- [ ] Win rate consistente across pares (±5%)
- [ ] Profit factor > 1.5 em 80%+ dos pares
- [ ] p-value < 0.01
- [ ] Drawdown máximo < 20%
- [ ] Edge sobrevive custos de transação

---

## 📊 RESUMO DO PIPELINE

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  DADOS BRUTOS (Ticks)                                           │
│         ↓                                                       │
│  FASE 1: Labeling 210 configs (EURUSD + GBPUSD)                │
│         ↓                                                       │
│  FASE 2: Features Matemáticas (Hurst, Lyapunov, Entropy...)    │
│         ↓                                                       │
│  FASE 3: Regime Detection (Clustering)                         │
│         ↓                                                       │
│  FASE 4: Cruzamento Regime × Label                             │
│         ↓                                                       │
│  FASE 5: Filtro Top 5-10% configs                              │
│         ↓                                                       │
│  FASE 6: Expansão 10 pares                                     │
│         ↓                                                       │
│  FASE 7: Confirmação Multi-Par                                 │
│         ↓                                                       │
│  FASE 8: Matriz Força de Moedas                                │
│         ↓                                                       │
│  FASE 9: Análise Temporal (Lead-Lag)                           │
│         ↓                                                       │
│  FASE 10: Validação Estatística                                │
│         ↓                                                       │
│  💎 EDGE CONFIRMADO MATEMATICAMENTE 💎                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ TEMPO ESTIMADO TOTAL

| Fase | Tempo |
|------|-------|
| Fase 1: Labeling 2 pares | ~4 horas |
| Fase 2: Features | ~30 min |
| Fase 3: Regime Detection | ~15 min |
| Fase 4: Cruzamento | ~15 min |
| Fase 5: Filtro | ~5 min |
| Fase 6: Expansão 10 pares | ~3 horas |
| Fase 7-9: Multi-Par Analysis | ~1 hora |
| Fase 10: Validação | ~1 hora |
| **TOTAL** | **~10 horas** |

---

## 🔬 FILOSOFIA

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  "Não usamos RSI porque alguém inventou.                      ║
║   Usamos Hurst porque a MATEMÁTICA prova."                    ║
║                                                               ║
║  "Não achamos que vai subir.                                  ║
║   Os DADOS mostram persistência estatística."                 ║
║                                                               ║
║  "Não confiamos em 1 par.                                     ║
║   Exigimos CONFIRMAÇÃO de 10 mercados."                       ║
║                                                               ║
║  INDICADORES = Astrologia financeira 🔮                       ║
║  MATEMÁTICA  = Física do mercado 🔬                           ║
║                                                               ║
║  NECROZMA = FÍSICA! 💎                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```
