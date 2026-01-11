#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CHUNKED PROCESSING INTEGRATION TEST 💎🌟⚡

Test the complete chunked processing system end-to-end
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_chunker import DataChunker
from checkpoint_manager import CheckpointManager
from thermal_manager import CoolingManager, CPUMonitor
from result_consolidator import ResultConsolidator
from universe_processor import UniverseProcessor


def test_data_chunker():
    """Test data chunking functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: Data Chunker")
    print("=" * 60)
    
    # Create test data
    dates = pd.date_range("2025-01-01", "2025-03-31", freq="5min")
    df = pd.DataFrame({
        'timestamp': dates,
        'mid_price': 1.1000 + np.cumsum(np.random.randn(len(dates)) * 0.00001),
        'volume': np.random.randint(1, 100, len(dates))
    })
    
    test_dir = Path("/tmp/necrozma_integration_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Save test parquet
    test_parquet = test_dir / "test_data.parquet"
    df.to_parquet(test_parquet, compression='snappy')
    
    print(f"✓ Created test data: {len(df):,} rows")
    
    # Test chunking
    chunker = DataChunker(output_dir=test_dir / "chunks")
    chunk_files = chunker.split_temporal(test_parquet, chunk_size="monthly")
    
    assert len(chunk_files) == 3, f"Expected 3 chunks, got {len(chunk_files)}"
    print(f"✓ Created {len(chunk_files)} chunks")
    
    # Test metadata
    metadata = chunker.get_chunk_metadata()
    assert metadata['total_chunks'] == 3, "Metadata mismatch"
    assert metadata['total_rows'] == len(df), "Row count mismatch"
    print(f"✓ Metadata correct: {metadata['total_rows']:,} rows across {metadata['total_chunks']} chunks")
    
    # Cleanup
    chunker.cleanup_chunks(keep_metadata=False)
    test_parquet.unlink()
    
    print("✅ Data Chunker test PASSED")
    return True


def test_checkpoint_manager():
    """Test checkpoint/resume functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Checkpoint Manager")
    print("=" * 60)
    
    test_dir = Path("/tmp/necrozma_integration_test/.checkpoint")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    mgr = CheckpointManager(checkpoint_dir=test_dir)
    
    # Save checkpoint
    checkpoint = mgr.save_checkpoint(
        universe_idx=5,
        chunk_idx=3,
        partial_results={'completed': ['u1', 'u2', 'u3']},
        strategy='universe'
    )
    
    print(f"✓ Saved checkpoint: {checkpoint.name}")
    
    # Check if should resume
    should_resume = mgr.should_resume()
    assert should_resume, "Should detect checkpoint"
    print(f"✓ Checkpoint detected for resume")
    
    # Load checkpoint
    u_idx, c_idx, results = mgr.load_checkpoint()
    assert u_idx == 5, f"Universe index mismatch: {u_idx}"
    assert c_idx == 3, f"Chunk index mismatch: {c_idx}"
    assert 'completed' in results, "Results missing"
    print(f"✓ Loaded checkpoint: universe={u_idx}, chunk={c_idx}")
    
    # Cleanup
    mgr.cleanup_checkpoints(keep_latest=0)
    
    print("✅ Checkpoint Manager test PASSED")
    return True


def test_thermal_manager():
    """Test thermal management"""
    print("\n" + "=" * 60)
    print("TEST 3: Thermal Manager")
    print("=" * 60)
    
    # Test CoolingManager
    cooling = CoolingManager(
        chunk_interval=2,
        universe_interval=3,
        chunk_duration=3,  # Short for testing
        universe_duration=5
    )
    
    # Test intervals
    assert not cooling.should_pause_chunk(1), "Should not pause at chunk 1"
    assert cooling.should_pause_chunk(2), "Should pause at chunk 2"
    print(f"✓ Cooling intervals working correctly")
    
    # Test CPUMonitor
    cpu_mon = CPUMonitor(max_cpu=85)
    status = cpu_mon.get_current_status()
    
    assert 'current_cpu' in status, "Status missing current_cpu"
    assert 'status' in status, "Status missing status field"
    print(f"✓ CPU Monitor: {status['current_cpu']:.1f}% ({status['status']})")
    
    print("✅ Thermal Manager test PASSED")
    return True


def test_result_consolidator():
    """Test result consolidation"""
    print("\n" + "=" * 60)
    print("TEST 4: Result Consolidator")
    print("=" * 60)
    
    test_dir = Path("/tmp/necrozma_integration_test")
    universe_dir = test_dir / "universes"
    universe_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample results
    for i in range(1, 4):
        df = pd.DataFrame({
            'pattern_signature': [f'pattern_{j}' for j in range(5)],
            'count': np.random.randint(10, 100, 5),
            'confidence': np.random.uniform(0.6, 1.0, 5)
        })
        
        output_file = universe_dir / f"universe_{i:02d}.parquet"
        df.to_parquet(output_file, compression='snappy')
    
    print(f"✓ Created 3 test universe result files")
    
    # Test consolidation
    consolidator = ResultConsolidator(output_dir=test_dir / "final")
    merged = consolidator.merge_universe_results(universe_dir)
    
    assert len(merged) > 0, "No results merged"
    assert 'global_rank' in merged.columns, "Missing global_rank"
    print(f"✓ Merged {len(merged)} patterns with global ranking")
    
    # Test report generation
    report = consolidator.generate_final_report(merged, metadata={'test': True})
    assert report.exists(), "Report not created"
    print(f"✓ Generated report: {report.name}")
    
    print("✅ Result Consolidator test PASSED")
    return True


def test_universe_processor():
    """Test UniverseProcessor (without full analysis)"""
    print("\n" + "=" * 60)
    print("TEST 5: Universe Processor")
    print("=" * 60)
    
    # Mock process function
    def mock_process(df, interval, lookback, name):
        return {
            'name': name,
            'total_patterns': len(df) // 100,
            'processing_time': 0.1,
            'config': {'interval': interval, 'lookback': lookback}
        }
    
    test_dir = Path("/tmp/necrozma_integration_test/processor")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create processor
    processor = UniverseProcessor(
        strategy='universe',
        chunk_size='monthly',
        output_dir=test_dir,
        enable_checkpoints=False,
        enable_cooling=False,
        process_func=mock_process
    )
    
    assert processor.strategy == 'universe', "Strategy not set correctly"
    assert processor.chunk_size == 'monthly', "Chunk size not set correctly"
    print(f"✓ Processor initialized with {processor.strategy} strategy")
    
    # Test auto-select
    processor2 = UniverseProcessor(
        strategy='auto',
        output_dir=test_dir,
        enable_checkpoints=False,
        enable_cooling=False,
        process_func=mock_process
    )
    
    selected_strategy = processor2._auto_select_strategy()
    assert selected_strategy in ['chunked', 'universe'], f"Invalid strategy: {selected_strategy}"
    print(f"✓ Auto-selected strategy: {selected_strategy}")
    
    print("✅ Universe Processor test PASSED")
    return True


def run_all_tests():
    """Run all integration tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ⚡🌟💎 CHUNKED PROCESSING INTEGRATION TESTS 💎🌟⚡        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Data Chunker", test_data_chunker),
        ("Checkpoint Manager", test_checkpoint_manager),
        ("Thermal Manager", test_thermal_manager),
        ("Result Consolidator", test_result_consolidator),
        ("Universe Processor", test_universe_processor)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {name} test FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✨ ALL TESTS PASSED! ✨\n")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
