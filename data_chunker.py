#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DATA CHUNKER 💎🌟⚡

Data Chunking System: Split large datasets into manageable pieces
"Dividing the light into prismatic fragments"

Technical: Temporal chunking for memory-efficient processing
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Literal
import json
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 🔧 CHUNK SIZE CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════

CHUNK_CONFIGS = {
    "daily": {
        "freq": "D",
        "approx_rows_per_chunk": 40_000,
        "description": "~40K rows per chunk (365 chunks/year)"
    },
    "weekly": {
        "freq": "W",
        "approx_rows_per_chunk": 300_000,
        "description": "~300K rows per chunk (52 chunks/year)"
    },
    "monthly": {
        "freq": "MS",  # Month Start
        "approx_rows_per_chunk": 1_200_000,
        "description": "~1.2M rows per chunk (12 chunks/year)"
    }
}


# ═══════════════════════════════════════════════════════════════
# 💎 DATA CHUNKER CLASS
# ═══════════════════════════════════════════════════════════════

class DataChunker:
    """
    Split large parquet files into manageable chunks
    
    Technical: Temporal-based chunking for parallel processing
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize DataChunker
        
        Args:
            output_dir: Directory to save chunks (default: data/chunks)
        """
        self.output_dir = output_dir or Path("data/chunks")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata = {}
        self.chunk_files = []
    
    def split_temporal(
        self,
        parquet_path: Path,
        chunk_size: Literal["daily", "weekly", "monthly"] = "monthly"
    ) -> List[Path]:
        """
        Split data by time periods
        
        Args:
            parquet_path: Path to source parquet file
            chunk_size: Temporal chunk size
                - 'monthly': ~1.2M rows per chunk (12 chunks/year)
                - 'weekly': ~300K rows per chunk (52 chunks/year)
                - 'daily': ~40K rows per chunk (365 chunks/year)
        
        Returns:
            List[Path]: Paths to chunk files
        """
        print(f"\n💎 Splitting {parquet_path.name} into {chunk_size} chunks...")
        print("─" * 60)
        
        # Load data
        print("📊 Loading source data...")
        df = pd.read_parquet(parquet_path)
        
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column for temporal splitting")
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        total_rows = len(df)
        print(f"   Total rows: {total_rows:,}")
        
        # Get chunk configuration
        config = CHUNK_CONFIGS[chunk_size]
        freq = config["freq"]
        
        # Group by period
        # Convert to period strings to avoid timezone issues
        if freq == 'D':
            df['period'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        elif freq == 'W':
            df['period'] = df['timestamp'].dt.strftime('%Y-W%U')
        else:  # Monthly
            df['period'] = df['timestamp'].dt.strftime('%Y-%m')
        
        periods = sorted(df['period'].unique())
        
        print(f"   Periods found: {len(periods)}")
        print(f"   Date range: {periods[0]} to {periods[-1]}")
        
        # Split into chunks
        chunk_files = []
        chunk_metadata = []
        
        for i, period in enumerate(periods, 1):
            period_df = df[df['period'] == period].drop(columns=['period'])
            
            if len(period_df) == 0:
                continue
            
            # Create chunk filename
            period_str = str(period)
            chunk_file = self.output_dir / f"chunk_{i:03d}_{period_str}.parquet"
            
            # Save chunk
            period_df.to_parquet(chunk_file, compression='snappy')
            chunk_files.append(chunk_file)
            
            # Store metadata
            chunk_meta = {
                "chunk_id": i,
                "period": period_str,
                "start_date": str(period_df['timestamp'].min()),
                "end_date": str(period_df['timestamp'].max()),
                "rows": len(period_df),
                "file": str(chunk_file),
                "size_mb": chunk_file.stat().st_size / (1024 * 1024)
            }
            chunk_metadata.append(chunk_meta)
            
            print(f"   ✅ Chunk {i:3d}/{len(periods)}: {period_str:12s} "
                  f"| {len(period_df):>8,} rows | {chunk_meta['size_mb']:>6.1f} MB")
        
        # Drop temporary column
        df.drop(columns=['period'], inplace=True, errors='ignore')
        
        # Store overall metadata
        self.metadata = {
            "source_file": str(parquet_path),
            "chunk_size": chunk_size,
            "chunk_config": config,
            "total_chunks": len(chunk_files),
            "total_rows": total_rows,
            "chunks": chunk_metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_file = self.output_dir / "chunks_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"\n✅ Created {len(chunk_files)} chunks")
        print(f"📁 Metadata saved to: {metadata_file}")
        
        self.chunk_files = chunk_files
        return chunk_files
    
    def get_chunk_metadata(self, chunk_dir: Optional[Path] = None) -> Dict:
        """
        Return metadata about chunks
        
        Args:
            chunk_dir: Directory containing chunks (default: self.output_dir)
        
        Returns:
            dict: Chunk metadata
                - Number of chunks
                - Rows per chunk
                - Date ranges
                - Total size
        """
        chunk_dir = chunk_dir or self.output_dir
        metadata_file = chunk_dir / "chunks_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            return metadata
        
        # If no metadata file, scan directory
        chunk_files = sorted(chunk_dir.glob("chunk_*.parquet"))
        
        if not chunk_files:
            return {
                "total_chunks": 0,
                "error": "No chunks found"
            }
        
        # Build metadata from files
        chunks_meta = []
        total_rows = 0
        
        for i, chunk_file in enumerate(chunk_files, 1):
            df = pd.read_parquet(chunk_file)
            
            chunk_meta = {
                "chunk_id": i,
                "file": str(chunk_file),
                "rows": len(df),
                "start_date": str(df['timestamp'].min()) if 'timestamp' in df.columns else None,
                "end_date": str(df['timestamp'].max()) if 'timestamp' in df.columns else None,
                "size_mb": chunk_file.stat().st_size / (1024 * 1024)
            }
            chunks_meta.append(chunk_meta)
            total_rows += len(df)
        
        metadata = {
            "total_chunks": len(chunk_files),
            "total_rows": total_rows,
            "chunks": chunks_meta,
            "scanned_at": datetime.now().isoformat()
        }
        
        return metadata
    
    def load_chunk(self, chunk_id: int) -> pd.DataFrame:
        """
        Load a specific chunk by ID
        
        Args:
            chunk_id: Chunk ID to load
        
        Returns:
            DataFrame: Chunk data
        """
        if not self.chunk_files:
            # Try to load from metadata
            metadata = self.get_chunk_metadata()
            if 'chunks' in metadata and chunk_id - 1 < len(metadata['chunks']):
                chunk_file = Path(metadata['chunks'][chunk_id - 1]['file'])
                return pd.read_parquet(chunk_file)
            raise ValueError(f"Chunk {chunk_id} not found")
        
        if chunk_id < 1 or chunk_id > len(self.chunk_files):
            raise ValueError(f"Chunk ID {chunk_id} out of range (1-{len(self.chunk_files)})")
        
        return pd.read_parquet(self.chunk_files[chunk_id - 1])
    
    def cleanup_chunks(self, keep_metadata: bool = True):
        """
        Remove chunk files
        
        Args:
            keep_metadata: If True, keep metadata file
        """
        chunk_files = list(self.output_dir.glob("chunk_*.parquet"))
        
        for chunk_file in chunk_files:
            chunk_file.unlink()
        
        print(f"🗑️  Removed {len(chunk_files)} chunk files")
        
        if not keep_metadata:
            metadata_file = self.output_dir / "chunks_metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
                print(f"🗑️  Removed metadata file")


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            ⚡ DATA CHUNKER TEST ⚡                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    print("📊 Generating test data...")
    
    test_dir = Path("/tmp/necrozma_chunker_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create 3 months of synthetic data
    dates = pd.date_range("2025-01-01", "2025-03-31", freq="1min")
    n_samples = len(dates)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'mid_price': 1.1000 + np.cumsum(np.random.randn(n_samples) * 0.00001),
        'volume': np.random.randint(1, 100, n_samples)
    })
    
    test_parquet = test_dir / "test_data.parquet"
    df.to_parquet(test_parquet, compression='snappy')
    
    print(f"   ✅ Created test data: {len(df):,} rows")
    print(f"   📁 Saved to: {test_parquet}")
    
    # Test chunking
    print("\n📦 Testing chunking...")
    chunker = DataChunker(output_dir=test_dir / "chunks")
    
    chunk_files = chunker.split_temporal(test_parquet, chunk_size="monthly")
    
    print(f"\n✅ Created {len(chunk_files)} chunk files")
    
    # Test metadata
    print("\n📋 Testing metadata retrieval...")
    metadata = chunker.get_chunk_metadata()
    
    print(f"   Total chunks: {metadata['total_chunks']}")
    print(f"   Total rows: {metadata['total_rows']:,}")
    print(f"   Chunk size: {metadata.get('chunk_size', 'N/A')}")
    
    # Test loading chunk
    print("\n📥 Testing chunk loading...")
    chunk_df = chunker.load_chunk(1)
    print(f"   ✅ Loaded chunk 1: {len(chunk_df):,} rows")
    
    # Cleanup
    print("\n🗑️  Cleaning up test files...")
    chunker.cleanup_chunks(keep_metadata=False)
    test_parquet.unlink()
    
    print("\n✅ All tests passed!")
