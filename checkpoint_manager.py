#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CHECKPOINT MANAGER 💎🌟⚡

Checkpoint/Resume System: Save and restore processing state
"Dimensional anchors prevent loss of progress"

Technical: Granular checkpointing for resumable processing
"""

import json
import time
import psutil
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 💎 CHECKPOINT MANAGER CLASS
# ═══════════════════════════════════════════════════════════════

class CheckpointManager:
    """
    Manage dual-level checkpointing for chunked and universe processing
    
    Technical: State persistence for resumable execution
    """
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize CheckpointManager
        
        Args:
            checkpoint_dir: Directory to save checkpoints (default: .checkpoint)
        """
        self.checkpoint_dir = checkpoint_dir or Path(".checkpoint")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_checkpoint = None
        self.checkpoint_history = []
    
    def save_checkpoint(
        self,
        universe_idx: int,
        chunk_idx: int,
        partial_results: Dict[str, Any],
        strategy: str = "auto",
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Save checkpoint with metadata
        
        Args:
            universe_idx: Current universe index
            chunk_idx: Current chunk index
            partial_results: Partial results to save
            strategy: Processing strategy used ('chunked', 'universe', 'auto')
            metadata: Additional metadata
        
        Returns:
            Path: Checkpoint file path
        """
        # Generate checkpoint filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoint_dir / f"u{universe_idx:03d}_c{chunk_idx:03d}_{timestamp}.json"
        
        # Get system resources
        mem = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Build checkpoint data
        checkpoint_data = {
            "version": "1.0",
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "strategy": strategy,
            "universe_idx": universe_idx,
            "chunk_idx": chunk_idx,
            "partial_results_path": None,  # Will be set if saving separately
            "metadata": metadata or {},
            "system_state": {
                "memory_used_gb": mem.used / 1e9,
                "memory_total_gb": mem.total / 1e9,
                "memory_percent": mem.percent,
                "cpu_percent": cpu_percent,
                "process_id": psutil.Process().pid
            },
            "elapsed_time": metadata.get('elapsed_time', 0) if metadata else 0
        }
        
        # If partial results are large, save separately
        if partial_results:
            results_size_estimate = len(str(partial_results))
            
            if results_size_estimate > 1_000_000:  # > 1MB
                # Save results separately
                results_file = self.checkpoint_dir / f"results_u{universe_idx:03d}_c{chunk_idx:03d}_{timestamp}.json"
                with open(results_file, 'w') as f:
                    json.dump(partial_results, f, indent=2, default=str)
                checkpoint_data["partial_results_path"] = str(results_file)
            else:
                # Include in checkpoint
                checkpoint_data["partial_results"] = partial_results
        
        # Save checkpoint
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
        
        self.current_checkpoint = checkpoint_file
        self.checkpoint_history.append(checkpoint_file)
        
        return checkpoint_file
    
    def load_checkpoint(self, checkpoint_file: Optional[Path] = None) -> Tuple[int, int, Dict]:
        """
        Load latest or specified checkpoint and resume
        
        Args:
            checkpoint_file: Specific checkpoint to load (default: latest)
        
        Returns:
            Tuple[int, int, Dict]: (universe_idx, chunk_idx, completed_items)
                - universe_idx: Universe index to resume from
                - chunk_idx: Chunk index to resume from
                - completed_items: Dictionary of completed work
        """
        if checkpoint_file is None:
            checkpoint_file = self._get_latest_checkpoint()
        
        if checkpoint_file is None:
            raise FileNotFoundError("No checkpoint file found")
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_file}")
        
        # Load checkpoint
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        
        universe_idx = checkpoint_data['universe_idx']
        chunk_idx = checkpoint_data['chunk_idx']
        
        # Load partial results
        completed_items = {}
        
        if 'partial_results' in checkpoint_data:
            completed_items = checkpoint_data['partial_results']
        elif 'partial_results_path' in checkpoint_data and checkpoint_data['partial_results_path']:
            results_file = Path(checkpoint_data['partial_results_path'])
            if results_file.exists():
                with open(results_file, 'r') as f:
                    completed_items = json.load(f)
        
        print(f"✅ Loaded checkpoint from {checkpoint_file.name}")
        print(f"   Universe: {universe_idx}, Chunk: {chunk_idx}")
        print(f"   Strategy: {checkpoint_data.get('strategy', 'unknown')}")
        print(f"   Saved at: {checkpoint_data.get('datetime', 'unknown')}")
        
        return universe_idx, chunk_idx, completed_items
    
    def should_resume(self) -> bool:
        """
        Check if valid checkpoint exists
        
        Returns:
            bool: True if checkpoint exists and is valid
        """
        latest = self._get_latest_checkpoint()
        
        if latest is None:
            return False
        
        # Check if checkpoint is recent (within 24 hours)
        age_hours = (time.time() - latest.stat().st_mtime) / 3600
        
        if age_hours > 24:
            print(f"⚠️  Checkpoint is {age_hours:.1f} hours old (may be stale)")
            return False
        
        return True
    
    def cleanup_checkpoints(self, keep_latest: int = 1):
        """
        Remove old checkpoints after successful completion
        
        Args:
            keep_latest: Number of latest checkpoints to keep
        """
        checkpoint_files = sorted(
            self.checkpoint_dir.glob("u*_c*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(checkpoint_files) <= keep_latest:
            return
        
        # Remove old checkpoints
        for checkpoint_file in checkpoint_files[keep_latest:]:
            # Also remove associated results file
            results_file = self.checkpoint_dir / checkpoint_file.name.replace("u", "results_u")
            if results_file.exists():
                results_file.unlink()
            
            checkpoint_file.unlink()
        
        removed = len(checkpoint_files) - keep_latest
        print(f"🗑️  Removed {removed} old checkpoint(s)")
    
    def get_checkpoint_info(self, checkpoint_file: Optional[Path] = None) -> Dict:
        """
        Get information about a checkpoint without loading results
        
        Args:
            checkpoint_file: Checkpoint to inspect (default: latest)
        
        Returns:
            dict: Checkpoint information
        """
        if checkpoint_file is None:
            checkpoint_file = self._get_latest_checkpoint()
        
        if checkpoint_file is None or not checkpoint_file.exists():
            return {"error": "No checkpoint found"}
        
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        
        # Remove large data
        info = {k: v for k, v in checkpoint_data.items() if k != 'partial_results'}
        
        return info
    
    def list_checkpoints(self) -> list:
        """
        List all available checkpoints
        
        Returns:
            list: List of checkpoint info dicts
        """
        checkpoint_files = sorted(
            self.checkpoint_dir.glob("u*_c*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        checkpoints = []
        for checkpoint_file in checkpoint_files:
            info = self.get_checkpoint_info(checkpoint_file)
            info['file'] = str(checkpoint_file)
            checkpoints.append(info)
        
        return checkpoints
    
    def _get_latest_checkpoint(self) -> Optional[Path]:
        """
        Get path to latest checkpoint file
        
        Returns:
            Path or None: Latest checkpoint file
        """
        checkpoint_files = sorted(
            self.checkpoint_dir.glob("u*_c*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return checkpoint_files[0] if checkpoint_files else None


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ⚡ CHECKPOINT MANAGER TEST ⚡                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create test directory
    test_dir = Path("/tmp/necrozma_checkpoint_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test checkpoint manager
    print("📋 Testing checkpoint manager...")
    manager = CheckpointManager(checkpoint_dir=test_dir)
    
    # Save checkpoint
    print("\n💾 Saving checkpoint...")
    partial_results = {
        "completed_universes": ["universe_1", "universe_2"],
        "total_patterns": 5000,
        "current_status": "processing"
    }
    
    checkpoint_file = manager.save_checkpoint(
        universe_idx=3,
        chunk_idx=5,
        partial_results=partial_results,
        strategy="chunked",
        metadata={"elapsed_time": 1234.5}
    )
    
    print(f"   ✅ Saved to: {checkpoint_file.name}")
    
    # Check if should resume
    print("\n🔍 Checking if should resume...")
    should_resume = manager.should_resume()
    print(f"   Should resume: {should_resume}")
    
    # Load checkpoint
    print("\n📥 Loading checkpoint...")
    universe_idx, chunk_idx, completed = manager.load_checkpoint()
    
    print(f"   Universe index: {universe_idx}")
    print(f"   Chunk index: {chunk_idx}")
    print(f"   Completed items: {len(completed)} keys")
    
    # Get checkpoint info
    print("\n📊 Getting checkpoint info...")
    info = manager.get_checkpoint_info()
    print(f"   Strategy: {info.get('strategy')}")
    print(f"   Memory: {info['system_state']['memory_percent']:.1f}%")
    print(f"   CPU: {info['system_state']['cpu_percent']:.1f}%")
    
    # List checkpoints
    print("\n📋 Listing checkpoints...")
    checkpoints = manager.list_checkpoints()
    print(f"   Found {len(checkpoints)} checkpoint(s)")
    
    # Cleanup
    print("\n🗑️  Cleaning up...")
    manager.cleanup_checkpoints(keep_latest=0)
    
    print("\n✅ All tests passed!")
