#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - THERMAL PROTECTION SYSTEM 💎🌟⚡

Thermal Guardian: Protect against CPU overheating during intensive analysis
"Even the Blinding One must respect the laws of thermodynamics"

Features:
- CPU temperature monitoring via multiple methods
- Automatic worker throttling based on temperature
- Background thermal monitoring thread
- Critical temperature pause/resume functionality
"""

import psutil
import threading
import time
import warnings
from typing import Optional, Dict, Callable
from pathlib import Path

warnings.filterwarnings("ignore")


# ═══════════════════════════════════════════════════════════════
# 🌡️ TEMPERATURE THRESHOLDS
# ═══════════════════════════════════════════════════════════════

THERMAL_THRESHOLDS = {
    "safe": {
        "max": 75,
        "emoji": "🟢",
        "status": "SAFE",
        "action": "continue",
        "worker_reduction": 0
    },
    "warm": {
        "max": 80,
        "emoji": "🟡",
        "status": "WARM",
        "action": "continue",
        "worker_reduction": 0
    },
    "hot": {
        "max": 85,
        "emoji": "🟠",
        "status": "HOT",
        "action": "throttle",
        "worker_reduction": 0.25  # Reduce by 25%
    },
    "very_hot": {
        "max": 90,
        "emoji": "🔴",
        "status": "VERY HOT",
        "action": "throttle",
        "worker_reduction": 0.50  # Reduce by 50%
    },
    "danger": {
        "max": 95,
        "emoji": "🚨",
        "status": "DANGER",
        "action": "throttle",
        "worker_reduction": 0.75  # Reduce to 2 workers minimum
    },
    "critical": {
        "max": 999,  # Above 95°C
        "emoji": "⛔",
        "status": "CRITICAL",
        "action": "pause",
        "worker_reduction": 1.0
    }
}


# ═══════════════════════════════════════════════════════════════
# 🌡️ CORE TEMPERATURE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_cpu_temperature() -> Optional[float]:
    """
    Get CPU temperature in Celsius using multiple methods
    
    Tries:
    1. psutil.sensors_temperatures() (Linux, Windows with proper drivers)
    2. /sys/class/thermal/thermal_zone*/temp (Linux fallback)
    
    Returns:
        float: Average CPU temperature in Celsius, or None if unavailable
    """
    temp_readings = []
    
    # Method 1: Try psutil sensors
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Look for CPU-related sensors
            for sensor_name, entries in temps.items():
                # Common CPU sensor names
                if any(keyword in sensor_name.lower() for keyword in ['cpu', 'core', 'processor', 'k10temp', 'coretemp']):
                    for entry in entries:
                        # Filter out unrealistic values
                        if 0 < entry.current < 150:
                            temp_readings.append(entry.current)
            
            # If no CPU-specific sensors, use all temperature sensors
            if not temp_readings:
                for sensor_name, entries in temps.items():
                    for entry in entries:
                        if 0 < entry.current < 150:
                            temp_readings.append(entry.current)
    except (AttributeError, OSError):
        pass
    
    # Method 2: Try Linux thermal zones (fallback)
    if not temp_readings:
        try:
            thermal_zones = list(Path("/sys/class/thermal").glob("thermal_zone*/temp"))
            for zone_file in thermal_zones:
                try:
                    with open(zone_file, 'r') as f:
                        # Read temperature (in millidegrees)
                        temp_millidegrees = int(f.read().strip())
                        temp_celsius = temp_millidegrees / 1000.0
                        if 0 < temp_celsius < 150:
                            temp_readings.append(temp_celsius)
                except (ValueError, IOError):
                    continue
        except (FileNotFoundError, PermissionError):
            pass
    
    # Return average of all readings
    if temp_readings:
        return sum(temp_readings) / len(temp_readings)
    
    return None


def check_thermal_status(temp: Optional[float]) -> dict:
    """
    Check thermal status and determine action
    
    Args:
        temp: Temperature in Celsius (or None)
    
    Returns:
        dict: {
            "status": str,      # "safe", "warm", "hot", "very_hot", "danger", "critical"
            "emoji": str,       # Visual indicator
            "action": str,      # "continue", "throttle", "pause"
            "temperature": float,
            "worker_reduction": float  # 0.0 to 1.0
        }
    
    Thresholds:
    - < 75°C: 🟢 SAFE (continue)
    - 75-80°C: 🟡 WARM (continue, log warning)
    - 80-85°C: 🟠 HOT (reduce workers by 25%)
    - 85-90°C: 🔴 VERY HOT (reduce workers by 50%)
    - 90-95°C: 🚨 DANGER (reduce to 2 workers)
    - 95°C+: ⛔ CRITICAL (pause until < 75°C)
    """
    if temp is None:
        return {
            "status": "unknown",
            "emoji": "❓",
            "action": "continue",
            "temperature": None,
            "worker_reduction": 0.0,
            "message": "Temperature monitoring unavailable"
        }
    
    # Determine thermal zone
    for zone_name, zone_config in THERMAL_THRESHOLDS.items():
        if temp < zone_config["max"]:
            return {
                "status": zone_name,
                "emoji": zone_config["emoji"],
                "action": zone_config["action"],
                "temperature": temp,
                "worker_reduction": zone_config["worker_reduction"],
                "message": f"{zone_config['emoji']} {temp:.1f}°C {zone_config['status']}"
            }
    
    # Fallback (shouldn't reach here)
    return {
        "status": "critical",
        "emoji": "⛔",
        "action": "pause",
        "temperature": temp,
        "worker_reduction": 1.0,
        "message": f"⛔ {temp:.1f}°C CRITICAL"
    }


# ═══════════════════════════════════════════════════════════════
# 🛡️ THERMAL MONITOR CLASS
# ═══════════════════════════════════════════════════════════════

class ThermalMonitor:
    """
    Background thread to monitor temperature during processing
    
    Features:
    - Periodic temperature checks
    - Automatic throttling callbacks
    - Warning emission
    - Max temperature tracking
    
    Usage:
        monitor = ThermalMonitor(check_interval=10)
        monitor.set_throttle_callback(my_throttle_function)
        monitor.start()
        # ... do work ...
        monitor.stop()
        stats = monitor.get_stats()
    """
    
    def __init__(self, check_interval: float = 10.0):
        """
        Initialize thermal monitor
        
        Args:
            check_interval: Seconds between temperature checks
        """
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.throttle_callback = None
        
        # Statistics
        self.max_temperature = None
        self.warning_count = 0
        self.throttle_count = 0
        self.pause_count = 0
        self.temperature_history = []
        
        # Current state
        self.current_temp = None
        self.current_status = None
        self.is_paused = False
    
    def set_throttle_callback(self, callback: Callable[[dict], None]):
        """
        Set callback function for thermal events
        
        The callback receives a dict with thermal status info:
        {
            "status": str,
            "emoji": str,
            "action": str,
            "temperature": float,
            "worker_reduction": float
        }
        
        Args:
            callback: Function to call when thermal status changes
        """
        self.throttle_callback = callback
    
    def start(self):
        """Start monitoring in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)"""
        last_status = None
        
        while self.running:
            try:
                # Get current temperature
                temp = get_cpu_temperature()
                self.current_temp = temp
                
                # Check thermal status
                status = check_thermal_status(temp)
                self.current_status = status
                
                # Track statistics
                if temp is not None:
                    self.temperature_history.append(temp)
                    if self.max_temperature is None or temp > self.max_temperature:
                        self.max_temperature = temp
                
                # Detect status changes
                status_changed = (last_status is None or 
                                last_status.get("status") != status.get("status"))
                
                if status_changed and status.get("action") != "continue":
                    # Count events
                    if status["action"] == "throttle":
                        self.throttle_count += 1
                        if status["status"] in ["warm", "hot"]:
                            self.warning_count += 1
                    elif status["action"] == "pause":
                        self.pause_count += 1
                        self.is_paused = True
                    
                    # Call throttle callback
                    if self.throttle_callback:
                        try:
                            self.throttle_callback(status)
                        except Exception as e:
                            print(f"⚠️ Throttle callback error: {e}")
                
                # If paused, check if we can resume
                if self.is_paused and status["action"] == "continue":
                    self.is_paused = False
                    if self.throttle_callback:
                        try:
                            self.throttle_callback({
                                **status,
                                "action": "resume"
                            })
                        except Exception as e:
                            print(f"⚠️ Resume callback error: {e}")
                
                last_status = status
                
            except Exception as e:
                print(f"⚠️ Thermal monitor error: {e}")
            
            # Wait before next check
            time.sleep(self.check_interval)
    
    def get_max_workers_for_temp(self, current_workers: int, desired_workers: int = None) -> int:
        """
        Calculate max allowed workers based on current temperature
        
        Args:
            current_workers: Current number of workers
            desired_workers: Desired number of workers (uses current if None)
        
        Returns:
            int: Adjusted number of workers
        """
        if desired_workers is None:
            desired_workers = current_workers
        
        if self.current_status is None:
            return desired_workers
        
        reduction = self.current_status.get("worker_reduction", 0.0)
        action = self.current_status.get("action", "continue")
        
        if action == "pause":
            return 0  # Pause all processing
        elif action == "throttle":
            # Reduce from desired workers
            reduced = int(desired_workers * (1.0 - reduction))
            # Minimum 1 worker (unless paused)
            return max(1, min(reduced, desired_workers))
        else:
            return desired_workers
    
    def get_stats(self) -> dict:
        """
        Get thermal monitoring statistics
        
        Returns:
            dict: Statistics including max temp, event counts, etc.
        """
        avg_temp = None
        if self.temperature_history:
            avg_temp = sum(self.temperature_history) / len(self.temperature_history)
        
        return {
            "max_temperature": self.max_temperature,
            "average_temperature": avg_temp,
            "current_temperature": self.current_temp,
            "current_status": self.current_status,
            "warning_count": self.warning_count,
            "throttle_count": self.throttle_count,
            "pause_count": self.pause_count,
            "is_paused": self.is_paused,
            "measurements": len(self.temperature_history)
        }


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🌡️ ULTRA NECROZMA - THERMAL PROTECTION TEST 🌡️          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test temperature reading
    print("\n🌡️ Testing CPU temperature reading...")
    temp = get_cpu_temperature()
    if temp:
        print(f"   ✅ CPU Temperature: {temp:.1f}°C")
    else:
        print("   ⚠️ Temperature monitoring not available on this system")
    
    # Test thermal status
    print("\n🌡️ Testing thermal status checks...")
    test_temps = [65, 78, 83, 88, 92, 97]
    for test_temp in test_temps:
        status = check_thermal_status(test_temp)
        print(f"   {status['emoji']} {test_temp}°C: {status['status'].upper()} - {status['action']}")
        if status['action'] == 'throttle':
            print(f"      → Reduce workers by {status['worker_reduction']*100:.0f}%")
    
    # Test thermal monitor
    print("\n🌡️ Testing thermal monitor (5 second test)...")
    
    event_log = []
    
    def thermal_callback(status):
        event_log.append(status)
        print(f"   📡 Event: {status['message']} - Action: {status['action']}")
    
    monitor = ThermalMonitor(check_interval=1.0)
    monitor.set_throttle_callback(thermal_callback)
    monitor.start()
    
    # Run for 5 seconds
    time.sleep(5)
    
    monitor.stop()
    
    # Show stats
    stats = monitor.get_stats()
    print("\n📊 Monitoring Statistics:")
    print(f"   Current: {stats['current_temperature']:.1f}°C" if stats['current_temperature'] else "   Current: N/A")
    print(f"   Max: {stats['max_temperature']:.1f}°C" if stats['max_temperature'] else "   Max: N/A")
    print(f"   Average: {stats['average_temperature']:.1f}°C" if stats['average_temperature'] else "   Average: N/A")
    print(f"   Measurements: {stats['measurements']}")
    print(f"   Events: {stats['warning_count']} warnings, {stats['throttle_count']} throttles, {stats['pause_count']} pauses")
    
    print("\n✅ Thermal protection test complete!")
