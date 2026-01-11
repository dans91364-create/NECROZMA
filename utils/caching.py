#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CACHING UTILITIES 💎🌟⚡

Intelligent caching with Joblib
"Save progress, never lose the light"

Technical: Disk-based caching and checkpointing
- Automatic cache invalidation on parameter changes
- Crash-resistant checkpointing
- Fast re-runs
"""

import hashlib
import json
import pickle
from pathlib import Path
from functools import wraps
import time

try:
    from joblib import Memory, dump, load
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# 🔧 CACHE MANAGER
# ═══════════════════════════════════════════════════════════════

class CacheManager:
    """
    Central cache manager for NECROZMA
    
    Features:
    - Memory-based caching with Joblib
    - Checkpoint saving/loading
    - Hash-based invalidation
    """
    
    def __init__(self, cache_dir="joblib_cache", enable=True):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory for cache files
            enable: Whether to enable caching
        """
        self.cache_dir = Path(cache_dir)
        self.enable = enable and JOBLIB_AVAILABLE
        
        if self.enable:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.memory = Memory(self.cache_dir, verbose=0)
        else:
            self.memory = None
    
    def cached(self, func):
        """
        Decorator to cache function results
        
        Usage:
            @cache_manager.cached
            def expensive_function(data, param1, param2):
                # ... computation
                return result
        """
        if not self.enable:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = self._create_cache_key(func.__name__, args, kwargs)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            # Check if cached result exists
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        result = pickle.load(f)
                    return result
                except Exception:
                    # Cache corrupted, recompute
                    pass
            
            # Compute and cache
            result = func(*args, **kwargs)
            
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
            except Exception:
                # Can't cache, just return result
                pass
            
            return result
        
        return wrapper
    
    def _create_cache_key(self, func_name, args, kwargs):
        """Create unique cache key from function and arguments"""
        # Convert arguments to string representation
        key_parts = [func_name]
        
        for arg in args:
            key_parts.append(str(type(arg).__name__))
            if hasattr(arg, 'shape'):  # numpy array
                key_parts.append(str(arg.shape))
            elif isinstance(arg, (int, float, str)):
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        # Create hash
        key_str = "_".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear(self):
        """Clear all cached data"""
        if self.enable and self.memory:
            self.memory.clear()
    
    def get_cache_size(self):
        """Get total size of cache directory in MB"""
        if not self.cache_dir.exists():
            return 0.0
        
        total_size = 0
        for file in self.cache_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        
        return total_size / (1024 * 1024)  # Convert to MB


# ═══════════════════════════════════════════════════════════════
# 💾 CHECKPOINT MANAGER
# ═══════════════════════════════════════════════════════════════

class CheckpointManager:
    """
    Checkpoint manager for saving/loading progress
    
    Features:
    - Save analysis progress at intervals
    - Resume from last checkpoint on crash
    - Metadata tracking
    """
    
    def __init__(self, checkpoint_dir="checkpoints"):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_dir: Directory for checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.current_checkpoint = None
    
    def save_checkpoint(self, name, data, metadata=None):
        """
        Save checkpoint to disk
        
        Args:
            name: Checkpoint name
            data: Data to save
            metadata: Optional metadata dict
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.checkpoint"
        
        checkpoint = {
            "name": name,
            "timestamp": time.time(),
            "data": data,
            "metadata": metadata or {}
        }
        
        try:
            dump(checkpoint, checkpoint_file)
            self.current_checkpoint = name
            return True
        except Exception as e:
            print(f"⚠️ Failed to save checkpoint {name}: {e}")
            return False
    
    def load_checkpoint(self, name):
        """
        Load checkpoint from disk
        
        Args:
            name: Checkpoint name
            
        Returns:
            dict: Checkpoint data or None if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.checkpoint"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            checkpoint = load(checkpoint_file)
            self.current_checkpoint = name
            return checkpoint
        except Exception as e:
            print(f"⚠️ Failed to load checkpoint {name}: {e}")
            return None
    
    def list_checkpoints(self):
        """
        List all available checkpoints
        
        Returns:
            list: List of checkpoint names with metadata
        """
        checkpoints = []
        
        for file in self.checkpoint_dir.glob("*.checkpoint"):
            try:
                checkpoint = load(file)
                checkpoints.append({
                    "name": checkpoint["name"],
                    "timestamp": checkpoint["timestamp"],
                    "file": str(file),
                    "metadata": checkpoint.get("metadata", {})
                })
            except Exception:
                continue
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return checkpoints
    
    def get_latest_checkpoint(self):
        """
        Get the most recent checkpoint
        
        Returns:
            dict: Latest checkpoint or None
        """
        checkpoints = self.list_checkpoints()
        if checkpoints:
            return self.load_checkpoint(checkpoints[0]["name"])
        return None
    
    def delete_checkpoint(self, name):
        """Delete a specific checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{name}.checkpoint"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            return True
        return False
    
    def clear_old_checkpoints(self, keep_last_n=5):
        """
        Keep only the N most recent checkpoints
        
        Args:
            keep_last_n: Number of recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints()
        
        for checkpoint in checkpoints[keep_last_n:]:
            self.delete_checkpoint(checkpoint["name"])


# ═══════════════════════════════════════════════════════════════
# 🔧 CONFIG HASHING
# ═══════════════════════════════════════════════════════════════

def hash_config(config_dict):
    """
    Create hash of configuration dictionary
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        str: MD5 hash of configuration
    """
    # Convert to JSON and sort keys for consistency
    config_str = json.dumps(config_dict, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()


def save_config_snapshot(config_dict, output_dir):
    """
    Save configuration snapshot with hash
    
    Args:
        config_dict: Configuration dictionary
        output_dir: Directory to save snapshot
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config_hash = hash_config(config_dict)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    snapshot = {
        "timestamp": timestamp,
        "hash": config_hash,
        "config": config_dict
    }
    
    snapshot_file = output_dir / f"config_{timestamp}_{config_hash[:8]}.json"
    
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return snapshot_file


# ═══════════════════════════════════════════════════════════════
# 🎯 GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════════════

# Default cache manager (can be overridden)
default_cache_manager = None
default_checkpoint_manager = None


def get_cache_manager(cache_dir="joblib_cache", enable=True):
    """Get or create default cache manager"""
    global default_cache_manager
    if default_cache_manager is None:
        default_cache_manager = CacheManager(cache_dir, enable)
    return default_cache_manager


def get_checkpoint_manager(checkpoint_dir="checkpoints"):
    """Get or create default checkpoint manager"""
    global default_checkpoint_manager
    if default_checkpoint_manager is None:
        default_checkpoint_manager = CheckpointManager(checkpoint_dir)
    return default_checkpoint_manager
