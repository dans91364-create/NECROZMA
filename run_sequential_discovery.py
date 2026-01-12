#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - Sequential Discovery Runner 💎🌟⚡

CPU-first optimization (allow RAM usage up to 50GB)
STRICTLY SEQUENTIAL: 1 process, < 85% CPU target

"Where light moves in harmony, not in chaos"
"""

import sys
from pathlib import Path
import time
import gc

# Ensure correct imports
sys.path.insert(0, str(Path(__file__).parent))

from data_chunker import DataChunker
from config import MAX_MEMORY_GB

# Import psutil for monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  Warning: psutil not available - resource monitoring disabled")


def cooling_break(duration=120, cpu_threshold=85):
    """
    Pause if CPU is too high
    
    Args:
        duration: Duration in seconds
        cpu_threshold: CPU threshold percentage
    """
    if not HAS_PSUTIL:
        print(f"\n❄️  COOLING BREAK - {duration}s pause...", flush=True)
        time.sleep(duration)
        return
    
    current_cpu = psutil.cpu_percent(interval=2)
    
    if current_cpu > cpu_threshold:
        print(f"\n❄️  COOLING BREAK - CPU too high ({current_cpu:.1f}%)", flush=True)
        print(f"   Waiting {duration}s...", flush=True)
        
        for i in range(duration, 0, -10):
            cpu = psutil.cpu_percent(interval=1)
            mem_gb = psutil.virtual_memory().used / 1e9
            print(f"   {i:3d}s | CPU: {cpu:5.1f}% | RAM: {mem_gb:5.1f}GB", flush=True)
            time.sleep(10)
        
        print("   ✅ Resumed\n", flush=True)
    else:
        print(f"\n   💤 Quick pause ({duration}s, CPU OK at {current_cpu:.1f}%)...", flush=True)
        time.sleep(duration)
        print("   ✅ Resumed\n", flush=True)


def main():
    """
    Main sequential discovery runner
    
    Processes data in STRICT SEQUENTIAL MODE:
    - 1 universe at a time
    - 1 chunk at a time
    - CPU target: < 85%
    - RAM can use up to 50GB
    """
    print("\n" + "═"*70)
    print("🌟 ULTRA NECROZMA - Sequential Discovery (Low CPU Mode)")
    print("═"*70 + "\n")
    
    # Config
    PARQUET_FILE = 'data/EURUSD_2025.parquet'
    CHUNKS_DIR = Path('data/chunks')
    RESULTS_DIR = Path('results')
    RESULTS_DIR.mkdir(exist_ok=True)
    
    # Universes - as specified in problem statement
    timeframes = [5]
    lookbacks = [5, 10, 20, 30, 50, 75, 100, 120, 150, 180, 200, 220, 250, 
                 270, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200]
    
    universes = [
        {'tf': tf, 'lb': lb, 'name': f'{tf}min_{lb}lb'} 
        for tf in timeframes for lb in lookbacks
    ]
    
    print(f"📊 Configuration:")
    print(f"   Universes:  {len(universes)}")
    print(f"   Mode:       SEQUENTIAL (1 universe at a time)")
    print(f"   CPU limit:  85%")
    print(f"   RAM limit:  {MAX_MEMORY_GB:.0f}GB (soft, can go higher)")
    print()
    
    # Create chunks if they don't exist
    if not CHUNKS_DIR.exists() or len(list(CHUNKS_DIR.glob('*.parquet'))) == 0:
        print("📦 Creating chunks...", flush=True)
        chunker = DataChunker()
        chunks = chunker.split_temporal(PARQUET_FILE, chunk_size='monthly')
        print(f"✅ Created {len(chunks)} chunks\n")
    
    chunks = sorted(CHUNKS_DIR.glob('chunk_*.parquet'))
    print(f"📁 Found {len(chunks)} chunks\n")
    
    # Process
    total_start = time.time()
    
    # Import analyzer here to avoid early loading
    from analyzer import PatternAnalyzer
    import pandas as pd
    
    for universe_idx, universe in enumerate(universes):
        print(f"\n{'═'*70}")
        print(f"🌟 UNIVERSE {universe_idx+1}/{len(universes)}: {universe['name']}")
        print(f"{'═'*70}\n")
        
        universe_results = []
        
        # Process each chunk SEQUENTIALLY
        for chunk_idx, chunk_file in enumerate(chunks):
            print(f"  📦 Chunk {chunk_idx+1}/{len(chunks)}: {chunk_file.name}", flush=True)
            
            chunk_start = time.time()
            
            # Load chunk (RAM ok)
            df = pd.read_parquet(chunk_file)
            
            # Process
            try:
                # Import and use the real analyzer
                from data_loader import resample_to_ohlc
                from analyzer import get_movement_targets, extract_window_features
                
                # Resample to OHLC
                ohlc = resample_to_ohlc(df, universe['tf'])
                
                # Get movement targets
                targets = get_movement_targets(ohlc, universe['lb'])
                
                # Count patterns
                pattern_count = sum(
                    len(targets[level][direction])
                    for level in targets
                    for direction in targets[level]
                )
                
                universe_results.append({
                    'chunk': chunk_file.name,
                    'patterns': pattern_count
                })
                
            except Exception as e:
                print(f"     ⚠️  Error processing: {e}", flush=True)
                pattern_count = 0
            
            # Stats
            elapsed = time.time() - chunk_start
            
            if HAS_PSUTIL:
                cpu = psutil.cpu_percent(interval=0.5)
                mem_gb = psutil.virtual_memory().used / 1e9
                
                print(f"     ⏱️  {elapsed:6.1f}s | Patterns: {pattern_count:7,} | "
                      f"CPU: {cpu:5.1f}% | RAM: {mem_gb:5.1f}GB", flush=True)
                
                # Cooling break if CPU high
                if cpu > 85:
                    cooling_break(60, cpu_threshold=85)
                
                # Light cleanup
                del df
                if mem_gb > MAX_MEMORY_GB:
                    print(f"     💾 Cleaning up memory (RAM: {mem_gb:.1f}GB)...", flush=True)
                    gc.collect()
            else:
                print(f"     ⏱️  {elapsed:6.1f}s | Patterns: {pattern_count:7,}", flush=True)
                del df
                gc.collect()
        
        # Merge universe results
        if universe_results:
            total_patterns = sum(r['patterns'] for r in universe_results)
            
            print(f"\n✅ Universe {universe_idx+1} complete:")
            print(f"   Total patterns: {total_patterns:,}")
            print(f"   Chunks processed: {len(universe_results)}\n")
            
            # Cleanup between universes
            del universe_results
            gc.collect()
        
        # Cooling break every 5 universes
        if (universe_idx + 1) % 5 == 0 and universe_idx + 1 < len(universes):
            cooling_break(120, cpu_threshold=70)
    
    # End
    total_elapsed = time.time() - total_start
    print("\n" + "═"*70)
    print("🎉 DISCOVERY COMPLETE!")
    print(f"   Total time: {total_elapsed/3600:.2f}h")
    print(f"   Universes:  {len(universes)}")
    print("═"*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
