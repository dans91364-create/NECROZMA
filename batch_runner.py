#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BATCH RUNNER ORCHESTRATOR 💎🌟⚡

Main orchestrator for batch processing strategy backtests
Divides strategies into batches and runs each in isolated subprocess

Features:
- Batch processing with subprocess isolation
- Memory cleanup between batches
- Progress tracking with time and RAM usage
- Failed batch handling
- Result merging
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple
import pandas as pd
import psutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import StrategyFactory
from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS, OUTPUT_DIR, PARQUET_FILE


class BatchRunner:
    """Orchestrator for batch processing strategy backtests"""
    
    def __init__(self, batch_size: int = 200, parquet_file: Path = None, skip_existing: bool = True, force_rerun: bool = False):
        """
        Initialize batch runner
        
        Args:
            batch_size: Number of strategies per batch (default: 200)
            parquet_file: Path to data parquet file (default: from config)
            skip_existing: Skip batches with existing results (default: True)
            force_rerun: Force rerun all batches, ignore cache (default: False)
        """
        self.batch_size = batch_size
        self.parquet_file = parquet_file or PARQUET_FILE
        self.output_dir = OUTPUT_DIR / "batch_results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.skip_existing = skip_existing and not force_rerun  # force_rerun overrides skip_existing
        self.force_rerun = force_rerun
        
        # Track batches
        self.total_strategies = 0
        self.num_batches = 0
        self.batch_files = []
        self.failed_batches = []
        self.cached_batches = []  # Track which batches were loaded from cache
    
    def calculate_batches(self) -> List[Tuple[int, int]]:
        """
        Calculate batch ranges based on total strategies
        
        Returns:
            List of (start_idx, end_idx) tuples
        """
        # Generate all strategies to get count
        print(f"\n🔍 Calculating total strategies...")
        factory = StrategyFactory(
            templates=STRATEGY_TEMPLATES,
            params=STRATEGY_PARAMS
        )
        all_strategies = factory.generate_strategies()
        self.total_strategies = len(all_strategies)
        
        print(f"   ✅ Total strategies: {self.total_strategies:,}")
        
        # Calculate batches
        batches = []
        for i in range(0, self.total_strategies, self.batch_size):
            start_idx = i
            end_idx = min(i + self.batch_size, self.total_strategies)
            batches.append((start_idx, end_idx))
        
        self.num_batches = len(batches)
        print(f"   ✅ Total batches: {self.num_batches} (batch size: {self.batch_size})")
        
        return batches
    
    def run_batch(self, batch_idx: int, start_idx: int, end_idx: int) -> Tuple[bool, float, str, bool]:
        """
        Run a single batch in subprocess
        
        Args:
            batch_idx: Batch index (0-based)
            start_idx: Strategy start index (inclusive)
            end_idx: Strategy end index (exclusive)
        
        Returns:
            Tuple of (success, elapsed_time, output_file, from_cache)
        """
        output_file = self.output_dir / f"results_batch_{batch_idx}.parquet"
        error_log_file = self.output_dir / f"error_batch_{batch_idx}.log"
        
        # Check if batch already exists (cache detection)
        if self.skip_existing and output_file.exists():
            return True, 0.0, str(output_file), True  # from_cache=True
        
        # Build command with batch context for progress display
        cmd = [
            sys.executable,
            "backtest_batch.py",
            "--start", str(start_idx),
            "--end", str(end_idx),
            "--output", str(output_file),
            "--parquet", str(self.parquet_file),
            "--batch-number", str(batch_idx + 1),  # 1-based for display
            "--total-batches", str(self.num_batches)
        ]
        
        # Run subprocess (stream stdout for real-time progress display)
        # Note: stdout streams directly to terminal for real-time progress visibility
        # stderr is captured to error log file for debugging while still visible in terminal
        start_time = time.time()
        try:
            with open(error_log_file, 'w') as error_log:
                result = subprocess.run(
                    cmd,
                    cwd=Path(__file__).parent,
                    stdout=None,  # Stream to terminal
                    stderr=error_log,  # Capture errors to file for debugging
                    text=True,  # Ensure text mode for error log
                    timeout=3600  # 1 hour timeout per batch
                )
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Clean up error log if successful
                if error_log_file.exists() and error_log_file.stat().st_size == 0:
                    error_log_file.unlink()
                return True, elapsed, str(output_file), False  # from_cache=False
            else:
                print(f"\n   ❌ Batch {batch_idx} failed with return code {result.returncode}")
                print(f"      Check output above or error log: {error_log_file}")
                return False, elapsed, str(output_file), False  # from_cache=False
                
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            print(f"\n   ⏰ Batch {batch_idx} timed out after {elapsed:.0f}s")
            return False, elapsed, str(output_file), False  # from_cache=False
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n   ❌ Batch {batch_idx} error: {e}")
            return False, elapsed, str(output_file), False  # from_cache=False
    
    def run_all_batches(self) -> List[str]:
        """
        Run all batches sequentially
        
        Returns:
            List of successful output file paths
        """
        batches = self.calculate_batches()
        
        # Check for existing batches (cache detection)
        cached_batch_indices = []
        if self.skip_existing:
            for batch_idx in range(self.num_batches):
                output_file = self.output_dir / f"results_batch_{batch_idx}.parquet"
                if output_file.exists():
                    cached_batch_indices.append(batch_idx + 1)  # 1-based for display
        
        # Display cache status
        print(f"\n{'='*80}")
        print(f"🚀 BATCH PROCESSING: {self.total_strategies:,} strategies in {self.num_batches} batches")
        print(f"{'='*80}\n")
        
        if cached_batch_indices:
            n_cached = len(cached_batch_indices)
            n_remaining = self.num_batches - n_cached
            
            print(f"✅ Found {n_cached} cached batch result{'s' if n_cached != 1 else ''}!")
            
            # Display ranges of cached batches
            if n_cached <= 5:
                # Show individual batch numbers if few
                batch_list = ", ".join(map(str, cached_batch_indices))
                print(f"   Skipping batches: {batch_list}")
            else:
                # Show range if many
                print(f"   Skipping batches: {cached_batch_indices[0]}-{cached_batch_indices[-1]}")
            
            print(f"   Processing remaining: {n_remaining} batch{'es' if n_remaining != 1 else ''}\n")
        elif self.force_rerun:
            print(f"🔄 Force rerun enabled - reprocessing all batches\n")
        
        successful_files = []
        total_start = time.time()
        
        for batch_idx, (start_idx, end_idx) in enumerate(batches, start=1):
            batch_size = end_idx - start_idx
            
            # Get current RAM usage
            mem = psutil.virtual_memory()
            mem_pct = mem.percent
            
            print(f"\n{'─'*80}")
            print(f"Batch {batch_idx:2d}/{self.num_batches}: {start_idx:5d}-{end_idx:5d}  ", end="")
            
            # Run batch (with cache detection)
            success, elapsed, output_file, from_cache = self.run_batch(batch_idx - 1, start_idx, end_idx)
            
            if success:
                # Check output file exists
                if Path(output_file).exists():
                    file_size_mb = Path(output_file).stat().st_size / (1024 ** 2)
                    successful_files.append(output_file)
                    
                    if from_cache:
                        # Cached batch
                        print(f"📦 CACHED | {batch_size:3d} strategies | RAM: {mem_pct:4.1f}% | {file_size_mb:.2f}MB")
                        self.cached_batches.append((batch_idx, start_idx, end_idx))
                    else:
                        # Newly processed batch
                        print(f"✅ {elapsed:5.1f}s | {batch_size:3d} strategies | RAM: {mem_pct:4.1f}% | {file_size_mb:.2f}MB")
                else:
                    print(f"⚠️  {elapsed:5.1f}s | Output file missing!")
                    self.failed_batches.append((batch_idx, start_idx, end_idx))
            else:
                print(f"❌ {elapsed:5.1f}s | FAILED")
                self.failed_batches.append((batch_idx, start_idx, end_idx))
        
        total_elapsed = time.time() - total_start
        
        # Summary
        print(f"\n{'='*80}")
        print(f"✅ BATCH PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"   Total time: {int(total_elapsed//60)}m {int(total_elapsed%60)}s")
        print(f"   Successful batches: {len(successful_files)}/{self.num_batches}")
        
        # Show cache vs processed breakdown
        n_cached = len(self.cached_batches)
        n_processed = len(successful_files) - n_cached
        if n_cached > 0:
            print(f"   Cached batches: {n_cached}")
            print(f"   Processed batches: {n_processed}")
        
        print(f"   Failed batches: {len(self.failed_batches)}")
        
        if self.failed_batches:
            print(f"\n   ⚠️  Failed batches:")
            for batch_idx, start_idx, end_idx in self.failed_batches:
                print(f"      Batch {batch_idx}: {start_idx}-{end_idx}")
        
        print(f"{'='*80}\n")
        
        return successful_files
    
    def merge_results(self, result_files: List[str], output_file: Path = None) -> Path:
        """
        Merge all batch result files into single parquet
        
        Args:
            result_files: List of batch result file paths
            output_file: Output file path (default: auto-generated)
        
        Returns:
            Path to merged results file
        """
        if not result_files:
            print("\n⚠️  No result files to merge!")
            return None
        
        print(f"\n{'='*80}")
        print(f"🔗 MERGING RESULTS")
        print(f"{'='*80}")
        print(f"   Batch files: {len(result_files)}")
        
        # Read all files
        dfs = []
        total_rows = 0
        
        for i, file_path in enumerate(result_files, start=1):
            try:
                df = pd.read_parquet(file_path)
                dfs.append(df)
                total_rows += len(df)
                print(f"   [{i:2d}/{len(result_files)}] {Path(file_path).name}: {len(df):,} rows")
            except Exception as e:
                print(f"   ⚠️  [{i:2d}/{len(result_files)}] Failed to read {file_path}: {e}")
        
        # Merge
        if not dfs:
            print("\n❌ No valid dataframes to merge!")
            return None
        
        print(f"\n   🔗 Merging {len(dfs)} dataframes...")
        merged_df = pd.concat(dfs, ignore_index=True)
        
        print(f"   ✅ Merged: {len(merged_df):,} total rows")
        
        # Save merged results
        if output_file is None:
            from config import FILE_PREFIX
            output_file = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_parquet(output_file, compression='snappy')
        
        file_size_mb = output_file.stat().st_size / (1024 ** 2)
        print(f"\n   💾 Saved to: {output_file}")
        print(f"      Size: {file_size_mb:.2f} MB")
        print(f"{'='*80}\n")
        
        return output_file
    
    def run(self, merge: bool = True) -> Path:
        """
        Run complete batch processing pipeline
        
        Args:
            merge: Whether to merge results (default: True)
        
        Returns:
            Path to merged results file (if merge=True), else None
        """
        # Run all batches
        successful_files = self.run_all_batches()
        
        # Merge results
        if merge and successful_files:
            merged_file = self.merge_results(successful_files)
            return merged_file
        
        return None


def run_batch_processing(batch_size: int = 200, parquet_file: Path = None, force_rerun: bool = False) -> Path:
    """
    Convenience function to run batch processing
    
    Args:
        batch_size: Number of strategies per batch (default: 200)
        parquet_file: Path to data parquet file (default: from config)
        force_rerun: Force rerun all batches, ignore cache (default: False)
    
    Returns:
        Path to merged results file
    """
    runner = BatchRunner(batch_size=batch_size, parquet_file=parquet_file, force_rerun=force_rerun)
    return runner.run(merge=True)


if __name__ == "__main__":
    """Test batch runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch runner for strategy backtesting")
    parser.add_argument("--batch-size", type=int, default=200, help="Batch size (default: 200)")
    parser.add_argument("--parquet", type=str, default=None, help="Path to parquet data file")
    parser.add_argument("--no-merge", action="store_true", help="Skip merging results")
    parser.add_argument("--force-rerun", action="store_true", help="Force rerun all batches, ignore cache")
    parser.add_argument("--no-skip-existing", action="store_true", help="Don't skip existing batches (reprocess all)")
    
    args = parser.parse_args()
    
    parquet_path = Path(args.parquet) if args.parquet else None
    
    # Determine skip_existing based on flags
    skip_existing = not args.no_skip_existing
    
    runner = BatchRunner(
        batch_size=args.batch_size, 
        parquet_file=parquet_path,
        skip_existing=skip_existing,
        force_rerun=args.force_rerun
    )
    result_file = runner.run(merge=not args.no_merge)
    
    if result_file:
        print(f"\n✅ Complete! Results saved to: {result_file}")
    else:
        print(f"\n⚠️  Processing complete but no merged results")
