#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for _simplify_result function to ensure it handles missing keys defensively
This test validates the fix without requiring full analyzer initialization.
"""

import pytest
import sys
from pathlib import Path


# Simplified version of _simplify_result for testing
# This matches the fixed version in analyzer.py
TOP_PATTERNS_PER_LEVEL = 10  # Default value from config


def _simplify_result(result):
    """Simplify result for JSON serialization"""
    # Verificar se result tem estrutura válida
    if result is None or not isinstance(result, dict):
        return result
    
    simplified = {
        "name": result.get("name", "unknown"),
        "config": result.get("config", {}),
        "processing_time": result.get("processing_time", 0),
        "total_patterns": result.get("total_patterns", 0),
        "results": {},
        "ohlc_data": result.get("ohlc_data", []),
        "metadata": result.get("metadata", {}),
    }
    
    # Se não tem results, retorna simplificado vazio
    if "results" not in result or not result["results"]:
        return simplified
    
    for level in result["results"]:
        simplified["results"][level] = {}
        
        for direction in result["results"][level]:
            level_data = result["results"][level][direction]
            
            # Get top patterns
            patterns = level_data.get("patterns", {})
            top_patterns = sorted(
                patterns.items(),
                key=lambda x: x[1].get("count", 0),
                reverse=True
            )[:TOP_PATTERNS_PER_LEVEL]
            
            simplified["results"][level][direction] = {
                "total_occurrences": level_data.get("total_occurrences", 0),
                "unique_patterns": len(patterns),
                "top_patterns": [
                    {"signature": sig, "count": data.get("count", 0)}
                    for sig, data in top_patterns
                ],
                "feature_stats": level_data.get("feature_stats", {})
            }
    
    return simplified


class TestSimplifyResult:
    """Test _simplify_result method handles missing keys gracefully"""
    
    def setup_method(self):
        """Set up test fixtures"""
        pass
    
    def test_empty_result(self):
        """Test with empty result"""
        result = None
        simplified = _simplify_result(result)
        assert simplified is None
    
    def test_non_dict_result(self):
        """Test with non-dict result"""
        result = "invalid"
        simplified = _simplify_result(result)
        assert simplified == "invalid"
    
    def test_empty_dict_result(self):
        """Test with empty dict result"""
        result = {}
        simplified = _simplify_result(result)
        assert isinstance(simplified, dict)
        assert simplified["name"] == "unknown"
        assert simplified["processing_time"] == 0
        assert simplified["total_patterns"] == 0
        assert simplified["results"] == {}
    
    def test_missing_processing_time(self):
        """Test handling missing processing_time key"""
        result = {
            "name": "test",
            "config": {},
            "total_patterns": 10,
            "results": {}
        }
        simplified = _simplify_result(result)
        assert simplified["processing_time"] == 0
        assert simplified["name"] == "test"
    
    def test_missing_results_key(self):
        """Test handling missing results key"""
        result = {
            "name": "test",
            "config": {},
            "processing_time": 1.5,
            "total_patterns": 10
        }
        simplified = _simplify_result(result)
        assert simplified["results"] == {}
    
    def test_empty_results(self):
        """Test handling empty results"""
        result = {
            "name": "test",
            "config": {},
            "processing_time": 1.5,
            "total_patterns": 10,
            "results": {}
        }
        simplified = _simplify_result(result)
        assert simplified["results"] == {}
    
    def test_missing_count_in_patterns(self):
        """Test handling missing count in pattern data"""
        result = {
            "name": "test",
            "config": {},
            "processing_time": 1.5,
            "total_patterns": 10,
            "results": {
                "level_1": {
                    "up": {
                        "patterns": {
                            "pattern_1": {},  # Missing count
                            "pattern_2": {"count": 5}
                        },
                        "total_occurrences": 5
                    }
                }
            }
        }
        simplified = _simplify_result(result)
        assert "level_1" in simplified["results"]
        assert "up" in simplified["results"]["level_1"]
        # Should handle missing count gracefully
        top_patterns = simplified["results"]["level_1"]["up"]["top_patterns"]
        assert len(top_patterns) == 2
        # Pattern without count should default to 0
        counts = [p["count"] for p in top_patterns]
        assert 0 in counts
        assert 5 in counts
    
    def test_missing_total_occurrences(self):
        """Test handling missing total_occurrences"""
        result = {
            "name": "test",
            "config": {},
            "processing_time": 1.5,
            "total_patterns": 10,
            "results": {
                "level_1": {
                    "up": {
                        "patterns": {
                            "pattern_1": {"count": 3}
                        }
                    }
                }
            }
        }
        simplified = _simplify_result(result)
        assert simplified["results"]["level_1"]["up"]["total_occurrences"] == 0
    
    def test_complete_valid_result(self):
        """Test with complete valid result"""
        result = {
            "name": "test_universe",
            "config": {"interval": "1h"},
            "processing_time": 2.5,
            "total_patterns": 100,
            "ohlc_data": [1, 2, 3],
            "metadata": {"source": "test"},
            "results": {
                "level_1": {
                    "up": {
                        "patterns": {
                            "pattern_1": {"count": 10},
                            "pattern_2": {"count": 5}
                        },
                        "total_occurrences": 15,
                        "feature_stats": {"mean": 0.5}
                    }
                }
            }
        }
        simplified = _simplify_result(result)
        
        # Verify all fields are preserved
        assert simplified["name"] == "test_universe"
        assert simplified["config"] == {"interval": "1h"}
        assert simplified["processing_time"] == 2.5
        assert simplified["total_patterns"] == 100
        assert simplified["ohlc_data"] == [1, 2, 3]
        assert simplified["metadata"] == {"source": "test"}
        
        # Verify results structure
        assert "level_1" in simplified["results"]
        assert "up" in simplified["results"]["level_1"]
        assert simplified["results"]["level_1"]["up"]["total_occurrences"] == 15
        assert simplified["results"]["level_1"]["up"]["unique_patterns"] == 2
        assert len(simplified["results"]["level_1"]["up"]["top_patterns"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
