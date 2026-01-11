#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test enhanced Telegram notifications

Verifies that:
1. LoreSystem can be initialized with enable_telegram=False
2. Broadcast method works correctly
3. New event types are defined
4. Messages are formatted properly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lore import LoreSystem, EventType


def test_lore_system_initialization():
    """Test that LoreSystem can be initialized with telegram disabled"""
    # Should work without telegram
    lore = LoreSystem(enable_telegram=False)
    assert lore.telegram_enabled == False
    assert lore.telegram_notifier is None
    

def test_new_event_types_exist():
    """Test that new event types are defined"""
    assert hasattr(EventType, 'SYSTEM_INIT')
    assert hasattr(EventType, 'SYSTEM_CHECK')
    assert hasattr(EventType, 'DATA_LOADING')
    assert hasattr(EventType, 'DATA_LOADED')
    assert hasattr(EventType, 'ANALYSIS_START')
    assert hasattr(EventType, 'UNIVERSE_PROGRESS')


def test_broadcast_with_telegram_disabled():
    """Test that broadcast works when telegram is disabled"""
    lore = LoreSystem(enable_telegram=False)
    
    # Should not crash when telegram is disabled
    lore.broadcast(EventType.SYSTEM_INIT, message="Test message")
    lore.broadcast(EventType.SYSTEM_CHECK, status="pass")
    lore.broadcast(EventType.DATA_LOADING, filename="test.csv")
    lore.broadcast(EventType.DATA_LOADED, rows=1000)
    lore.broadcast(EventType.ANALYSIS_START, num_universes=25)
    lore.broadcast(EventType.UNIVERSE_PROGRESS, completed=5, total=25, percentage=20.0)
    
    # If we get here without exception, test passes
    assert True


def test_deity_quotes_for_new_events():
    """Test that deity quotes are defined for new event types"""
    lore = LoreSystem(enabled=True, enable_telegram=False)
    
    # Check that quotes exist for new event types
    assert EventType.SYSTEM_INIT in lore.deities["ARCEUS"].quotes
    assert EventType.SYSTEM_CHECK in lore.deities["ARCEUS"].quotes
    assert EventType.DATA_LOADING in lore.deities["NECROZMA"].quotes
    assert EventType.DATA_LOADED in lore.deities["NECROZMA"].quotes
    assert EventType.ANALYSIS_START in lore.deities["NECROZMA"].quotes
    assert EventType.UNIVERSE_PROGRESS in lore.deities["NECROZMA"].quotes


def test_speak_with_new_events():
    """Test that speak method works with new event types"""
    lore = LoreSystem(enabled=True, enable_telegram=False)
    
    # Test each new event type
    msg1 = lore.speak("ARCEUS", EventType.SYSTEM_INIT)
    assert msg1  # Should return a non-empty string
    assert "ARCEUS" in msg1 or "⚪" in msg1
    
    msg2 = lore.speak("ARCEUS", EventType.SYSTEM_CHECK)
    assert msg2
    assert "ARCEUS" in msg2 or "⚪" in msg2
    
    msg3 = lore.speak("NECROZMA", EventType.DATA_LOADING)
    assert msg3
    assert "NECROZMA" in msg3 or "🌟" in msg3
    
    msg4 = lore.speak("NECROZMA", EventType.DATA_LOADED, rows=1000)
    assert msg4
    
    msg5 = lore.speak("NECROZMA", EventType.ANALYSIS_START, num_universes=25)
    assert msg5
    
    msg6 = lore.speak("NECROZMA", EventType.UNIVERSE_PROGRESS, 
                      completed=5, total=25, percentage=20.0)
    assert msg6


if __name__ == "__main__":
    # Run tests manually
    print("Running Telegram notification tests...\n")
    
    test_lore_system_initialization()
    print("✅ LoreSystem initialization test passed")
    
    test_new_event_types_exist()
    print("✅ New event types test passed")
    
    test_broadcast_with_telegram_disabled()
    print("✅ Broadcast with telegram disabled test passed")
    
    test_deity_quotes_for_new_events()
    print("✅ Deity quotes for new events test passed")
    
    test_speak_with_new_events()
    print("✅ Speak with new events test passed")
    
    print("\n✨ All tests passed!")
