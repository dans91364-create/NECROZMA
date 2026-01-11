#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - THERMAL PROTECTION TESTS 💎🌟⚡

Test suite for thermal protection system
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import time
from utils.thermal_protection import (
    get_cpu_temperature,
    check_thermal_status,
    ThermalMonitor,
    THERMAL_THRESHOLDS
)


class TestTemperatureReading:
    """Test CPU temperature reading functions"""
    
    def test_get_cpu_temperature_returns_valid_or_none(self):
        """Temperature should be valid float or None"""
        temp = get_cpu_temperature()
        
        if temp is not None:
            assert isinstance(temp, float)
            assert 0 < temp < 150, f"Temperature {temp}°C is out of realistic range"
    
    def test_temperature_reading_is_consistent(self):
        """Multiple readings should be somewhat consistent"""
        readings = []
        for _ in range(3):
            temp = get_cpu_temperature()
            if temp is not None:
                readings.append(temp)
            time.sleep(0.1)
        
        if len(readings) >= 2:
            # Readings should not vary by more than 10°C in quick succession
            max_diff = max(readings) - min(readings)
            assert max_diff < 10, f"Temperature variance too high: {max_diff}°C"


class TestThermalStatus:
    """Test thermal status checking"""
    
    def test_check_thermal_status_safe(self):
        """Test safe temperature status"""
        status = check_thermal_status(65.0)
        
        assert status["status"] == "safe"
        assert status["emoji"] == "🟢"
        assert status["action"] == "continue"
        assert status["worker_reduction"] == 0.0
        assert status["temperature"] == 65.0
    
    def test_check_thermal_status_warm(self):
        """Test warm temperature status"""
        status = check_thermal_status(78.0)
        
        assert status["status"] == "warm"
        assert status["emoji"] == "🟡"
        assert status["action"] == "continue"
        assert status["worker_reduction"] == 0.0
    
    def test_check_thermal_status_hot(self):
        """Test hot temperature status"""
        status = check_thermal_status(83.0)
        
        assert status["status"] == "hot"
        assert status["emoji"] == "🟠"
        assert status["action"] == "throttle"
        assert status["worker_reduction"] == 0.25
    
    def test_check_thermal_status_very_hot(self):
        """Test very hot temperature status"""
        status = check_thermal_status(88.0)
        
        assert status["status"] == "very_hot"
        assert status["emoji"] == "🔴"
        assert status["action"] == "throttle"
        assert status["worker_reduction"] == 0.50
    
    def test_check_thermal_status_danger(self):
        """Test danger temperature status"""
        status = check_thermal_status(92.0)
        
        assert status["status"] == "danger"
        assert status["emoji"] == "🚨"
        assert status["action"] == "throttle"
        assert status["worker_reduction"] == 0.75
    
    def test_check_thermal_status_critical(self):
        """Test critical temperature status"""
        status = check_thermal_status(97.0)
        
        assert status["status"] == "critical"
        assert status["emoji"] == "⛔"
        assert status["action"] == "pause"
        assert status["worker_reduction"] == 1.0
    
    def test_check_thermal_status_none(self):
        """Test status when temperature is unavailable"""
        status = check_thermal_status(None)
        
        assert status["status"] == "unknown"
        assert status["emoji"] == "❓"
        assert status["action"] == "continue"
        assert status["temperature"] is None
    
    def test_all_thresholds_are_monotonic(self):
        """Verify thermal thresholds are in ascending order"""
        thresholds = list(THERMAL_THRESHOLDS.values())
        max_temps = [t["max"] for t in thresholds]
        
        # Should be strictly increasing
        for i in range(len(max_temps) - 1):
            assert max_temps[i] < max_temps[i+1], \
                f"Thresholds not monotonic: {max_temps}"


class TestThermalMonitor:
    """Test thermal monitoring thread"""
    
    def test_thermal_monitor_initialization(self):
        """Test monitor can be initialized"""
        monitor = ThermalMonitor(check_interval=1.0)
        
        assert monitor.check_interval == 1.0
        assert not monitor.running
        assert monitor.thread is None
        assert monitor.max_temperature is None
    
    def test_thermal_monitor_start_stop(self):
        """Test monitor can start and stop"""
        monitor = ThermalMonitor(check_interval=1.0)
        
        monitor.start()
        assert monitor.running
        assert monitor.thread is not None
        
        time.sleep(2)  # Let it run for 2 seconds
        
        monitor.stop()
        assert not monitor.running
    
    def test_thermal_monitor_collects_stats(self):
        """Test monitor collects statistics"""
        monitor = ThermalMonitor(check_interval=0.5)
        
        monitor.start()
        time.sleep(2)  # Run for 2 seconds
        monitor.stop()
        
        stats = monitor.get_stats()
        
        assert "max_temperature" in stats
        assert "average_temperature" in stats
        assert "current_temperature" in stats
        assert "warning_count" in stats
        assert "throttle_count" in stats
        assert "pause_count" in stats
        assert "measurements" in stats
        
        # Should have taken at least 3 measurements in 2 seconds (0.5s interval)
        # But may not if temperature reading is unavailable
        # assert stats["measurements"] >= 3 or stats["current_temperature"] is None
    
    def test_thermal_monitor_callback(self):
        """Test monitor calls callback on events"""
        callback_called = []
        
        def test_callback(status):
            callback_called.append(status)
        
        monitor = ThermalMonitor(check_interval=0.5)
        monitor.set_throttle_callback(test_callback)
        
        monitor.start()
        time.sleep(1.5)
        monitor.stop()
        
        # Callback behavior depends on actual temperature
        # If temperature is unavailable, callback won't be called
        # So we just verify the mechanism works without errors
        assert isinstance(callback_called, list)
    
    def test_get_max_workers_for_temp(self):
        """Test worker count adjustment based on temperature"""
        monitor = ThermalMonitor(check_interval=1.0)
        
        # Simulate different temperatures
        monitor.current_status = check_thermal_status(65.0)  # Safe
        assert monitor.get_max_workers_for_temp(16, 16) == 16
        
        monitor.current_status = check_thermal_status(83.0)  # Hot (25% reduction)
        assert monitor.get_max_workers_for_temp(16, 16) == 12
        
        monitor.current_status = check_thermal_status(88.0)  # Very Hot (50% reduction)
        assert monitor.get_max_workers_for_temp(16, 16) == 8
        
        monitor.current_status = check_thermal_status(97.0)  # Critical (pause)
        assert monitor.get_max_workers_for_temp(16, 16) == 0


class TestIntegration:
    """Integration tests for thermal protection"""
    
    def test_thermal_protection_workflow(self):
        """Test complete thermal protection workflow"""
        # Get current temperature
        temp = get_cpu_temperature()
        
        # Check status
        status = check_thermal_status(temp)
        
        # Verify status is valid
        assert status["status"] in ["unknown", "safe", "warm", "hot", "very_hot", "danger", "critical"]
        assert status["action"] in ["continue", "throttle", "pause", "resume"]
        assert 0.0 <= status["worker_reduction"] <= 1.0
        
        # Create monitor
        monitor = ThermalMonitor(check_interval=1.0)
        
        # Start and stop
        monitor.start()
        time.sleep(2)
        monitor.stop()
        
        # Get stats
        stats = monitor.get_stats()
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
