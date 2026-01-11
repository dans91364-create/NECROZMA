#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - RESULT CONSOLIDATOR 💎🌟⚡

Result Consolidation: Merge partial results into final output
"Converging infinite dimensions into unified light"

Technical: Merge and aggregate partial analysis results
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 💎 RESULT CONSOLIDATOR CLASS
# ═══════════════════════════════════════════════════════════════

class ResultConsolidator:
    """
    Merge partial results into final output
    
    Technical: Aggregate and deduplicate analysis results
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize ResultConsolidator
        
        Args:
            output_dir: Directory to save consolidated results
        """
        self.output_dir = output_dir or Path("ultra_necrozma_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def merge_universe_results(
        self,
        universe_results_dir: Path
    ) -> pd.DataFrame:
        """
        Merge all universe_XX.parquet files
        Apply global ranking
        Generate final dashboard
        
        Args:
            universe_results_dir: Directory containing universe result files
        
        Returns:
            DataFrame: Merged and ranked results
        """
        print(f"\n🌌 Merging universe results from {universe_results_dir}")
        print("─" * 60)
        
        # Find all universe result files
        universe_files = sorted(universe_results_dir.glob("universe_*.parquet"))
        
        if not universe_files:
            print("   ⚠️  No universe result files found")
            return pd.DataFrame()
        
        print(f"   Found {len(universe_files)} universe files")
        
        # Load and merge
        all_results = []
        
        for universe_file in universe_files:
            try:
                df = pd.read_parquet(universe_file)
                
                # Add source info
                df['source_file'] = universe_file.name
                df['universe'] = universe_file.stem
                
                all_results.append(df)
                
                print(f"   ✅ Loaded {universe_file.name}: {len(df):,} patterns")
            except Exception as e:
                print(f"   ❌ Error loading {universe_file.name}: {e}")
        
        if not all_results:
            print("   ⚠️  No results loaded")
            return pd.DataFrame()
        
        # Concatenate all results
        merged_df = pd.concat(all_results, ignore_index=True)
        
        print(f"\n   📊 Total patterns: {len(merged_df):,}")
        
        # Apply global ranking
        print(f"   🏆 Applying global ranking...")
        merged_df = self._apply_global_ranking(merged_df)
        
        # Save merged results
        output_file = self.output_dir / "final_patterns.parquet"
        merged_df.to_parquet(output_file, compression='snappy')
        
        print(f"   ✅ Saved to: {output_file}")
        
        return merged_df
    
    def merge_chunk_results(
        self,
        chunk_results_dir: Path
    ) -> pd.DataFrame:
        """
        Merge all chunk_XX.parquet files
        Handle duplicate patterns across chunks
        Aggregate statistics
        
        Args:
            chunk_results_dir: Directory containing chunk result files
        
        Returns:
            DataFrame: Merged results
        """
        print(f"\n📦 Merging chunk results from {chunk_results_dir}")
        print("─" * 60)
        
        # Find all chunk result files
        chunk_files = sorted(chunk_results_dir.glob("chunk_*.parquet"))
        
        if not chunk_files:
            print("   ⚠️  No chunk result files found")
            return pd.DataFrame()
        
        print(f"   Found {len(chunk_files)} chunk files")
        
        # Load and merge
        all_results = []
        
        for chunk_file in chunk_files:
            try:
                df = pd.read_parquet(chunk_file)
                
                # Add source info
                df['source_file'] = chunk_file.name
                df['chunk'] = chunk_file.stem
                
                all_results.append(df)
                
                print(f"   ✅ Loaded {chunk_file.name}: {len(df):,} patterns")
            except Exception as e:
                print(f"   ❌ Error loading {chunk_file.name}: {e}")
        
        if not all_results:
            print("   ⚠️  No results loaded")
            return pd.DataFrame()
        
        # Concatenate all results
        merged_df = pd.concat(all_results, ignore_index=True)
        
        print(f"\n   📊 Total patterns before dedup: {len(merged_df):,}")
        
        # Handle duplicates
        if 'pattern_signature' in merged_df.columns:
            print(f"   🔍 Deduplicating patterns...")
            merged_df = self._deduplicate_patterns(merged_df)
            print(f"   📊 Total patterns after dedup: {len(merged_df):,}")
        
        # Save merged results
        output_file = self.output_dir / "final_patterns_chunked.parquet"
        merged_df.to_parquet(output_file, compression='snappy')
        
        print(f"   ✅ Saved to: {output_file}")
        
        return merged_df
    
    def generate_final_report(
        self,
        merged_results: pd.DataFrame,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Create comprehensive report
        
        Args:
            merged_results: Merged results DataFrame
            metadata: Additional metadata
        
        Returns:
            Path: Report file path
        """
        print(f"\n📝 Generating final report...")
        print("─" * 60)
        
        report_lines = []
        
        # Header
        report_lines.append("═" * 80)
        report_lines.append("⚡🌟💎 ULTRA NECROZMA - FINAL ANALYSIS REPORT 💎🌟⚡")
        report_lines.append("═" * 80)
        report_lines.append("")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall statistics
        report_lines.append("─" * 80)
        report_lines.append("📊 OVERALL STATISTICS")
        report_lines.append("─" * 80)
        report_lines.append(f"Total patterns: {len(merged_results):,}")
        
        if 'universe' in merged_results.columns:
            n_universes = merged_results['universe'].nunique()
            report_lines.append(f"Universes analyzed: {n_universes}")
        
        if 'chunk' in merged_results.columns:
            n_chunks = merged_results['chunk'].nunique()
            report_lines.append(f"Chunks processed: {n_chunks}")
        
        report_lines.append("")
        
        # Top patterns
        if len(merged_results) > 0:
            report_lines.append("─" * 80)
            report_lines.append("🏆 TOP PATTERNS")
            report_lines.append("─" * 80)
            
            # Get top patterns by score/rank
            top_n = min(20, len(merged_results))
            
            if 'global_rank' in merged_results.columns:
                top_patterns = merged_results.nsmallest(top_n, 'global_rank')
            elif 'score' in merged_results.columns:
                top_patterns = merged_results.nlargest(top_n, 'score')
            else:
                top_patterns = merged_results.head(top_n)
            
            for i, (idx, row) in enumerate(top_patterns.iterrows(), 1):
                pattern_info = f"{i:2d}. "
                
                if 'pattern_signature' in row:
                    pattern_info += f"{row['pattern_signature'][:50]:50s}"
                
                if 'count' in row:
                    pattern_info += f" | Count: {row['count']:>6,}"
                
                if 'score' in row:
                    pattern_info += f" | Score: {row['score']:>8.2f}"
                
                report_lines.append(pattern_info)
            
            report_lines.append("")
        
        # Per-universe performance (if available)
        if 'universe' in merged_results.columns:
            report_lines.append("─" * 80)
            report_lines.append("🌌 PER-UNIVERSE PERFORMANCE")
            report_lines.append("─" * 80)
            
            universe_stats = merged_results.groupby('universe').agg({
                'universe': 'count'
            }).rename(columns={'universe': 'pattern_count'})
            
            universe_stats = universe_stats.sort_values('pattern_count', ascending=False)
            
            for universe, stats in universe_stats.head(10).iterrows():
                report_lines.append(f"{universe:30s} | Patterns: {stats['pattern_count']:>8,}")
            
            report_lines.append("")
        
        # Metadata
        if metadata:
            report_lines.append("─" * 80)
            report_lines.append("ℹ️  METADATA")
            report_lines.append("─" * 80)
            
            for key, value in metadata.items():
                report_lines.append(f"{key}: {value}")
            
            report_lines.append("")
        
        report_lines.append("═" * 80)
        report_lines.append("✨ ULTRA NECROZMA - Analysis Complete ✨")
        report_lines.append("═" * 80)
        
        # Save report
        report_file = self.output_dir / "performance_report.md"
        
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"   ✅ Report saved to: {report_file}")
        
        # Also save as JSON
        json_report = {
            "generated_at": datetime.now().isoformat(),
            "total_patterns": len(merged_results),
            "metadata": metadata or {}
        }
        
        json_file = self.output_dir / "performance_report.json"
        with open(json_file, 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        
        return report_file
    
    def _apply_global_ranking(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply global ranking to patterns
        
        Args:
            df: DataFrame with patterns
        
        Returns:
            DataFrame: Ranked patterns
        """
        # Calculate composite score
        score_components = []
        
        if 'count' in df.columns:
            score_components.append(df['count'].fillna(0))
        
        if 'confidence' in df.columns:
            score_components.append(df['confidence'].fillna(0) * 10)
        
        if score_components:
            df['composite_score'] = sum(score_components)
        else:
            df['composite_score'] = 1.0
        
        # Rank by composite score
        df['global_rank'] = df['composite_score'].rank(ascending=False, method='dense')
        
        return df.sort_values('global_rank')
    
    def _deduplicate_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicate patterns across chunks
        
        Args:
            df: DataFrame with potentially duplicate patterns
        
        Returns:
            DataFrame: Deduplicated patterns
        """
        if 'pattern_signature' not in df.columns:
            return df
        
        # Group by pattern signature and aggregate
        agg_dict = {}
        
        if 'count' in df.columns:
            agg_dict['count'] = 'sum'
        
        if 'confidence' in df.columns:
            agg_dict['confidence'] = 'mean'
        
        # Keep first occurrence of other columns
        for col in df.columns:
            if col not in ['pattern_signature', 'count', 'confidence', 'source_file', 'chunk']:
                agg_dict[col] = 'first'
        
        if not agg_dict:
            # Just drop duplicates
            return df.drop_duplicates(subset=['pattern_signature'], keep='first')
        
        # Aggregate
        dedup_df = df.groupby('pattern_signature', as_index=False).agg(agg_dict)
        
        return dedup_df


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ⚡ RESULT CONSOLIDATOR TEST ⚡                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create test data
    test_dir = Path("/tmp/necrozma_consolidator_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    universe_dir = test_dir / "universes"
    universe_dir.mkdir(exist_ok=True)
    
    # Create sample universe results
    print("📊 Creating test universe results...")
    
    for i in range(1, 4):
        df = pd.DataFrame({
            'pattern_signature': [f'pattern_{j}' for j in range(10)],
            'count': np.random.randint(1, 100, 10),
            'confidence': np.random.uniform(0.5, 1.0, 10)
        })
        
        output_file = universe_dir / f"universe_{i:02d}.parquet"
        df.to_parquet(output_file, compression='snappy')
        
        print(f"   ✅ Created {output_file.name}")
    
    # Test consolidator
    print("\n🔧 Testing consolidator...")
    consolidator = ResultConsolidator(output_dir=test_dir / "final")
    
    # Merge universe results
    merged = consolidator.merge_universe_results(universe_dir)
    print(f"\n   Total merged patterns: {len(merged):,}")
    
    # Generate report
    report_file = consolidator.generate_final_report(
        merged,
        metadata={
            "test": True,
            "universes": 3,
            "patterns_per_universe": 10
        }
    )
    
    print(f"\n   Report: {report_file}")
    
    print("\n✅ All tests passed!")
