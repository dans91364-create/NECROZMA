# ⚡🌟💎 Ultra Necrozma - Forex Analysis System 💎🌟⚡

> *"The Light That Burns The Sky - Illuminating Hidden Patterns"*

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![NumPy](https://img.shields.io/badge/NumPy-1.24+-orange.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Sistema avançado de análise de dados Forex com **500+ features** extraídas de séries temporais, utilizando técnicas de teoria do caos, análise fractal, entropia e processamento paralelo. 

---

## 🌟 Características

### 📊 Análise Avançada
- **500+ features** extraídas de cada janela de análise
- Derivadas até 5ª ordem (velocity, acceleration, jerk, snap, crackle)
- Análise espectral (FFT, Wavelets multi-escala)
- Teoria do Caos (Lyapunov, DFA, Hurst, Fractal Dimension)
- Entropia (Shannon, Sample, Permutation, Approximate)
- Reconstrução de Espaço de Fases (Takens Embedding)
- Análise Multifractal (MF-DFA)
- Quantificação de Recorrência (RQA)

### ⚡ Performance
- **Parquet** para armazenamento otimizado (10-20x mais rápido que CSV)
- **Numba JIT** para funções críticas (50-100x speedup)
- **Multiprocessing** para análise paralela (usa todos os cores)
- Otimizado para datasets de **16+ milhões de linhas**

### 🎮 Temática Pokémon
- Sistema de evolução (Necrozma → Ultra Necrozma)
- Coleta de Prismatic Cores
- Z-Move:  "Light That Burns The Sky" (análise final)
- Nomenclatura técnica + temática lado a lado

---

## 📁 Estrutura do Projeto

```
necroza/
├── config.py              # ⚙️  Configurações centralizadas
├── data_loader.py         # 💾 CSV → Parquet + Loading
├── features_core.py       # 🔬 Features básicas (derivadas, spectral, chaos, entropy)
├── features_advanced. py   # 🌌 Features avançadas (phase space, RQA, multifractal)
├── analyzer.py            # 🎯 Motor de análise + Paralelização
├── reports.py             # 📊 Geração de relatórios JSON
├── main.py                # 🚀 Ponto de entrada
├── requirements.txt       # 📦 Dependências
└── README.md              # 📖 Este arquivo
```

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/dans91364-create/necroza.git
cd necroza
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o caminho do CSV

Edite `config.py` e ajuste o caminho do seu arquivo CSV:

```python
CSV_FILE = Path("/home/usuario/EURUSD_2025_COMPLETO.csv")
```

---

## 📊 Formato dos Dados

O sistema espera um CSV com tick data no seguinte formato:

```csv
"Exness","Symbol","Timestamp","Bid","Ask"
"exness","EURUSD_Zero_Spread","2025-01-01 22:05:15. 653Z",1.03521,1.03552
"exness","EURUSD_Zero_Spread","2025-01-01 22:05:16.753Z",1.03527,1.03556
```

**Colunas necessárias:**
- `Timestamp` - Data/hora do tick (ISO format)
- `Bid` - Preço de compra
- `Ask` - Preço de venda

---

## 🎮 Uso

### Análise Completa (Recomendado)

```bash
python main.py
```

Este comando irá:
1. ✅ Verificar dependências
2. 💎 Converter CSV para Parquet (se necessário)
3. ⚡ Carregar dados
4. 🌌 Processar todas as configurações em paralelo
5. 📊 Gerar relatórios JSON

### Opções de Linha de Comando

```bash
# Apenas converter CSV para Parquet
python main.py --convert-only

# Apenas analisar (Parquet deve existir)
python main.py --analyze-only

# Rodar sequencialmente (sem paralelização)
python main.py --sequential

# Especificar número de workers
python main.py --workers 8

# Usar CSV customizado
python main.py --csv /caminho/para/dados.csv

# Forçar re-conversão do Parquet
python main.py --force-convert

# Modo de teste (dados sintéticos)
python main.py --test

# Ajuda
python main.py --help
```

### Modo de Teste

Para testar o sistema sem dados reais:

```bash
python main.py --test
```

Isso gera 100. 000 ticks sintéticos e executa a análise completa.

---

## ⚙️ Configuração

Todas as configurações estão em `config.py`:

### Intervalos de Tempo

```python
INTERVALS = [1, 5, 15, 30, 60]  # minutos
```

### Períodos de Lookback

```python
LOOKBACKS = [5, 10, 15, 20, 30]  # candles
```

### Níveis de Movimento

```python
MOVEMENT_LEVELS = {
    "Pequeno": {"min":  1, "max": 5},       # 1-5 pips
    "Médio":  {"min": 5, "max": 15},        # 5-15 pips
    "Grande": {"min": 15, "max": 30},      # 15-30 pips
    "Muito Grande": {"min": 30, "max": inf} # 30+ pips
}
```

### Workers Paralelos

```python
NUM_WORKERS = 16  # Ajuste conforme seus cores
```

### Grupos de Features

```python
FEATURE_GROUPS = {
    "derivatives": True,    # D1-D5
    "spectral": True,       # FFT, Wavelets
    "chaos": True,          # Lyapunov, DFA, Hurst
    "entropy": True,        # Shannon, Sample, etc.
    "quantum": True,        # Phase Space
    "multifractal": True,   # MF-DFA
    "recurrence": True,     # RQA
    "patterns": True,       # Crystal patterns
    "ultra":  True           # Photon, Z-Crystal
}
```

---

## 📈 Features Extraídas

### 🌟 Grupo 1: Derivadas (20+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `d1_mean` | Média da 1ª derivada (momentum) |
| `d2_current` | Aceleração atual |
| `d3_mean` | Jerk médio |
| `d4_mean` | Snap médio |
| `d5_mean` | Crackle médio |

### 💎 Grupo 2: Spectral (40+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `fft_freq_1` | Frequência dominante |
| `spectral_centroid` | Centro de massa espectral |
| `spectral_entropy` | Entropia do espectro |
| `wavelet_d1_energy` | Energia do detalhe nível 1 |

### 🔥 Grupo 3: Chaos (15+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `lyapunov` | Expoente de Lyapunov (sensibilidade ao caos) |
| `dfa_alpha` | DFA α (persistência/anti-persistência) |
| `hurst` | Expoente de Hurst (memória longa) |
| `fractal_dim` | Dimensão fractal de Higuchi |

### 🔮 Grupo 4: Entropy (20+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `entropy_shannon` | Entropia de Shannon |
| `entropy_sample` | Sample Entropy |
| `entropy_permutation` | Permutation Entropy |
| `entropy_approximate` | Approximate Entropy |

### 🌌 Grupo 5: Phase Space (15+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `correlation_dimension` | Dimensão de correlação |
| `phase_dist_mean` | Distância média no espaço de fases |
| `attractor_spread` | Espalhamento do atrator |

### 🔄 Grupo 6: RQA (12+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `recurrence_rate` | Taxa de recorrência |
| `determinism` | Determinismo (linhas diagonais) |
| `laminarity` | Laminaridade (linhas verticais) |
| `trapping_time` | Tempo de aprisionamento |

### 💎 Grupo 7: Multifractal (15+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `multifractal_width` | Largura do espectro multifractal |
| `mf_hurst_q2` | Hurst generalizado (q=2) |
| `multifractal_asymmetry` | Assimetria do espectro |

### ⚡ Grupo 8: Ultra Necrozma (30+ features)
| Feature | Descrição Técnica |
|---------|-------------------|
| `photon_energy_total` | Energia total do movimento |
| `photon_efficiency` | Eficiência (movimento líquido/total) |
| `wave_particle_ratio` | Razão onda/partícula |
| `z_crystal_resonance` | Ressonância do Z-Crystal |
| `crystal_symmetry` | Padrões de simetria |

---

## 📊 Output

### Estrutura de Saída

```
ultra_necrozma_results/
├── universes/           # Resultados por configuração
│   ├── universe_1m_5lb.json
│   ├── universe_5m_10lb.json
│   └── ... 
├── crystals/            # Formações de cristais
├── reports/             # Relatórios consolidados
│   ├── final_judgment_*. json
│   ├── rankings_*.json
│   ├── market_analysis_*.json
│   ├── pattern_catalog_*.json
│   ├── executive_summary_*.json
│   └── ULTRA_NECROZMA_MASTER_REPORT_*.json
└── checkpoints/         # Progresso salvo
```

### Exemplo de Output (Market Regime)

```json
{
  "regime": "STRONG_TRENDING",
  "dfa_alpha": 0.583,
  "hurst_exponent": 0.567,
  "lyapunov_exponent": 0.0234,
  "chaos_level": "MODERATE",
  "complexity": "HIGH"
}
```

### Exemplo de Recomendação

```json
{
  "primary_strategy": "AGGRESSIVE TREND-FOLLOWING",
  "confidence": "HIGH",
  "key_points": [
    "Enter on breakouts with momentum confirmation",
    "Hold positions for extended moves",
    "Use trailing stops to protect profits",
    "Optimal timeframe: 5 minute candles with 10 lookback"
  ]
}
```

---

## 🕐 Estimativa de Tempo

| Dataset | Sequencial | Paralelo (16 workers) |
|---------|------------|----------------------|
| 100K ticks | ~5 min | ~1 min |
| 1M ticks | ~30 min | ~10 min |
| 10M ticks | ~3 horas | ~45 min |
| 16M ticks | ~5 horas | ~1. 5 horas |

---

## 🔧 Requisitos de Sistema

### Mínimo
- Python 3.8+
- 8 GB RAM
- 4 cores CPU

### Recomendado
- Python 3.10+
- 32+ GB RAM
- 16+ cores CPU
- SSD para armazenamento

### Testado em
- Ubuntu 22.04 (VM)
- 100 GB RAM
- Ryzen 9 (16 cores / 32 threads)

---

## 📦 Dependências

```
numpy>=1.24.0
pandas>=2.0.0
pyarrow>=14.0.0
scipy>=1.11.0
numba>=0.58.0
psutil>=5.9.0
tqdm>=4.66.0
```

---

## 🐛 Troubleshooting

### Erro:  "CSV file not found"
```bash
# Verifique o caminho em config.py ou use:
python main.py --csv /caminho/correto/para/arquivo.csv
```

### Erro: "Out of memory"
```bash
# Reduza o número de workers: 
python main.py --workers 4

# Ou rode sequencialmente:
python main.py --sequential
```

### Numba não disponível
```bash
# Instale Numba (opcional, mas recomendado):
pip install numba
```

### Análise muito lenta
1. Verifique se Numba está instalado
2. Aumente o número de workers
3. Use SSD em vez de HDD
4. Considere reduzir `INTERVALS` ou `LOOKBACKS` em config.py

---

## 📚 Referências Técnicas

- **DFA (Detrended Fluctuation Analysis)**: Peng et al., 1994
- **Hurst Exponent**: Hurst, 1951
- **Lyapunov Exponent**: Rosenstein et al., 1993
- **Sample Entropy**: Richman & Moorman, 2000
- **Takens Embedding**: Takens, 1981
- **Multifractal DFA**: Kantelhardt et al., 2002
- **RQA**:  Marwan et al., 2007

---

## 🎮 Evolução do Projeto

```
🔥 Monster         → Análise matemática básica
🦎 Charmander      → Features aprimoradas
🔥 Charmeleon      → Padrões avançados
🐉 Charizard       → 150+ features, mega evolução
⚡ Arceus          → Poderes divinos, 300+ features
🌟 Ultra Necrozma  → Transcendência suprema, 500+ features
```

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📧 Contato

- **GitHub**: [@dans91364-create](https://github.com/dans91364-create)
- **Projeto**: [necroza](https://github.com/dans91364-create/necroza)

---

<div align="center">

### ⚡🌟💎 *"The light reveals all patterns.  Trade wisely."* 💎🌟⚡

**Ultra Necrozma - The Blinding One**

</div>