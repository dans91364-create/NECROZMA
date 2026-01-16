#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - REGIME DETECTOR 💎🌟⚡

Market Regime Detection System
"Giratina reveals the hidden states of chaos"

Features:
- Unsupervised clustering (K-Means, HDBSCAN)
- Automatic optimal cluster detection
- Regime characterization
- Transition probability matrices
- Performance analysis by regime
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import warnings

warnings.filterwarnings("ignore")

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    print("⚠️  HDBSCAN not available. Install with: pip install hdbscan")

from config import REGIME_CONFIG


# ═══════════════════════════════════════════════════════════════
# 🎯 REGIME DETECTION
# ═══════════════════════════════════════════════════════════════

class RegimeDetector:
    """
    Market regime detection using unsupervised learning
    
    Usage:
        detector = RegimeDetector()
        regimes = detector.detect_regimes(features_df)
        analysis = detector.analyze_regimes(regimes_df)
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize regime detector
        
        Args:
            config: Configuration dictionary (uses REGIME_CONFIG if None)
        """
        self.config = config or REGIME_CONFIG
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_n_clusters = None
        self.regime_names = {}
        
    def _select_features(self, df: pd.DataFrame) -> List[str]:
        """
        Select relevant features for regime detection
        
        Args:
            df: Features DataFrame
            
        Returns:
            List of feature column names
        """
        # Prioritize these feature types
        priority_patterns = [
            "volatility", "atr", "volume", "spread",
            "trend", "momentum", "rsi", "macd",
            "entropy", "hurst", "dfa", "lyapunov",
            "autocorr", "variance", "std"
        ]
        
        selected = []
        
        # First pass: priority features
        for pattern in priority_patterns:
            for col in df.columns:
                if pattern in col.lower() and col not in selected:
                    selected.append(col)
        
        # If not enough features, add more
        if len(selected) < 10:
            for col in df.columns:
                if col not in selected and df[col].dtype in [np.float64, np.float32]:
                    selected.append(col)
                    if len(selected) >= 20:
                        break
        
        return selected[:30]  # Limit to 30 features
    
    def _find_optimal_clusters(self, X: np.ndarray) -> int:
        """
        Find optimal number of clusters using elbow method and silhouette
        
        Args:
            X: Scaled feature matrix
            
        Returns:
            Optimal number of clusters
        """
        n_range = self.config.get("n_clusters_range", [2, 3, 4, 5, 6])
        
        best_score = -1
        best_n = n_range[0]
        
        scores = []
        
        for n in n_range:
            if n >= len(X):
                continue
                
            kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
            # Silhouette score (higher is better)
            silhouette = silhouette_score(X, labels)
            
            # Davies-Bouldin score (lower is better, invert for comparison)
            db_score = davies_bouldin_score(X, labels)
            
            # Combined score
            combined_score = silhouette - (db_score / 10.0)
            
            scores.append({
                "n_clusters": n,
                "silhouette": silhouette,
                "davies_bouldin": db_score,
                "combined": combined_score,
            })
            
            if combined_score > best_score:
                best_score = combined_score
                best_n = n
        
        print(f"\n   Cluster evaluation:")
        for s in scores:
            marker = "👑" if s["n_clusters"] == best_n else "  "
            print(f"   {marker} {s['n_clusters']} clusters: "
                  f"Silhouette={s['silhouette']:.3f}, "
                  f"DB={s['davies_bouldin']:.3f}, "
                  f"Combined={s['combined']:.3f}")
        
        return best_n
    
    def detect_regimes_kmeans(self, df: pd.DataFrame, 
                             feature_cols: List[str] = None) -> pd.DataFrame:
        """
        Detect regimes using K-Means clustering
        
        Args:
            df: DataFrame with features
            feature_cols: List of feature columns (auto-select if None)
            
        Returns:
            DataFrame with added 'regime' column
        """
        print("🔵 Detecting regimes with K-Means...")
        
        # Select features
        if feature_cols is None:
            feature_cols = self._select_features(df)
        
        print(f"   Using {len(feature_cols)} features")
        
        # Prepare data
        X = df[feature_cols].fillna(0).values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Find optimal clusters
        n_clusters = self._find_optimal_clusters(X_scaled)
        self.best_n_clusters = n_clusters
        
        print(f"\n   📊 Selected {n_clusters} clusters (regimes)")
        
        # Fit final model
        self.best_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = self.best_model.fit_predict(X_scaled)
        
        # Add to dataframe
        result_df = df.copy()
        result_df["regime"] = labels
        
        return result_df
    
    def detect_regimes_hdbscan(self, df: pd.DataFrame,
                               feature_cols: List[str] = None) -> pd.DataFrame:
        """
        Detect regimes using HDBSCAN (density-based)
        
        Args:
            df: DataFrame with features
            feature_cols: List of feature columns (auto-select if None)
            
        Returns:
            DataFrame with added 'regime' column
        """
        if not HDBSCAN_AVAILABLE:
            print("⚠️  HDBSCAN not available, falling back to K-Means")
            return self.detect_regimes_kmeans(df, feature_cols)
        
        print("🟣 Detecting regimes with HDBSCAN...")
        
        # Select features
        if feature_cols is None:
            feature_cols = self._select_features(df)
        
        print(f"   Using {len(feature_cols)} features")
        
        # Prepare data
        X = df[feature_cols].fillna(0).values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit HDBSCAN with dynamic min_cluster_size
        config_min_size = self.config.get("min_cluster_size", 100)
        # Dynamic: at least 1% of data or 10,000 points, whichever is larger
        min_cluster_size = max(10000, int(len(df) * 0.01), config_min_size)
        print(f"   Using min_cluster_size={min_cluster_size:,} (1% of {len(df):,} rows)")
        
        print(f"   🔄 Processing HDBSCAN clustering on {len(df):,} samples...")
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=10,
            metric='euclidean'
        )
        
        labels = clusterer.fit_predict(X_scaled)
        print(f"   ✅ HDBSCAN clustering complete")
        
        # Count clusters (excluding noise label -1)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = (labels == -1).sum()
        
        print(f"\n   📊 Found {n_clusters} regimes ({n_noise:,} noise points)")
        
        self.best_model = clusterer
        self.best_n_clusters = n_clusters
        
        # Add to dataframe
        result_df = df.copy()
        result_df["regime"] = labels
        
        return result_df
    
    def detect_regimes(self, df: pd.DataFrame, 
                       method: str = "auto",
                       feature_cols: List[str] = None) -> pd.DataFrame:
        """
        Detect market regimes
        
        Args:
            df: DataFrame with features
            method: "kmeans", "hdbscan", or "auto"
            feature_cols: List of feature columns (auto-select if None)
            
        Returns:
            DataFrame with added 'regime' column
        """
        if method == "auto":
            method = "hdbscan" if HDBSCAN_AVAILABLE else "kmeans"
        
        if method == "hdbscan":
            return self.detect_regimes_hdbscan(df, feature_cols)
        else:
            return self.detect_regimes_kmeans(df, feature_cols)
    
    def characterize_regimes(self, df: pd.DataFrame,
                            feature_cols: List[str] = None) -> Dict:
        """
        Characterize each regime by analyzing feature distributions
        
        Args:
            df: DataFrame with 'regime' column
            feature_cols: Features to use for characterization
            
        Returns:
            Dictionary with regime characteristics
        """
        if "regime" not in df.columns:
            raise ValueError("DataFrame must have 'regime' column")
        
        if feature_cols is None:
            feature_cols = self._select_features(df)
        
        # Key features for characterization
        key_features = []
        for pattern in ["volatility", "trend", "volume", "momentum", "entropy"]:
            for col in feature_cols:
                if pattern in col.lower():
                    key_features.append(col)
                    break
        
        if not key_features:
            key_features = feature_cols[:5]
        
        characteristics = {}
        
        for regime_id in sorted(df["regime"].unique()):
            if regime_id == -1:  # Skip noise
                continue
            
            regime_data = df[df["regime"] == regime_id]
            
            # Calculate statistics for key features
            stats = {}
            for feature in key_features:
                if feature in regime_data.columns:
                    stats[feature] = {
                        "mean": regime_data[feature].mean(),
                        "std": regime_data[feature].std(),
                        "median": regime_data[feature].median(),
                    }
            
            # Try to name the regime
            name = self._name_regime(stats, key_features)
            self.regime_names[regime_id] = name
            
            characteristics[regime_id] = {
                "name": name,
                "size": len(regime_data),
                "percentage": len(regime_data) / len(df) * 100,
                "statistics": stats,
            }
        
        return characteristics
    
    def _name_regime(self, stats: Dict, features: List[str]) -> str:
        """Generate a descriptive name for a regime"""
        # Look for volatility indicators
        vol_features = [f for f in features if "volatility" in f.lower() or "atr" in f.lower()]
        trend_features = [f for f in features if "trend" in f.lower() or "momentum" in f.lower()]
        
        vol_level = "UNKNOWN"
        trend_level = "RANGING"
        
        if vol_features and vol_features[0] in stats:
            vol_mean = stats[vol_features[0]]["mean"]
            if vol_mean > 0.8:
                vol_level = "HIGH_VOL"
            elif vol_mean > 0.4:
                vol_level = "MEDIUM_VOL"
            else:
                vol_level = "LOW_VOL"
        
        if trend_features and trend_features[0] in stats:
            trend_mean = abs(stats[trend_features[0]]["mean"])
            if trend_mean > 0.6:
                trend_level = "TRENDING"
            elif trend_mean > 0.3:
                trend_level = "WEAK_TREND"
            else:
                trend_level = "RANGING"
        
        return f"{trend_level}_{vol_level}"
    
    def calculate_transitions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate regime transition probability matrix
        
        Args:
            df: DataFrame with 'regime' column
            
        Returns:
            Transition probability DataFrame
        """
        if "regime" not in df.columns:
            raise ValueError("DataFrame must have 'regime' column")
        
        regimes = df["regime"].values
        unique_regimes = sorted([r for r in df["regime"].unique() if r != -1])
        
        # Count transitions
        transition_counts = np.zeros((len(unique_regimes), len(unique_regimes)))
        
        for i in range(len(regimes) - 1):
            current = regimes[i]
            next_regime = regimes[i + 1]
            
            if current == -1 or next_regime == -1:
                continue
            
            current_idx = unique_regimes.index(current)
            next_idx = unique_regimes.index(next_regime)
            
            transition_counts[current_idx, next_idx] += 1
        
        # Convert to probabilities
        transition_probs = np.zeros_like(transition_counts)
        for i in range(len(unique_regimes)):
            row_sum = transition_counts[i].sum()
            if row_sum > 0:
                transition_probs[i] = transition_counts[i] / row_sum
        
        # Create DataFrame
        regime_labels = [self.regime_names.get(r, f"Regime_{r}") for r in unique_regimes]
        
        transition_df = pd.DataFrame(
            transition_probs,
            index=regime_labels,
            columns=regime_labels
        )
        
        return transition_df
    
    def analyze_regimes(self, df: pd.DataFrame) -> Dict:
        """
        Complete regime analysis
        
        Args:
            df: DataFrame with 'regime' column
            
        Returns:
            Dictionary with full analysis
        """
        print("\n🔍 Analyzing regimes...")
        
        characteristics = self.characterize_regimes(df)
        transitions = self.calculate_transitions(df)
        
        print("\n📊 Regime Summary:")
        for regime_id, char in characteristics.items():
            print(f"\n   {char['name']} (Regime {regime_id}):")
            print(f"      Size: {char['size']:,} ({char['percentage']:.1f}%)")
        
        print("\n🔄 Transition Matrix:")
        print(transitions.round(3))
        
        return {
            "characteristics": characteristics,
            "transitions": transitions,
            "n_regimes": len(characteristics),
        }


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🔮 REGIME DETECTOR TEST 🔮                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data with distinct regimes
    print("📊 Generating test data with 3 synthetic regimes...")
    np.random.seed(42)
    
    n_per_regime = 1000
    
    # Regime 1: Low vol, ranging
    regime1 = pd.DataFrame({
        "volatility": np.random.uniform(0.1, 0.3, n_per_regime),
        "trend": np.random.uniform(-0.2, 0.2, n_per_regime),
        "momentum": np.random.uniform(-0.1, 0.1, n_per_regime),
        "volume": np.random.uniform(0.5, 1.0, n_per_regime),
    })
    
    # Regime 2: High vol, trending up
    regime2 = pd.DataFrame({
        "volatility": np.random.uniform(0.7, 1.0, n_per_regime),
        "trend": np.random.uniform(0.5, 1.0, n_per_regime),
        "momentum": np.random.uniform(0.4, 0.9, n_per_regime),
        "volume": np.random.uniform(1.5, 2.5, n_per_regime),
    })
    
    # Regime 3: Medium vol, trending down
    regime3 = pd.DataFrame({
        "volatility": np.random.uniform(0.4, 0.6, n_per_regime),
        "trend": np.random.uniform(-1.0, -0.5, n_per_regime),
        "momentum": np.random.uniform(-0.9, -0.4, n_per_regime),
        "volume": np.random.uniform(1.0, 1.5, n_per_regime),
    })
    
    # Combine
    df = pd.concat([regime1, regime2, regime3], ignore_index=True)
    
    print(f"   Generated {len(df):,} samples")
    print()
    
    # Test regime detection
    detector = RegimeDetector()
    
    # K-Means
    print("=" * 60)
    regimes_df = detector.detect_regimes(df, method="kmeans")
    analysis = detector.analyze_regimes(regimes_df)
    
    # HDBSCAN
    if HDBSCAN_AVAILABLE:
        print("\n" + "=" * 60)
        detector2 = RegimeDetector()
        regimes_df2 = detector2.detect_regimes(df, method="hdbscan")
        analysis2 = detector2.analyze_regimes(regimes_df2)
    
    print("\n✅ Regime detection test complete!")
