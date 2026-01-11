#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - UNIVERSE PROCESSOR 💎🌟⚡

Dual Processing Strategy: Process universes with chunked or universe-first approach
"Two paths to enlightenment - choose wisely"

Technical: Flexible processing strategies for different resource constraints
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Literal, Callable
import time
import psutil
import gc

from data_chunker import DataChunker
from checkpoint_manager import CheckpointManager
from thermal_manager import CoolingManager, CPUMonitor
from result_consolidator import ResultConsolidator


# ═══════════════════════════════════════════════════════════════
# 💎 UNIVERSE PROCESSOR CLASS
# ═══════════════════════════════════════════════════════════════

class UniverseProcessor:
    """
    Process universes with dual strategy support
    
    Strategies:
    - 'chunked': Process all universes per chunk (fast, more memory)
    - 'universe': Process all chunks per universe (slow, less memory)
    - 'auto': Decide based on RAM available
    
    Technical: Flexible processing with checkpoint/resume support
    """
    
    def __init__(
        self,
        strategy: Literal['auto', 'chunked', 'universe'] = 'auto',
        chunk_size: Literal['daily', 'weekly', 'monthly'] = 'monthly',
        output_dir: Optional[Path] = None,
        enable_checkpoints: bool = True,
        enable_cooling: bool = True,
        cooling_chunk_interval: int = 3,
        cooling_universe_interval: int = 5,
        cooling_duration: int = 120,
        max_cpu: int = 85,
        process_func: Optional[Callable] = None
    ):
        """
        Initialize UniverseProcessor
        
        Args:
            strategy: Processing strategy
            chunk_size: Temporal chunk size
            output_dir: Output directory
            enable_checkpoints: Enable checkpoint/resume
            enable_cooling: Enable cooling breaks
            cooling_chunk_interval: Cooling break every N chunks
            cooling_universe_interval: Cooling break every N universes
            cooling_duration: Cooling break duration in seconds
            max_cpu: Maximum CPU percentage before throttling
            process_func: Custom processing function (for testing)
        """
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.output_dir = output_dir or Path("ultra_necrozma_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Processing function
        self.process_func = process_func
        
        # Components
        self.chunker = DataChunker(output_dir=self.output_dir / "chunks")
        self.checkpoint_mgr = CheckpointManager(
            checkpoint_dir=self.output_dir / ".checkpoint"
        ) if enable_checkpoints else None
        
        self.cooling_mgr = CoolingManager(
            chunk_interval=cooling_chunk_interval,
            universe_interval=cooling_universe_interval,
            chunk_duration=cooling_duration,
            universe_duration=cooling_duration
        ) if enable_cooling else None
        
        self.cpu_monitor = CPUMonitor(max_cpu=max_cpu)
        self.consolidator = ResultConsolidator(output_dir=self.output_dir)
        
        # State
        self.chunks = []
        self.universes = []
        self.results = {}
        self.start_time = None
    
    def _get_process_function(self):
        """Get the processing function (lazy import)"""
        if self.process_func:
            return self.process_func
        
        # Import here to avoid circular dependency
        from analyzer import process_universe
        return process_universe
    
    def process(
        self,
        df: pd.DataFrame,
        universes: List[Dict],
        resume: bool = False,
        fresh: bool = False
    ) -> Dict:
        """
        Main processing entry point
        
        Args:
            df: Input DataFrame
            universes: List of universe configurations
            resume: Resume from checkpoint if available
            fresh: Ignore checkpoints and start fresh
        
        Returns:
            dict: Processing results
        """
        self.start_time = time.time()
        self.universes = universes
        
        # Auto-select strategy if needed
        if self.strategy == 'auto':
            self.strategy = self._auto_select_strategy()
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🌟 ULTRA NECROZMA - Universe Processor                     ║
╚══════════════════════════════════════════════════════════════╝

📊 Configuration:
   Strategy:       {self.strategy}
   Chunk size:     {self.chunk_size}
   Universes:      {len(universes)}
   Checkpointing:  {'Enabled' if self.checkpoint_mgr else 'Disabled'}
   Cooling:        {'Enabled' if self.cooling_mgr else 'Disabled'}
   Max CPU:        {self.cpu_monitor.max_cpu}%
""")
        
        # Handle checkpoints
        start_universe = 0
        start_chunk = 0
        
        if fresh and self.checkpoint_mgr:
            print("🗑️  Fresh start requested - cleaning up old checkpoints...")
            self.checkpoint_mgr.cleanup_checkpoints(keep_latest=0)
        elif resume and self.checkpoint_mgr and self.checkpoint_mgr.should_resume():
            print("♻️  Resume requested - loading checkpoint...")
            start_universe, start_chunk, completed = self.checkpoint_mgr.load_checkpoint()
            self.results = completed.get('results', {})
        
        # Split data into chunks
        if not self.chunks:
            print(f"\n💎 Creating temporal chunks ({self.chunk_size})...")
            # Save temp parquet for chunking
            temp_parquet = self.output_dir / "temp_data.parquet"
            df.to_parquet(temp_parquet, compression='snappy')
            
            self.chunks = self.chunker.split_temporal(temp_parquet, self.chunk_size)
            
            # Clean up temp file
            temp_parquet.unlink()
        
        print(f"\n   Created {len(self.chunks)} chunks")
        
        # Process based on strategy
        if self.strategy == 'chunked':
            results = self._process_chunked_strategy(
                start_chunk=start_chunk,
                start_universe=start_universe
            )
        else:  # universe
            results = self._process_universe_strategy(
                start_universe=start_universe,
                start_chunk=start_chunk
            )
        
        # Consolidate results
        print(f"\n🔧 Consolidating results...")
        final_results = self._consolidate_results()
        
        # Cleanup if successful
        if self.checkpoint_mgr:
            self.checkpoint_mgr.cleanup_checkpoints(keep_latest=1)
        
        elapsed = time.time() - self.start_time
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ PROCESSING COMPLETE                                     ║
╚══════════════════════════════════════════════════════════════╝

   Total time:     {elapsed/3600:.1f} hours
   Strategy:       {self.strategy}
   Universes:      {len(self.universes)}
   Chunks:         {len(self.chunks)}
""")
        
        return final_results
    
    def _process_chunked_strategy(
        self,
        start_chunk: int = 0,
        start_universe: int = 0
    ) -> Dict:
        """
        Process all universes per chunk (fast, more memory)
        
        FOR each chunk:
            FOR each universe:
                Process universe on chunk
                Save temp results
            Merge universe results for chunk
            Save chunk_XX_results.parquet
        
        Args:
            start_chunk: Chunk to start from
            start_universe: Universe to start from (within chunk)
        
        Returns:
            dict: Results
        """
        print(f"\n⚡ Running CHUNKED strategy (fast, more memory)")
        print("─" * 60)
        
        for chunk_idx, chunk_file in enumerate(self.chunks, 1):
            if chunk_idx < start_chunk:
                continue
            
            print(f"\n📦 Processing chunk {chunk_idx}/{len(self.chunks)}: {chunk_file.name}")
            
            # Load chunk
            chunk_df = pd.read_parquet(chunk_file)
            
            chunk_results = []
            
            # Process all universes on this chunk
            for universe_idx, universe_config in enumerate(self.universes, 1):
                if chunk_idx == start_chunk and universe_idx < start_universe:
                    continue
                
                print(f"   🌌 [{universe_idx}/{len(self.universes)}] {universe_config['name']}...")
                
                # Check CPU before processing
                if self.cpu_monitor.is_overheating():
                    self.cpu_monitor.wait_for_cooldown()
                
                # Process universe
                process_func = self._get_process_function()
                result = process_func(
                    chunk_df,
                    universe_config['interval'],
                    universe_config['lookback'],
                    universe_config['name']
                )
                
                if result:
                    chunk_results.append(result)
                
                # Memory cleanup
                gc.collect()
            
            # Save chunk results
            if chunk_results:
                chunk_output = self.output_dir / f"chunk_{chunk_idx:03d}_results.parquet"
                self._save_chunk_results(chunk_results, chunk_output)
            
            # Checkpoint
            if self.checkpoint_mgr:
                self.checkpoint_mgr.save_checkpoint(
                    universe_idx=0,  # Not applicable for chunked
                    chunk_idx=chunk_idx,
                    partial_results={'results': self.results},
                    strategy='chunked',
                    metadata={'elapsed_time': time.time() - self.start_time}
                )
            
            # Cooling break
            if self.cooling_mgr and self.cooling_mgr.should_pause_chunk(chunk_idx):
                self.cooling_mgr.cooling_break(
                    self.cooling_mgr.chunk_duration,
                    f"after chunk {chunk_idx}/{len(self.chunks)}"
                )
                self.cooling_mgr.mark_chunk_processed()
            
            # Cleanup
            gc.collect()
        
        return self.results
    
    def _process_universe_strategy(
        self,
        start_universe: int = 0,
        start_chunk: int = 0
    ) -> Dict:
        """
        Process all chunks per universe (slow, less memory)
        
        FOR each universe:
            FOR each chunk:
                Process chunk for universe
                Save temp results
            Merge chunks for universe
            Save universe_XX_results.parquet
        
        Args:
            start_universe: Universe to start from
            start_chunk: Chunk to start from (within universe)
        
        Returns:
            dict: Results
        """
        print(f"\n🌌 Running UNIVERSE strategy (slow, less memory)")
        print("─" * 60)
        
        for universe_idx, universe_config in enumerate(self.universes, 1):
            if universe_idx < start_universe:
                continue
            
            print(f"\n🌌 Processing universe {universe_idx}/{len(self.universes)}: {universe_config['name']}")
            
            universe_results = []
            
            # Process all chunks for this universe
            for chunk_idx, chunk_file in enumerate(self.chunks, 1):
                if universe_idx == start_universe and chunk_idx < start_chunk:
                    continue
                
                print(f"   📦 [{chunk_idx}/{len(self.chunks)}] {chunk_file.name}...")
                
                # Check CPU before processing
                if self.cpu_monitor.is_overheating():
                    self.cpu_monitor.wait_for_cooldown()
                
                # Load chunk
                chunk_df = pd.read_parquet(chunk_file)
                
                # Process universe on chunk
                process_func = self._get_process_function()
                result = process_func(
                    chunk_df,
                    universe_config['interval'],
                    universe_config['lookback'],
                    universe_config['name']
                )
                
                if result:
                    universe_results.append(result)
                
                # Checkpoint
                if self.checkpoint_mgr:
                    self.checkpoint_mgr.save_checkpoint(
                        universe_idx=universe_idx,
                        chunk_idx=chunk_idx,
                        partial_results={'results': self.results},
                        strategy='universe',
                        metadata={'elapsed_time': time.time() - self.start_time}
                    )
                
                # Cooling break
                if self.cooling_mgr and self.cooling_mgr.should_pause_chunk(chunk_idx):
                    self.cooling_mgr.cooling_break(
                        self.cooling_mgr.chunk_duration,
                        f"universe {universe_idx}, chunk {chunk_idx}/{len(self.chunks)}"
                    )
                    self.cooling_mgr.mark_chunk_processed()
                
                # Memory cleanup
                del chunk_df
                gc.collect()
            
            # Save universe results
            if universe_results:
                universe_output = self.output_dir / f"universe_{universe_idx:03d}_results.parquet"
                self._save_universe_results(universe_results, universe_output)
            
            # Universe cooling break
            if self.cooling_mgr and self.cooling_mgr.should_pause_universe(universe_idx):
                self.cooling_mgr.cooling_break(
                    self.cooling_mgr.universe_duration,
                    f"after universe {universe_idx}/{len(self.universes)}"
                )
                self.cooling_mgr.mark_universe_processed()
            
            # Cleanup
            gc.collect()
        
        return self.results
    
    def _auto_select_strategy(self) -> str:
        """Auto-select best strategy based on system resources"""
        total_ram_gb = psutil.virtual_memory().total / 1e9
        
        # Check if VM
        is_vm = False
        try:
            product_name_file = Path('/sys/class/dmi/id/product_name')
            if product_name_file.exists():
                product_name = product_name_file.read_text().strip()
                is_vm = any(indicator in product_name.lower() for indicator in 
                           ['vmware', 'virtualbox', 'kvm', 'qemu', 'xen', 'hyperv'])
        except:
            pass
        
        if is_vm:
            print(f"   🖥️  VM detected - selecting 'universe' strategy")
            return 'universe'
        elif total_ram_gb < 32:
            print(f"   💾 RAM < 32GB ({total_ram_gb:.1f}GB) - selecting 'universe' strategy")
            return 'universe'
        else:
            print(f"   ⚡ {total_ram_gb:.1f}GB RAM - selecting 'chunked' strategy")
            return 'chunked'
    
    def _save_chunk_results(self, results: List[Dict], output_file: Path):
        """Save chunk results to parquet"""
        # Convert to DataFrame (simplified)
        df = pd.DataFrame([
            {
                'universe': r['name'],
                'total_patterns': r['total_patterns'],
                'processing_time': r['processing_time']
            }
            for r in results
        ])
        
        df.to_parquet(output_file, compression='snappy')
        print(f"   ✅ Saved chunk results: {output_file.name}")
    
    def _save_universe_results(self, results: List[Dict], output_file: Path):
        """Save universe results to parquet"""
        # Convert to DataFrame (simplified)
        df = pd.DataFrame([
            {
                'chunk': i,
                'total_patterns': r['total_patterns'],
                'processing_time': r['processing_time']
            }
            for i, r in enumerate(results, 1)
        ])
        
        df.to_parquet(output_file, compression='snappy')
        print(f"   ✅ Saved universe results: {output_file.name}")
    
    def _consolidate_results(self) -> Dict:
        """Consolidate all results"""
        if self.strategy == 'chunked':
            results_dir = self.output_dir
            merged = self.consolidator.merge_chunk_results(results_dir)
        else:
            results_dir = self.output_dir
            merged = self.consolidator.merge_universe_results(results_dir)
        
        # Generate report
        report_file = self.consolidator.generate_final_report(
            merged,
            metadata={
                'strategy': self.strategy,
                'chunk_size': self.chunk_size,
                'total_chunks': len(self.chunks),
                'total_universes': len(self.universes),
                'elapsed_time': time.time() - self.start_time
            }
        )
        
        return {
            'merged_results': merged,
            'report_file': report_file
        }


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ⚡ UNIVERSE PROCESSOR TEST ⚡                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create test data
    print("📊 Creating test data...")
    
    test_dir = Path("/tmp/necrozma_processor_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create 2 months of data
    dates = pd.date_range("2025-01-01", "2025-02-28", freq="1min")
    df = pd.DataFrame({
        'timestamp': dates,
        'bid': 1.1000 + np.cumsum(np.random.randn(len(dates)) * 0.00001),
        'ask': 1.1000 + np.cumsum(np.random.randn(len(dates)) * 0.00001),
        'mid_price': 1.1000,
        'spread_pips': 1.0,
        'pips_change': np.random.randn(len(dates)) * 0.1
    })
    
    print(f"   ✅ Created {len(df):,} rows")
    
    # Create test universes
    test_universes = [
        {'name': 'universe_5m_10lb', 'interval': 5, 'lookback': 10},
        {'name': 'universe_15m_20lb', 'interval': 15, 'lookback': 20}
    ]
    
    # Test processor
    print("\n🔧 Testing Universe Processor...")
    processor = UniverseProcessor(
        strategy='universe',
        chunk_size='monthly',
        output_dir=test_dir,
        enable_checkpoints=False,
        enable_cooling=False
    )
    
    # This would process the full pipeline
    # For testing, we just verify initialization
    print(f"   ✅ Processor initialized")
    print(f"   Strategy: {processor.strategy}")
    print(f"   Chunk size: {processor.chunk_size}")
    
    print("\n✅ Test complete!")
