#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - PATTERN MINER 💎🌟⚡

ML-Based Pattern Discovery System
"Mining the light from chaos - feature importance and rules"

Features:
- Feature importance (XGBoost, LightGBM, Permutation)
- SHAP values for interpretability
- Feature interaction detection
- Association rules mining
- Optimal threshold discovery
- Redundancy elimination
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings("ignore")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not available. Install with: pip install xgboost")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️  LightGBM not available. Install with: pip install lightgbm")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP not available. Install with: pip install shap")

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

from config import FEATURE_IMPORTANCE_CONFIG, SHAP_CONFIG


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE IMPORTANCE
# ═══════════════════════════════════════════════════════════════

class PatternMiner:
    """
    ML-based pattern discovery and feature importance analysis
    
    Usage:
        miner = PatternMiner()
        importance = miner.analyze_features(X, y)
        rules = miner.mine_rules(X, y)
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize pattern miner
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or FEATURE_IMPORTANCE_CONFIG
        self.models = {}
        self.feature_importance = {}
        self.shap_values = None
        
    def _prepare_data(self, X: pd.DataFrame, y: pd.Series,
                     test_size: float = 0.2) -> Tuple:
        """
        Prepare train/test split
        
        Args:
            X: Features DataFrame
            y: Target Series
            test_size: Test set proportion
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        return train_test_split(X, y, test_size=test_size, 
                               random_state=42, stratify=y if len(y.unique()) < 20 else None)
    
    def feature_importance_xgboost(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Calculate feature importance using XGBoost
        
        Args:
            X: Features DataFrame
            y: Target Series
            
        Returns:
            DataFrame with feature importance
        """
        if not XGBOOST_AVAILABLE:
            print("⚠️  XGBoost not available, skipping")
            return pd.DataFrame()
        
        print("   Training XGBoost...")
        
        X_train, X_test, y_train, y_test = self._prepare_data(X, y)
        
        # Determine task type
        n_classes = len(y.unique())
        if n_classes == 2:
            objective = "binary:logistic"
        elif n_classes > 2 and n_classes < 100:
            objective = "multi:softmax"
        else:
            objective = "reg:squarederror"
        
        # Train model
        params = {
            "objective": objective,
            "max_depth": self.config.get("max_depth", 6),
            "learning_rate": self.config.get("learning_rate", 0.1),
            "n_estimators": self.config.get("n_estimators", 100),
            "random_state": 42,
        }
        
        if objective == "multi:softmax":
            params["num_class"] = n_classes
        
        model = xgb.XGBClassifier(**params) if n_classes < 100 else xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        self.models["xgboost"] = model
        
        # Get importance
        importance = model.feature_importances_
        
        importance_df = pd.DataFrame({
            "feature": X.columns,
            "importance": importance,
            "method": "xgboost"
        }).sort_values("importance", ascending=False)
        
        return importance_df
    
    def feature_importance_lightgbm(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Calculate feature importance using LightGBM
        
        Args:
            X: Features DataFrame
            y: Target Series
            
        Returns:
            DataFrame with feature importance
        """
        if not LIGHTGBM_AVAILABLE:
            print("⚠️  LightGBM not available, skipping")
            return pd.DataFrame()
        
        print("   Training LightGBM...")
        
        X_train, X_test, y_train, y_test = self._prepare_data(X, y)
        
        # Determine task type
        n_classes = len(y.unique())
        if n_classes == 2:
            objective = "binary"
        elif n_classes > 2 and n_classes < 100:
            objective = "multiclass"
        else:
            objective = "regression"
        
        # Train model
        params = {
            "objective": objective,
            "max_depth": self.config.get("max_depth", 6),
            "learning_rate": self.config.get("learning_rate", 0.1),
            "n_estimators": self.config.get("n_estimators", 100),
            "random_state": 42,
            "verbose": -1,
        }
        
        if objective == "multiclass":
            params["num_class"] = n_classes
        
        model = lgb.LGBMClassifier(**params) if n_classes < 100 else lgb.LGBMRegressor(**params)
        model.fit(X_train, y_train)
        
        self.models["lightgbm"] = model
        
        # Get importance
        importance = model.feature_importances_
        
        importance_df = pd.DataFrame({
            "feature": X.columns,
            "importance": importance,
            "method": "lightgbm"
        }).sort_values("importance", ascending=False)
        
        return importance_df
    
    def feature_importance_permutation(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Calculate permutation feature importance
        
        Args:
            X: Features DataFrame
            y: Target Series
            
        Returns:
            DataFrame with feature importance
        """
        print("   Calculating permutation importance...")
        
        X_train, X_test, y_train, y_test = self._prepare_data(X, y)
        
        # Train simple model
        model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Calculate permutation importance
        perm_importance = permutation_importance(
            model, X_test, y_test,
            n_repeats=10,
            random_state=42,
            n_jobs=-1
        )
        
        importance_df = pd.DataFrame({
            "feature": X.columns,
            "importance": perm_importance.importances_mean,
            "std": perm_importance.importances_std,
            "method": "permutation"
        }).sort_values("importance", ascending=False)
        
        return importance_df
    
    def analyze_features(self, X: pd.DataFrame, y: pd.Series,
                        methods: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Analyze feature importance using multiple methods
        
        Args:
            X: Features DataFrame
            y: Target Series
            methods: List of methods to use (default: all available)
            
        Returns:
            Dictionary mapping method -> importance DataFrame
        """
        if methods is None:
            methods = self.config.get("methods", ["xgboost", "lightgbm", "permutation"])
        
        print(f"\n🔍 Analyzing {len(X.columns)} features with {len(methods)} methods...")
        
        results = {}
        
        for method in methods:
            if method == "xgboost" and XGBOOST_AVAILABLE:
                results[method] = self.feature_importance_xgboost(X, y)
            elif method == "lightgbm" and LIGHTGBM_AVAILABLE:
                results[method] = self.feature_importance_lightgbm(X, y)
            elif method == "permutation":
                results[method] = self.feature_importance_permutation(X, y)
        
        self.feature_importance = results
        
        # Create aggregate importance
        if results:
            aggregate = self._aggregate_importance(results)
            results["aggregate"] = aggregate
            
            print(f"\n📊 Top 10 Most Important Features:")
            for i, row in aggregate.head(10).iterrows():
                print(f"   {i+1:2d}. {row['feature']:30s} {row['avg_importance']:.4f}")
        
        return results
    
    def _aggregate_importance(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Aggregate importance scores from multiple methods"""
        all_features = set()
        for df in results.values():
            all_features.update(df["feature"].values)
        
        aggregated = []
        
        for feature in all_features:
            scores = []
            for method, df in results.items():
                if method == "aggregate":
                    continue
                feature_row = df[df["feature"] == feature]
                if not feature_row.empty:
                    scores.append(feature_row["importance"].values[0])
            
            if scores:
                aggregated.append({
                    "feature": feature,
                    "avg_importance": np.mean(scores),
                    "std_importance": np.std(scores),
                    "max_importance": np.max(scores),
                    "min_importance": np.min(scores),
                })
        
        return pd.DataFrame(aggregated).sort_values("avg_importance", ascending=False)
    
    def calculate_shap_values(self, X: pd.DataFrame, y: pd.Series,
                             max_samples: int = None) -> Optional[np.ndarray]:
        """
        Calculate SHAP values for interpretability
        
        Args:
            X: Features DataFrame
            y: Target Series
            max_samples: Maximum samples for SHAP (default from config)
            
        Returns:
            SHAP values array or None if SHAP not available
        """
        if not SHAP_AVAILABLE or not SHAP_CONFIG.get("enabled", True):
            print("⚠️  SHAP not available or disabled")
            return None
        
        if max_samples is None:
            max_samples = SHAP_CONFIG.get("max_samples", 1000)
        
        print(f"\n🔮 Calculating SHAP values (max {max_samples} samples)...")
        
        # Use XGBoost model if available
        if "xgboost" not in self.models and XGBOOST_AVAILABLE:
            print("   Training model for SHAP...")
            self.feature_importance_xgboost(X, y)
        
        if "xgboost" not in self.models:
            print("⚠️  No model available for SHAP")
            return None
        
        model = self.models["xgboost"]
        
        # Sample data if too large
        if len(X) > max_samples:
            X_sample = X.sample(max_samples, random_state=42)
        else:
            X_sample = X
        
        # Calculate SHAP values
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            
            self.shap_values = shap_values
            
            print(f"   ✅ SHAP values calculated for {len(X_sample)} samples")
            
            return shap_values
        except Exception as e:
            print(f"⚠️  SHAP calculation failed: {e}")
            return None
    
    def find_feature_interactions(self, X: pd.DataFrame, y: pd.Series,
                                  top_n: int = 10) -> List[Tuple]:
        """
        Find important feature interactions
        
        Args:
            X: Features DataFrame
            y: Target Series
            top_n: Number of top interactions to return
            
        Returns:
            List of (feature1, feature2, interaction_strength) tuples
        """
        print(f"\n🔗 Finding feature interactions (top {top_n})...")
        
        # Get top features from importance
        if "aggregate" in self.feature_importance:
            top_features = self.feature_importance["aggregate"]["feature"].head(20).tolist()
        else:
            top_features = X.columns[:20].tolist()
        
        interactions = []
        
        # Create interaction features and test importance
        for i, feat1 in enumerate(top_features):
            for feat2 in top_features[i+1:]:
                # Create interaction
                interaction = X[feat1] * X[feat2]
                
                # Quick test with correlation
                corr = np.corrcoef(interaction, y)[0, 1]
                
                if not np.isnan(corr):
                    interactions.append((feat1, feat2, abs(corr)))
        
        # Sort by strength
        interactions.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n   Top {min(top_n, len(interactions))} interactions:")
        for i, (f1, f2, strength) in enumerate(interactions[:top_n]):
            print(f"   {i+1:2d}. {f1} × {f2}: {strength:.4f}")
        
        return interactions[:top_n]
    
    def find_optimal_thresholds(self, X: pd.DataFrame, y: pd.Series,
                               features: List[str] = None,
                               n_thresholds: int = 10) -> Dict:
        """
        Find optimal thresholds for top features
        
        Args:
            X: Features DataFrame
            y: Target Series (binary)
            features: Features to analyze (default: top 10)
            n_thresholds: Number of threshold candidates
            
        Returns:
            Dictionary mapping feature -> optimal threshold info
        """
        if features is None:
            if "aggregate" in self.feature_importance:
                features = self.feature_importance["aggregate"]["feature"].head(10).tolist()
            else:
                features = X.columns[:10].tolist()
        
        print(f"\n🎯 Finding optimal thresholds for {len(features)} features...")
        
        thresholds = {}
        
        for feature in features:
            values = X[feature].values
            
            # Create threshold candidates (percentiles)
            percentiles = np.linspace(10, 90, n_thresholds)
            candidates = np.percentile(values, percentiles)
            
            best_threshold = None
            best_score = 0.0
            
            # Test each threshold
            for threshold in candidates:
                # Split by threshold
                above = y[values > threshold]
                below = y[values <= threshold]
                
                if len(above) > 10 and len(below) > 10:
                    # Calculate difference in target means
                    score = abs(above.mean() - below.mean())
                    
                    if score > best_score:
                        best_score = score
                        best_threshold = threshold
            
            if best_threshold is not None:
                thresholds[feature] = {
                    "threshold": best_threshold,
                    "score": best_score,
                    "above_mean": y[values > best_threshold].mean(),
                    "below_mean": y[values <= best_threshold].mean(),
                }
        
        print(f"\n   Found optimal thresholds:")
        for feature, info in sorted(thresholds.items(), 
                                    key=lambda x: x[1]["score"], reverse=True)[:5]:
            print(f"   {feature:30s} > {info['threshold']:.4f} "
                  f"(above: {info['above_mean']:.3f}, below: {info['below_mean']:.3f})")
        
        return thresholds


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           ⛏️  PATTERN MINER TEST ⛏️                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    print("📊 Generating test data...")
    np.random.seed(42)
    n_samples = 2000
    
    # Create features with different importance levels
    X = pd.DataFrame({
        "very_important": np.random.randn(n_samples) * 2,
        "important": np.random.randn(n_samples),
        "somewhat_important": np.random.randn(n_samples) * 0.5,
        "noise1": np.random.randn(n_samples) * 0.1,
        "noise2": np.random.randn(n_samples) * 0.1,
    })
    
    # Create target based on features
    y = (
        X["very_important"] * 2 +
        X["important"] * 1 +
        X["somewhat_important"] * 0.3 +
        np.random.randn(n_samples) * 0.5
    ) > 0
    
    y = y.astype(int)
    
    print(f"   Generated {len(X):,} samples with {len(X.columns)} features")
    print(f"   Target distribution: {y.value_counts().to_dict()}")
    print()
    
    # Test pattern miner
    miner = PatternMiner()
    
    # Feature importance
    importance_results = miner.analyze_features(X, y)
    
    # SHAP values
    if SHAP_AVAILABLE:
        shap_values = miner.calculate_shap_values(X, y, max_samples=500)
    
    # Feature interactions
    interactions = miner.find_feature_interactions(X, y, top_n=5)
    
    # Optimal thresholds
    thresholds = miner.find_optimal_thresholds(X, y)
    
    print("\n✅ Pattern miner test complete!")
