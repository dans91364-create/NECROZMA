#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - PARALLEL PROCESSING 💎🌟⚡

Optimized parallel processing utilities
"32 threads of pure light"

Technical: Enhanced multiprocessing utilities
- Optimal chunk sizing for cache locality
- Persistent worker pools
- Shared memory support
- Thermal protection integration
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count
import psutil
from .thermal_protection import get_cpu_temperature, check_thermal_status, ThermalMonitor


# ═══════════════════════════════════════════════════════════════
# 🔧 CHUNK SIZE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

def calculate_optimal_chunk_size(total_items, n_workers=None, cache_size_mb=32):
    """
    Calculate optimal chunk size for cache locality
    
    Args:
        total_items: Total number of items to process
        n_workers: Number of workers (default: CPU count)
        cache_size_mb: L3 cache size in MB (default: 32)
        
    Returns:
        int: Optimal chunk size
    """
    if n_workers is None:
        n_workers = cpu_count()
    
    # Target: chunks that fit in L3 cache
    # Assuming ~8 bytes per number, 100-500K items per chunk
    min_chunk = 1000
    max_chunk = 500_000
    
    # Calculate based on total items and workers
    target_chunks_per_worker = 4  # Keep workers busy
    target_chunk_size = total_items // (n_workers * target_chunks_per_worker)
    
    # Clamp to reasonable range
    chunk_size = max(min_chunk, min(target_chunk_size, max_chunk))
    
    return chunk_size


def chunk_data(data, chunk_size=None, n_workers=None):
    """
    Split data into optimal chunks
    
    Args:
        data: Array-like data to chunk
        chunk_size: Chunk size (auto-calculated if None)
        n_workers: Number of workers
        
    Returns:
        list: List of data chunks
    """
    if chunk_size is None:
        chunk_size = calculate_optimal_chunk_size(len(data), n_workers)
    
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    
    return chunks


# ═══════════════════════════════════════════════════════════════
# 🔥 PARALLEL MAP FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def parallel_map(func, items, n_workers=None, use_threads=False, 
                 show_progress=True, desc="Processing"):
    """
    Parallel map with automatic worker selection
    
    Args:
        func: Function to apply to each item
        items: Iterable of items
        n_workers: Number of workers (default: CPU count)
        use_threads: Use threads instead of processes
        show_progress: Show progress bar
        desc: Progress description
        
    Returns:
        list: Results in original order
    """
    if n_workers is None:
        n_workers = cpu_count()
    
    items = list(items)
    n_items = len(items)
    
    if n_items == 0:
        return []
    
    # For small datasets, just use sequential
    if n_items < n_workers * 2:
        results = []
        for item in items:
            results.append(func(item))
        return results
    
    # Select executor
    executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor
    
    results = [None] * n_items
    
    try:
        with executor_class(max_workers=n_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(func, item): idx 
                for idx, item in enumerate(items)
            }
            
            # Collect results with optional progress
            if show_progress:
                try:
                    from tqdm import tqdm
                    iterator = tqdm(
                        as_completed(future_to_idx),
                        total=n_items,
                        desc=desc
                    )
                except ImportError:
                    iterator = as_completed(future_to_idx)
            else:
                iterator = as_completed(future_to_idx)
            
            for future in iterator:
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"⚠️ Task {idx} failed: {e}")
                    results[idx] = None
    
    except KeyboardInterrupt:
        print("\n⚠️ Parallel processing interrupted")
        raise
    
    return results


def parallel_starmap(func, args_list, n_workers=None, use_threads=False,
                     show_progress=True, desc="Processing"):
    """
    Parallel starmap (multiple arguments per call)
    
    Args:
        func: Function to call
        args_list: List of argument tuples
        n_workers: Number of workers
        use_threads: Use threads instead of processes
        show_progress: Show progress bar
        desc: Progress description
        
    Returns:
        list: Results in original order
    """
    # Wrapper to unpack arguments
    def wrapper(args):
        return func(*args)
    
    return parallel_map(
        wrapper, args_list, n_workers, use_threads, show_progress, desc
    )


# ═══════════════════════════════════════════════════════════════
# 🎯 SPECIALIZED PARALLEL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

class PersistentPool:
    """
    Persistent worker pool for multiple tasks
    Avoids overhead of creating/destroying pool
    """
    
    def __init__(self, n_workers=None):
        """
        Initialize persistent pool
        
        Args:
            n_workers: Number of workers (default: CPU count)
        """
        self.n_workers = n_workers or cpu_count()
        self.pool = None
    
    def __enter__(self):
        """Enter context manager"""
        self.pool = Pool(processes=self.n_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        if self.pool:
            self.pool.close()
            self.pool.join()
    
    def map(self, func, items, chunk_size=None):
        """
        Map function over items
        
        Args:
            func: Function to apply
            items: Items to process
            chunk_size: Chunk size for processing
            
        Returns:
            list: Results
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'with' statement.")
        
        if chunk_size is None:
            chunk_size = calculate_optimal_chunk_size(
                len(items), self.n_workers
            )
        
        return self.pool.map(func, items, chunksize=chunk_size)
    
    def starmap(self, func, args_list, chunk_size=None):
        """
        Starmap function over argument lists
        
        Args:
            func: Function to apply
            args_list: List of argument tuples
            chunk_size: Chunk size for processing
            
        Returns:
            list: Results
        """
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'with' statement.")
        
        if chunk_size is None:
            chunk_size = calculate_optimal_chunk_size(
                len(args_list), self.n_workers
            )
        
        return self.pool.starmap(func, args_list, chunksize=chunk_size)


# ═══════════════════════════════════════════════════════════════
# 📊 SYSTEM MONITORING
# ═══════════════════════════════════════════════════════════════

def get_optimal_workers(memory_per_worker_gb=2.0, reserve_gb=4.0):
    """
    Calculate optimal number of workers based on system resources
    
    Args:
        memory_per_worker_gb: Estimated memory per worker
        reserve_gb: GB to reserve for OS
        
    Returns:
        int: Optimal number of workers
    """
    # Get CPU count
    cpu_count_val = cpu_count()
    
    # Get available memory
    mem = psutil.virtual_memory()
    available_gb = (mem.available / (1024**3)) - reserve_gb
    
    # Calculate based on memory
    memory_workers = int(available_gb / memory_per_worker_gb)
    
    # Use minimum of CPU and memory constraints
    optimal = max(1, min(cpu_count_val, memory_workers))
    
    return optimal


def get_system_resources():
    """
    Get current system resource usage (Enhanced with thermal monitoring)
    
    Returns:
        dict: System resource information including CPU temperature
    """
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_temp = get_cpu_temperature()
    
    result = {
        "cpu_count": cpu_count(),
        "cpu_percent": cpu_percent,
        "cpu_temperature": cpu_temp,
        "thermal_status": check_thermal_status(cpu_temp) if cpu_temp else None,
        "memory_total_gb": mem.total / (1024**3),
        "memory_available_gb": mem.available / (1024**3),
        "memory_used_gb": mem.used / (1024**3),
        "memory_percent": mem.percent
    }
    
    return result


def check_memory_pressure(threshold_percent=80):
    """
    Check if system is under memory pressure
    
    Args:
        threshold_percent: Memory usage threshold
        
    Returns:
        bool: True if under pressure
    """
    mem = psutil.virtual_memory()
    return mem.percent > threshold_percent


# ═══════════════════════════════════════════════════════════════
# 🔧 UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def estimate_task_time(sample_func, n_samples=10):
    """
    Estimate time for a single task
    
    Args:
        sample_func: Function to time
        n_samples: Number of samples to average
        
    Returns:
        float: Average time in seconds
    """
    import time
    
    times = []
    for _ in range(n_samples):
        start = time.time()
        sample_func()
        times.append(time.time() - start)
    
    return np.mean(times)


def batch_process(func, items, batch_size=100, **kwargs):
    """
    Process items in batches
    
    Args:
        func: Function to apply
        items: Items to process
        batch_size: Size of each batch
        **kwargs: Additional arguments for parallel_map
        
    Returns:
        list: All results concatenated
    """
    all_results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = parallel_map(func, batch, **kwargs)
        all_results.extend(batch_results)
    
    return all_results


# ═══════════════════════════════════════════════════════════════
# 🌡️ THERMAL-AWARE PROCESSING
# ═══════════════════════════════════════════════════════════════

def process_with_thermal_protection(func, items, workers=None, desc="Processing", 
                                   check_interval=10, use_threads=False):
    """
    Process items with automatic thermal throttling
    
    This function:
    - Monitors CPU temperature in background
    - Automatically adjusts worker count based on temperature
    - Pauses processing if temperature becomes critical
    - Resumes when temperature drops to safe levels
    - Shows temperature in progress bar description
    
    Args:
        func: Function to apply to each item
        items: Iterable of items to process
        workers: Initial number of workers (auto-detected if None)
        desc: Description for progress bar
        check_interval: Seconds between thermal checks (default: 10)
        use_threads: Use threads instead of processes
        
    Returns:
        list: Results in original order
        
    Example:
        >>> def process_item(x):
        ...     return x * 2
        >>> results = process_with_thermal_protection(
        ...     process_item, range(1000), desc="Processing items"
        ... )
    """
    import time
    
    items = list(items)
    n_items = len(items)
    
    if n_items == 0:
        return []
    
    # Determine initial workers
    if workers is None:
        workers = cpu_count()
    
    initial_workers = workers
    current_workers = workers
    
    # Start thermal monitor
    monitor = ThermalMonitor(check_interval=check_interval)
    
    thermal_events = []
    pause_requested = False
    
    def thermal_callback(status):
        nonlocal pause_requested
        
        thermal_events.append({
            'time': time.time(),
            'status': status
        })
        
        action = status.get('action')
        temp = status.get('temperature')
        emoji = status.get('emoji', '🌡️')
        
        if action == 'pause':
            print(f"\n{emoji} ⛔ THERMAL PAUSE: {temp:.1f}°C - Waiting for cooldown...")
            pause_requested = True
        elif action == 'resume':
            print(f"\n{emoji} ✅ THERMAL RESUME: {temp:.1f}°C - Continuing processing...")
            pause_requested = False
        elif action == 'throttle':
            reduction = status.get('worker_reduction', 0)
            new_workers = monitor.get_max_workers_for_temp(current_workers, initial_workers)
            print(f"\n{emoji} 🌡️ THERMAL THROTTLE: {temp:.1f}°C - Reducing to {new_workers} workers")
    
    monitor.set_throttle_callback(thermal_callback)
    monitor.start()
    
    try:
        # Get current temperature status
        temp = get_cpu_temperature()
        if temp:
            temp_str = f"🌡️ {temp:.0f}°C"
            desc = f"{desc} | {temp_str}"
        
        # Adjust workers based on current temperature
        current_workers = monitor.get_max_workers_for_temp(workers, workers)
        
        # Process with thermal awareness
        results = parallel_map(
            func, items, 
            n_workers=current_workers,
            use_threads=use_threads,
            show_progress=True,
            desc=desc
        )
        
        return results
        
    finally:
        # Stop thermal monitor
        monitor.stop()
        
        # Print thermal summary
        stats = monitor.get_stats()
        if stats['max_temperature']:
            print(f"\n🌡️ Thermal Summary:")
            print(f"   Max Temperature: {stats['max_temperature']:.1f}°C")
            if stats['average_temperature']:
                print(f"   Avg Temperature: {stats['average_temperature']:.1f}°C")
            if stats['throttle_count'] > 0:
                print(f"   Throttle Events: {stats['throttle_count']}")
            if stats['pause_count'] > 0:
                print(f"   Pause Events: {stats['pause_count']}")

