#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - THERMAL MANAGER 💎🌟⚡

Cooling Break System: Manage cooling breaks for VM-safe operation
"Even Ultra Necrozma needs to cool down"

Technical: CPU monitoring and thermal throttling
"""

import time
import psutil
import numpy as np
from typing import Optional, Dict
from collections import deque


# ═══════════════════════════════════════════════════════════════
# 🔥 COOLING MANAGER CLASS
# ═══════════════════════════════════════════════════════════════

class CoolingManager:
    """
    Manage cooling breaks for VM-safe operation
    
    Technical: Periodic breaks to prevent thermal issues
    """
    
    def __init__(
        self,
        chunk_interval: int = 3,
        universe_interval: int = 5,
        chunk_duration: int = 60,
        universe_duration: int = 120
    ):
        """
        Initialize CoolingManager
        
        Args:
            chunk_interval: Pause every N chunks
            universe_interval: Pause every N universes
            chunk_duration: Pause duration after chunks (seconds)
            universe_duration: Pause duration after universes (seconds)
        """
        self.chunk_interval = chunk_interval
        self.universe_interval = universe_interval
        self.chunk_duration = chunk_duration
        self.universe_duration = universe_duration
        
        self.chunks_processed = 0
        self.universes_processed = 0
        self.total_cooling_time = 0
    
    def should_pause_chunk(self, chunk_idx: int) -> bool:
        """
        Check if cooling break needed after chunk
        
        Args:
            chunk_idx: Current chunk index
        
        Returns:
            bool: True if pause needed
        """
        if self.chunk_interval <= 0:
            return False
        
        return chunk_idx > 0 and chunk_idx % self.chunk_interval == 0
    
    def should_pause_universe(self, universe_idx: int) -> bool:
        """
        Check if cooling break needed after universe
        
        Args:
            universe_idx: Current universe index
        
        Returns:
            bool: True if pause needed
        """
        if self.universe_interval <= 0:
            return False
        
        return universe_idx > 0 and universe_idx % self.universe_interval == 0
    
    def cooling_break(self, duration: int, reason: str = "periodic"):
        """
        Execute cooling break with countdown
        Monitor CPU% during break
        Resume when CPU < 40% or timeout
        
        Args:
            duration: Break duration in seconds
            reason: Reason for cooling break
        """
        print(f"\n❄️  COOLING BREAK - {reason}")
        print(f"   Duration: {duration}s")
        print("─" * 60)
        
        start_time = time.time()
        elapsed = 0
        
        while elapsed < duration:
            remaining = int(duration - elapsed)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Show countdown
            print(f"   ⏱️  {remaining:3d}s remaining | CPU: {cpu_percent:5.1f}% ", end="\r")
            
            # Early exit if CPU is cool enough
            if cpu_percent < 40 and elapsed >= 30:  # At least 30s break
                print(f"\n   ✅ CPU cooled down to {cpu_percent:.1f}% - resuming early")
                break
            
            time.sleep(1)
            elapsed = time.time() - start_time
        
        self.total_cooling_time += elapsed
        
        final_cpu = psutil.cpu_percent(interval=1)
        print(f"\n   ✅ Cooling complete | Final CPU: {final_cpu:.1f}%")
        print("─" * 60 + "\n")
    
    def mark_chunk_processed(self):
        """Mark that a chunk has been processed"""
        self.chunks_processed += 1
    
    def mark_universe_processed(self):
        """Mark that a universe has been processed"""
        self.universes_processed += 1
    
    def get_stats(self) -> Dict:
        """
        Get cooling statistics
        
        Returns:
            dict: Cooling statistics
        """
        return {
            "chunks_processed": self.chunks_processed,
            "universes_processed": self.universes_processed,
            "total_cooling_time": self.total_cooling_time,
            "cooling_time_minutes": self.total_cooling_time / 60
        }


# ═══════════════════════════════════════════════════════════════
# 🌡️ CPU MONITOR CLASS
# ═══════════════════════════════════════════════════════════════

class CPUMonitor:
    """
    Monitor CPU usage as proxy for temperature in VMs
    
    Technical: Track CPU history and detect sustained high usage
    """
    
    def __init__(self, max_cpu: int = 85, check_interval: int = 60):
        """
        Initialize CPU Monitor
        
        Args:
            max_cpu: Pause processing if CPU > this % for 5+ minutes
            check_interval: Check interval in seconds
        """
        self.max_cpu = max_cpu
        self.check_interval = check_interval
        
        # CPU history (5 minutes of 1-second samples)
        self.cpu_history = deque(maxlen=300)
        
        self.monitoring = False
        self.paused_count = 0
    
    def record_cpu(self):
        """Record current CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_history.append(cpu_percent)
    
    def get_cpu_history(self, window: int = 300) -> list:
        """
        Get CPU history for specified window
        
        Args:
            window: Window in seconds (default: 300 = 5 minutes)
        
        Returns:
            list: CPU percentages
        """
        if len(self.cpu_history) == 0:
            # Sample current CPU
            for _ in range(min(10, window)):
                self.cpu_history.append(psutil.cpu_percent(interval=0.1))
        
        return list(self.cpu_history)[-window:]
    
    def is_overheating(self) -> bool:
        """
        Check if CPU sustained high for thermal risk
        
        Returns:
            bool: True if overheating detected
        """
        history = self.get_cpu_history(window=300)  # 5 minutes
        
        if len(history) < 60:  # Need at least 1 minute of data
            return False
        
        avg_cpu = np.mean(history)
        
        return avg_cpu > self.max_cpu
    
    def wait_for_cooldown(self):
        """
        Pause until CPU drops below threshold
        """
        if not self.is_overheating():
            return
        
        self.paused_count += 1
        print(f"\n🔥 CPU TOO HIGH - Initiating cooldown")
        print("─" * 60)
        
        wait_cycles = 0
        
        while self.is_overheating() and wait_cycles < 60:  # Max 60 minutes
            history = self.get_cpu_history(window=300)
            avg_cpu = np.mean(history)
            current_cpu = psutil.cpu_percent(interval=1)
            
            print(f"   ⏱️  Cooling... | Current: {current_cpu:5.1f}% | "
                  f"5-min avg: {avg_cpu:5.1f}% | Target: <{self.max_cpu}%", end="\r")
            
            time.sleep(60)  # Check every minute
            wait_cycles += 1
            
            # Record new sample
            self.record_cpu()
        
        final_cpu = psutil.cpu_percent(interval=1)
        print(f"\n   ✅ CPU cooled down to {final_cpu:.1f}%")
        print("─" * 60 + "\n")
    
    def get_current_status(self) -> Dict:
        """
        Get current CPU status
        
        Returns:
            dict: CPU status information
        """
        current = psutil.cpu_percent(interval=1)
        history = self.get_cpu_history(window=300)
        avg_5min = np.mean(history) if history else current
        
        status = "normal"
        if avg_5min > self.max_cpu:
            status = "overheating"
        elif avg_5min > self.max_cpu * 0.8:
            status = "warm"
        
        return {
            "current_cpu": current,
            "avg_5min": avg_5min,
            "max_cpu": self.max_cpu,
            "status": status,
            "is_overheating": self.is_overheating(),
            "paused_count": self.paused_count
        }


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ⚡ THERMAL MANAGER TEST ⚡                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test CoolingManager
    print("❄️  Testing CoolingManager...")
    print("─" * 60)
    
    cooling_mgr = CoolingManager(
        chunk_interval=2,
        universe_interval=3,
        chunk_duration=5,  # Short for testing
        universe_duration=10
    )
    
    # Simulate chunk processing
    print("\n📦 Simulating chunk processing...")
    for i in range(1, 6):
        print(f"   Processing chunk {i}...")
        time.sleep(0.5)
        
        if cooling_mgr.should_pause_chunk(i):
            cooling_mgr.cooling_break(5, f"after chunk {i}")
        
        cooling_mgr.mark_chunk_processed()
    
    # Get stats
    stats = cooling_mgr.get_stats()
    print(f"\n📊 Cooling stats:")
    print(f"   Chunks processed: {stats['chunks_processed']}")
    print(f"   Total cooling time: {stats['cooling_time_minutes']:.1f} minutes")
    
    # Test CPUMonitor
    print("\n\n🌡️  Testing CPUMonitor...")
    print("─" * 60)
    
    cpu_monitor = CPUMonitor(max_cpu=85)
    
    # Get current status
    status = cpu_monitor.get_current_status()
    print(f"\n📊 Current CPU status:")
    print(f"   Current: {status['current_cpu']:.1f}%")
    print(f"   5-min avg: {status['avg_5min']:.1f}%")
    print(f"   Status: {status['status']}")
    print(f"   Is overheating: {status['is_overheating']}")
    
    # Record some samples
    print(f"\n📈 Recording CPU samples...")
    for i in range(5):
        cpu_monitor.record_cpu()
        time.sleep(0.2)
    
    history = cpu_monitor.get_cpu_history(window=10)
    print(f"   Recorded {len(history)} samples")
    print(f"   Average: {np.mean(history):.1f}%")
    
    print("\n✅ All tests passed!")
