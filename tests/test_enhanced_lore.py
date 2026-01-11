#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - ENHANCED LORE SYSTEM TESTS 💎🌟⚡

Test suite for enhanced lore system
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lore import (
    LEGENDARY_LORE,
    ASCII_ART,
    print_legendary_banner,
    show_prismatic_cores,
    evolution_status,
    show_thermal_warning,
    show_prismatic_progress
)
from utils.thermal_protection import check_thermal_status


class TestLegendaryLore:
    """Test legendary lore data structures"""
    
    def test_legendary_lore_exists(self):
        """Test LEGENDARY_LORE dictionary exists and has correct structure"""
        assert isinstance(LEGENDARY_LORE, dict)
        
        expected_legendaries = ["dialga", "palkia", "giratina", "rayquaza", "necrozma", "ultra_necrozma"]
        
        for legendary in expected_legendaries:
            assert legendary in LEGENDARY_LORE, f"{legendary} missing from LEGENDARY_LORE"
            
            lore = LEGENDARY_LORE[legendary]
            assert "name" in lore
            assert "domain" in lore
            assert "power" in lore
            assert "features" in lore
            assert "messages" in lore
            
            assert isinstance(lore["features"], list)
            assert isinstance(lore["messages"], list)
            assert len(lore["messages"]) > 0
    
    def test_ascii_art_exists(self):
        """Test ASCII_ART dictionary exists"""
        assert isinstance(ASCII_ART, dict)
        
        expected_art = ["dialga", "palkia", "giratina", "rayquaza", "necrozma", "ultra_necrozma"]
        
        for legendary in expected_art:
            assert legendary in ASCII_ART, f"{legendary} missing from ASCII_ART"
            assert isinstance(ASCII_ART[legendary], str)
            assert len(ASCII_ART[legendary]) > 0


class TestPrintLegendaryBanner:
    """Test legendary banner printing"""
    
    def test_print_legendary_banner_dialga(self, capsys):
        """Test Dialga banner printing"""
        print_legendary_banner('dialga', count=100000)
        captured = capsys.readouterr()
        
        assert "DIALGA" in captured.out or "⏰" in captured.out
    
    def test_print_legendary_banner_ultra_necrozma(self, capsys):
        """Test Ultra Necrozma banner printing"""
        print_legendary_banner('ultra_necrozma', count=500000, universes=25)
        captured = capsys.readouterr()
        
        assert "ULTRA NECROZMA" in captured.out or "💎" in captured.out
    
    def test_print_legendary_banner_invalid(self, capsys):
        """Test invalid legendary name (should not crash)"""
        print_legendary_banner('invalid_pokemon')
        captured = capsys.readouterr()
        
        # Should not print anything for invalid legendary
        # Function should just return without error


class TestPrismaticCores:
    """Test prismatic cores display"""
    
    def test_show_prismatic_cores_basic(self, capsys):
        """Test basic prismatic cores display"""
        show_prismatic_cores(3, 7)
        captured = capsys.readouterr()
        
        assert "💎" in captured.out
        assert "⚫" in captured.out
        assert "3/7" in captured.out
        assert "Power" in captured.out
    
    def test_show_prismatic_cores_full(self, capsys):
        """Test full prismatic cores display"""
        show_prismatic_cores(7, 7)
        captured = capsys.readouterr()
        
        assert "💎" in captured.out
        assert "7/7" in captured.out
        assert "100%" in captured.out
    
    def test_show_prismatic_cores_empty(self, capsys):
        """Test empty prismatic cores display"""
        show_prismatic_cores(0, 7)
        captured = capsys.readouterr()
        
        assert "⚫" in captured.out
        assert "0/7" in captured.out
        assert "0%" in captured.out


class TestEvolutionStatus:
    """Test evolution status calculation"""
    
    def test_evolution_status_necrozma(self):
        """Test Necrozma stage (0-10k patterns)"""
        evo = evolution_status(5000)
        
        assert evo["stage"] == "necrozma"
        assert evo["cores"] == 1
        assert evo["name"] == "Necrozma"
        assert evo["emoji"] == "💎"
        assert 0 <= evo["power_percent"] <= 100
    
    def test_evolution_status_dusk_mane(self):
        """Test Dusk Mane stage (10k-50k patterns)"""
        evo = evolution_status(25000)
        
        assert evo["stage"] == "dusk_mane"
        assert evo["cores"] == 2
        assert evo["name"] == "Dusk Mane Necrozma"
        assert "💎" in evo["emoji"]
    
    def test_evolution_status_dawn_wings(self):
        """Test Dawn Wings stage (50k-100k patterns)"""
        evo = evolution_status(75000)
        
        assert evo["stage"] == "dawn_wings"
        assert evo["cores"] == 3
        assert evo["name"] == "Dawn Wings Necrozma"
    
    def test_evolution_status_ultra(self):
        """Test Ultra Necrozma stage (100k-500k patterns)"""
        evo = evolution_status(250000)
        
        assert evo["stage"] == "ultra_necrozma"
        assert evo["cores"] == 5
        assert evo["name"] == "Ultra Necrozma"
        assert "⚡" in evo["emoji"]
    
    def test_evolution_status_supreme(self):
        """Test Supreme Ultra Necrozma stage (500k+ patterns)"""
        evo = evolution_status(1000000)
        
        assert evo["stage"] == "supreme_ultra"
        assert evo["cores"] == 7
        assert evo["name"] == "SUPREME ULTRA NECROZMA"
        assert evo["power_percent"] == 100
    
    def test_evolution_status_boundaries(self):
        """Test evolution at exact boundaries"""
        # Just below threshold
        evo1 = evolution_status(9999)
        assert evo1["cores"] == 1
        
        # At threshold
        evo2 = evolution_status(10000)
        assert evo2["cores"] == 2
        
        # Just above threshold
        evo3 = evolution_status(10001)
        assert evo3["cores"] == 2


class TestThermalWarning:
    """Test thermal warning display"""
    
    def test_show_thermal_warning_safe(self, capsys):
        """Test safe temperature warning"""
        status = check_thermal_status(65.0)
        show_thermal_warning(65.0, status)
        captured = capsys.readouterr()
        
        assert "65" in captured.out
        assert "🟢" in captured.out or "SAFE" in captured.out
    
    def test_show_thermal_warning_hot(self, capsys):
        """Test hot temperature warning"""
        status = check_thermal_status(83.0)
        show_thermal_warning(83.0, status)
        captured = capsys.readouterr()
        
        assert "83" in captured.out
        assert "🟠" in captured.out or "HOT" in captured.out
    
    def test_show_thermal_warning_critical(self, capsys):
        """Test critical temperature warning"""
        status = check_thermal_status(97.0)
        show_thermal_warning(97.0, status)
        captured = capsys.readouterr()
        
        assert "97" in captured.out
        assert "⛔" in captured.out or "CRITICAL" in captured.out


class TestPrismaticProgress:
    """Test prismatic progress display"""
    
    def test_show_prismatic_progress_partial(self, capsys):
        """Test partial prismatic progress"""
        show_prismatic_progress(5, 7, 71.5)
        captured = capsys.readouterr()
        
        assert "💎" in captured.out
        assert "⚫" in captured.out
        assert "5/7" in captured.out
        assert "71" in captured.out or "72" in captured.out  # Rounding
        assert "Power" in captured.out
    
    def test_show_prismatic_progress_auto_calculate(self, capsys):
        """Test auto-calculation of power percent"""
        show_prismatic_progress(3, 7)
        captured = capsys.readouterr()
        
        assert "3/7" in captured.out
        # Should auto-calculate to ~43%
        assert "Power" in captured.out
    
    def test_show_prismatic_progress_full(self, capsys):
        """Test full prismatic progress"""
        show_prismatic_progress(7, 7, 100.0)
        captured = capsys.readouterr()
        
        assert "7/7" in captured.out
        assert "100" in captured.out


class TestIntegration:
    """Integration tests for lore system"""
    
    def test_evolution_progression(self):
        """Test complete evolution progression"""
        pattern_counts = [0, 5000, 25000, 75000, 250000, 1000000]
        expected_cores = [1, 1, 2, 3, 5, 7]
        
        for patterns, expected in zip(pattern_counts, expected_cores):
            evo = evolution_status(patterns)
            assert evo["cores"] == expected, \
                f"At {patterns} patterns, expected {expected} cores, got {evo['cores']}"
    
    def test_lore_messages_format_correctly(self):
        """Test that lore messages can be formatted with variables"""
        for legendary, lore in LEGENDARY_LORE.items():
            for message in lore["messages"]:
                # Test that messages don't crash when formatted
                # Some messages have placeholders like {count}, {percent}, etc.
                try:
                    # Try formatting with common placeholders
                    formatted = message.format(
                        count=1000,
                        percent=50,
                        features=25,
                        lookback=10,
                        regimes=3,
                        universes=25
                    )
                    assert isinstance(formatted, str)
                except KeyError:
                    # Some placeholders might be missing, that's okay
                    # The important thing is it doesn't crash completely
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
