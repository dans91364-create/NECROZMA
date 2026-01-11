#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TEST MODE SAMPLER 💎🌟⚡

NECROZMA Test Mode - Amostragem Inteligente de Dados

Seleciona automaticamente semanas aleatórias espalhadas pelo ano
para testar o sistema rapidamente antes de rodar a análise completa.

Technical: Smart data sampling for quick system validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Optional


class TestModeSampler:
    """
    Seleciona amostras representativas do dataset completo.
    
    Estratégias de amostragem:
    1. RANDOM_WEEKS: N semanas aleatórias
    2. STRATIFIED: 1 semana de cada trimestre
    3. EVENT_BASED: Semanas com eventos importantes (NFP, FOMC)
    4. REGIME_DIVERSE: Semanas com diferentes regimes detectados
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize test mode sampler.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
    
    def _get_week_boundaries(self, df: pd.DataFrame) -> Dict[int, Tuple[pd.Timestamp, pd.Timestamp]]:
        """
        Get start and end timestamps for each week in the dataset.
        
        Args:
            df: DataFrame with timestamp column
            
        Returns:
            Dict mapping week number to (start_timestamp, end_timestamp)
        """
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column")
        
        df_copy = df.copy()
        df_copy['week'] = df_copy['timestamp'].dt.isocalendar().week
        df_copy['year'] = df_copy['timestamp'].dt.year
        
        weeks = {}
        for (year, week), group in df_copy.groupby(['year', 'week']):
            week_key = year * 100 + week  # Unique key: YYYYWW
            weeks[week_key] = (group['timestamp'].min(), group['timestamp'].max())
        
        return weeks
    
    def _filter_holiday_weeks(self, weeks: Dict, year: int, avoid_holidays: bool = True) -> Dict:
        """
        Filter out holiday weeks if requested.
        
        Args:
            weeks: Dict of week boundaries
            year: Year to check
            avoid_holidays: Whether to filter holidays
            
        Returns:
            Filtered weeks dict
        """
        if not avoid_holidays:
            return weeks
        
        holiday_dates = self.get_holiday_weeks(year)
        filtered_weeks = {}
        
        for week_key, (start, end) in weeks.items():
            is_holiday = False
            for holiday_str in holiday_dates:
                # Ensure timezone awareness matches
                holiday = pd.to_datetime(holiday_str)
                if start.tz is not None:
                    holiday = holiday.tz_localize('UTC')
                    
                if start <= holiday <= end:
                    is_holiday = True
                    break
            
            if not is_holiday:
                filtered_weeks[week_key] = (start, end)
        
        return filtered_weeks
    
    def _get_week_volatility(self, df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> float:
        """
        Calculate volatility for a week.
        
        Args:
            df: DataFrame with price data
            start: Week start timestamp
            end: Week end timestamp
            
        Returns:
            Volatility measure (std of pips_change)
        """
        week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        
        if 'pips_change' in week_data.columns and len(week_data) > 0:
            return week_data['pips_change'].std()
        elif 'mid_price' in week_data.columns and len(week_data) > 1:
            # Calculate volatility from mid_price
            returns = week_data['mid_price'].pct_change() * 10000  # Convert to pips
            return returns.std()
        
        return 0.0
    
    def _get_week_trend(self, df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> float:
        """
        Calculate trend strength for a week.
        
        Args:
            df: DataFrame with price data
            start: Week start timestamp
            end: Week end timestamp
            
        Returns:
            Trend measure (net movement in pips)
        """
        week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        
        if 'mid_price' in week_data.columns and len(week_data) > 1:
            start_price = week_data['mid_price'].iloc[0]
            end_price = week_data['mid_price'].iloc[-1]
            return abs(end_price - start_price) * 10000  # Convert to pips
        
        return 0.0
    
    def sample_random_weeks(self, df: pd.DataFrame, n_weeks: int = 3, 
                           avoid_holidays: bool = True) -> pd.DataFrame:
        """
        Seleciona N semanas aleatórias espalhadas pelo ano.
        
        Args:
            df: DataFrame com dados completos
            n_weeks: Número de semanas a selecionar
            avoid_holidays: Evitar semanas de feriados (Natal, Ano Novo)
        
        Returns:
            DataFrame com dados das semanas selecionadas
        """
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column")
        
        # Get all weeks
        weeks = self._get_week_boundaries(df)
        
        # Filter holidays
        year = df['timestamp'].dt.year.iloc[0]
        weeks = self._filter_holiday_weeks(weeks, year, avoid_holidays)
        
        # Check minimum tick count per week
        min_ticks = 100_000
        valid_weeks = {}
        for week_key, (start, end) in weeks.items():
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            if len(week_data) >= min_ticks:
                valid_weeks[week_key] = (start, end)
        
        if len(valid_weeks) < n_weeks:
            print(f"⚠️  Warning: Only {len(valid_weeks)} valid weeks found (requested {n_weeks})")
            n_weeks = len(valid_weeks)
        
        # Randomly select weeks
        selected_week_keys = random.sample(list(valid_weeks.keys()), n_weeks)
        
        # Extract data for selected weeks
        selected_data = []
        for week_key in sorted(selected_week_keys):
            start, end = valid_weeks[week_key]
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            selected_data.append(week_data)
        
        if selected_data:
            result = pd.concat(selected_data, ignore_index=True)
            print(f"✅ Selected {n_weeks} random weeks: {len(result):,} ticks")
            return result
        
        return pd.DataFrame()
    
    def sample_stratified(self, df: pd.DataFrame, weeks_per_quarter: int = 1) -> pd.DataFrame:
        """
        Seleciona semanas de cada trimestre para representatividade.
        
        Args:
            df: DataFrame com dados completos
            weeks_per_quarter: Semanas por trimestre
        
        Returns:
            DataFrame com dados estratificados
        """
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column")
        
        # Get all weeks
        weeks = self._get_week_boundaries(df)
        year = df['timestamp'].dt.year.iloc[0]
        weeks = self._filter_holiday_weeks(weeks, year, avoid_holidays=True)
        
        # Group weeks by quarter
        quarters = {1: [], 2: [], 3: [], 4: []}
        for week_key, (start, end) in weeks.items():
            quarter = (start.month - 1) // 3 + 1
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            if len(week_data) >= 100_000:  # Minimum ticks
                quarters[quarter].append((week_key, start, end))
        
        # Select weeks from each quarter
        selected_data = []
        for quarter, quarter_weeks in quarters.items():
            if len(quarter_weeks) == 0:
                continue
            
            n_select = min(weeks_per_quarter, len(quarter_weeks))
            selected = random.sample(quarter_weeks, n_select)
            
            for week_key, start, end in selected:
                week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
                selected_data.append(week_data)
        
        if selected_data:
            result = pd.concat(selected_data, ignore_index=True)
            print(f"✅ Selected stratified weeks: {len(result):,} ticks")
            return result
        
        return pd.DataFrame()
    
    def sample_high_volatility(self, df: pd.DataFrame, n_weeks: int = 2) -> pd.DataFrame:
        """
        Seleciona semanas de alta volatilidade (bom para testar regime VOLATILE).
        
        Args:
            df: DataFrame com dados completos
            n_weeks: Número de semanas a selecionar
            
        Returns:
            DataFrame com semanas de alta volatilidade
        """
        weeks = self._get_week_boundaries(df)
        year = df['timestamp'].dt.year.iloc[0]
        weeks = self._filter_holiday_weeks(weeks, year, avoid_holidays=True)
        
        # Calculate volatility for each week
        week_volatilities = []
        for week_key, (start, end) in weeks.items():
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            if len(week_data) >= 100_000:
                volatility = self._get_week_volatility(df, start, end)
                week_volatilities.append((week_key, start, end, volatility))
        
        # Sort by volatility (descending)
        week_volatilities.sort(key=lambda x: x[3], reverse=True)
        
        # Select top N
        selected_data = []
        for week_key, start, end, vol in week_volatilities[:n_weeks]:
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            selected_data.append(week_data)
        
        if selected_data:
            result = pd.concat(selected_data, ignore_index=True)
            print(f"✅ Selected {n_weeks} high volatility weeks: {len(result):,} ticks")
            return result
        
        return pd.DataFrame()
    
    def sample_low_volatility(self, df: pd.DataFrame, n_weeks: int = 1) -> pd.DataFrame:
        """
        Seleciona semanas de baixa volatilidade (bom para testar regime QUIET).
        
        Args:
            df: DataFrame com dados completos
            n_weeks: Número de semanas a selecionar
            
        Returns:
            DataFrame com semanas de baixa volatilidade
        """
        weeks = self._get_week_boundaries(df)
        year = df['timestamp'].dt.year.iloc[0]
        weeks = self._filter_holiday_weeks(weeks, year, avoid_holidays=True)
        
        # Calculate volatility for each week
        week_volatilities = []
        for week_key, (start, end) in weeks.items():
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            if len(week_data) >= 100_000:
                volatility = self._get_week_volatility(df, start, end)
                week_volatilities.append((week_key, start, end, volatility))
        
        # Sort by volatility (ascending)
        week_volatilities.sort(key=lambda x: x[3])
        
        # Select bottom N
        selected_data = []
        for week_key, start, end, vol in week_volatilities[:n_weeks]:
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            selected_data.append(week_data)
        
        if selected_data:
            result = pd.concat(selected_data, ignore_index=True)
            print(f"✅ Selected {n_weeks} low volatility weeks: {len(result):,} ticks")
            return result
        
        return pd.DataFrame()
    
    def sample_trending(self, df: pd.DataFrame, n_weeks: int = 1) -> pd.DataFrame:
        """
        Seleciona semanas com forte tendência.
        
        Args:
            df: DataFrame com dados completos
            n_weeks: Número de semanas a selecionar
            
        Returns:
            DataFrame com semanas de forte tendência
        """
        weeks = self._get_week_boundaries(df)
        year = df['timestamp'].dt.year.iloc[0]
        weeks = self._filter_holiday_weeks(weeks, year, avoid_holidays=True)
        
        # Calculate trend strength for each week
        week_trends = []
        for week_key, (start, end) in weeks.items():
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            if len(week_data) >= 100_000:
                trend = self._get_week_trend(df, start, end)
                week_trends.append((week_key, start, end, trend))
        
        # Sort by trend strength (descending)
        week_trends.sort(key=lambda x: x[3], reverse=True)
        
        # Select top N
        selected_data = []
        for week_key, start, end, trend in week_trends[:n_weeks]:
            week_data = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            selected_data.append(week_data)
        
        if selected_data:
            result = pd.concat(selected_data, ignore_index=True)
            print(f"✅ Selected {n_weeks} trending weeks: {len(result):,} ticks")
            return result
        
        return pd.DataFrame()
    
    def get_test_sample(self, df: pd.DataFrame, strategy: str = 'balanced', 
                       total_weeks: int = 4) -> pd.DataFrame:
        """
        Método principal - retorna amostra balanceada para teste.
        
        Strategies:
        - 'minimal': 1 semana aleatória (~10min de teste)
        - 'quick': 2 semanas aleatórias (~15-20min)
        - 'balanced': 4 semanas estratificadas (~30-45min)
        - 'thorough': 8 semanas diversas (~1-1.5h)
        
        Args:
            df: DataFrame com dados completos
            strategy: Estratégia de amostragem
            total_weeks: Total de semanas (ignorado se strategy define)
            
        Returns:
            DataFrame com amostra selecionada
        """
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 🧪 TEST MODE SAMPLER                         ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        print(f"📊 Strategy: {strategy}")
        print(f"📂 Total data: {len(df):,} ticks")
        print()
        
        if strategy == 'minimal':
            print("🔬 Minimal test - 1 week")
            result = self.sample_random_weeks(df, n_weeks=1, avoid_holidays=True)
            
        elif strategy == 'quick':
            print("⚡ Quick test - 2 random weeks")
            result = self.sample_random_weeks(df, n_weeks=2, avoid_holidays=True)
            
        elif strategy == 'balanced':
            print("⚖️  Balanced test - 1 week per quarter")
            result = self.sample_stratified(df, weeks_per_quarter=1)
            
        elif strategy == 'thorough':
            print("🔍 Thorough test - diverse regime sampling")
            # Mix of different types
            samples = []
            
            # 2 random weeks
            print("  → 2 random weeks")
            samples.append(self.sample_random_weeks(df, n_weeks=2, avoid_holidays=True))
            
            # 2 high volatility
            print("  → 2 high volatility weeks")
            samples.append(self.sample_high_volatility(df, n_weeks=2))
            
            # 2 low volatility
            print("  → 2 low volatility weeks")
            samples.append(self.sample_low_volatility(df, n_weeks=2))
            
            # 2 trending
            print("  → 2 trending weeks")
            samples.append(self.sample_trending(df, n_weeks=2))
            
            result = pd.concat([s for s in samples if len(s) > 0], ignore_index=True)
            
        else:
            print(f"⚠️  Unknown strategy '{strategy}', using balanced")
            result = self.sample_stratified(df, weeks_per_quarter=1)
        
        # Estimate test time
        if len(result) > 0:
            est_time = self.estimate_test_time(len(result))
            print(f"""
📊 SAMPLE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total ticks:      {len(result):,}
Reduction:        {len(df) / len(result):.1f}x
Estimated time:   ~{est_time:.0f} minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
        
        return result
    
    def get_holiday_weeks(self, year: int) -> List[str]:
        """
        Retorna lista de semanas a evitar (feriados).
        
        Args:
            year: Year to get holidays for
            
        Returns:
            List of holiday date strings (ISO format)
        """
        holidays = [
            f"{year}-01-01",  # Ano Novo
            f"{year}-12-25",  # Natal
            f"{year}-12-31",  # Véspera Ano Novo
            # Adicionar outros feriados importantes do calendário econômico
        ]
        return holidays
    
    def estimate_test_time(self, n_ticks: int, baseline_time_per_million: int = 45) -> float:
        """
        Estima tempo de teste baseado no número de ticks.
        
        Args:
            n_ticks: Número de ticks na amostra
            baseline_time_per_million: Minutos por milhão de ticks
        
        Returns:
            Estimativa em minutos
        """
        return (n_ticks / 1_000_000) * baseline_time_per_million


# ═══════════════════════════════════════════════════════════════
# 🎮 MAIN (Testing)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🧪 TEST MODE SAMPLER - DEMO                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate synthetic test data
    print("📊 Generating synthetic test data...")
    np.random.seed(42)
    
    n_ticks = 1_000_000
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    prices = 1.10 + np.cumsum(np.random.randn(n_ticks) * 0.00005)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "bid": prices - 0.00005,
        "ask": prices + 0.00005,
        "mid_price": prices,
        "spread_pips": 1.0,
        "pips_change": np.concatenate([[0], np.diff(prices) * 10000])
    })
    
    print(f"✅ Generated {len(df):,} ticks\n")
    
    # Test sampler
    sampler = TestModeSampler(seed=42)
    
    print("=" * 60)
    print("Test 1: Minimal strategy")
    print("=" * 60)
    sample1 = sampler.get_test_sample(df, strategy='minimal')
    
    print("\n" + "=" * 60)
    print("Test 2: Quick strategy")
    print("=" * 60)
    sample2 = sampler.get_test_sample(df, strategy='quick')
    
    print("\n" + "=" * 60)
    print("Test 3: Balanced strategy")
    print("=" * 60)
    sample3 = sampler.get_test_sample(df, strategy='balanced')
    
    print("\n✅ All tests completed!")
