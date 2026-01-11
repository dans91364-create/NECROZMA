#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TEMPORAL FEATURES 💎🌟⚡

Temporal and Market Session Features
"Time reveals hidden patterns"

Technical: Time-based feature extraction
- Day of week, hour of day features
- Market session detection (Tokyo, London, NY)
- Session overlaps and volatility patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, time


# ═══════════════════════════════════════════════════════════════
# 🌟 TEMPORAL FEATURES
# ═══════════════════════════════════════════════════════════════

def extract_temporal_features(timestamps):
    """
    Extract temporal features from timestamps
    
    Args:
        timestamps: Array or Series of timestamps
        
    Returns:
        dict: Temporal features
    """
    features = {}
    
    if isinstance(timestamps, (list, np.ndarray)):
        timestamps = pd.to_datetime(timestamps)
    
    if len(timestamps) == 0:
        return features
    
    # Use most recent timestamp for features
    latest = timestamps.iloc[-1] if isinstance(timestamps, pd.Series) else timestamps[-1]
    
    # Day of week (0 = Monday, 4 = Friday)
    features["day_of_week"] = int(latest.dayofweek)
    
    # Hour of day (0-23)
    features["hour_of_day"] = int(latest.hour)
    
    # Minute of hour (0-59)
    features["minute_of_hour"] = int(latest.minute)
    
    # Is Monday / Friday (more volatile)
    features["is_monday"] = 1 if latest.dayofweek == 0 else 0
    features["is_friday"] = 1 if latest.dayofweek == 4 else 0
    
    # Time of day categories
    hour = latest.hour
    features["is_market_open"] = 1 if 8 <= hour < 17 else 0  # 8am-5pm
    features["is_market_close"] = 1 if 16 <= hour < 17 else 0  # 4-5pm
    features["is_night"] = 1 if hour < 6 or hour >= 22 else 0
    features["is_morning"] = 1 if 6 <= hour < 12 else 0
    features["is_afternoon"] = 1 if 12 <= hour < 17 else 0
    features["is_evening"] = 1 if 17 <= hour < 22 else 0
    
    # Cyclical encoding (for ML models)
    # Day of week (circular)
    features["day_of_week_sin"] = float(np.sin(2 * np.pi * latest.dayofweek / 7))
    features["day_of_week_cos"] = float(np.cos(2 * np.pi * latest.dayofweek / 7))
    
    # Hour of day (circular)
    features["hour_of_day_sin"] = float(np.sin(2 * np.pi * hour / 24))
    features["hour_of_day_cos"] = float(np.cos(2 * np.pi * hour / 24))
    
    # Minute (circular)
    features["minute_sin"] = float(np.sin(2 * np.pi * latest.minute / 60))
    features["minute_cos"] = float(np.cos(2 * np.pi * latest.minute / 60))
    
    return features


# ═══════════════════════════════════════════════════════════════
# 💎 MARKET SESSION FEATURES
# ═══════════════════════════════════════════════════════════════

def get_market_session(timestamp):
    """
    Determine which market session(s) are active
    
    Sessions (UTC):
    - Tokyo: 00:00 - 09:00
    - London: 08:00 - 16:30
    - New York: 13:00 - 22:00
    
    Args:
        timestamp: Timestamp to check
        
    Returns:
        dict: Session information
    """
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)
    
    # Convert to UTC time
    hour = timestamp.hour
    minute = timestamp.minute
    time_decimal = hour + minute / 60
    
    sessions = {
        "tokyo": 0,
        "london": 0,
        "new_york": 0,
        "london_ny_overlap": 0,
        "tokyo_london_overlap": 0
    }
    
    # Tokyo session: 00:00 - 09:00 UTC
    if 0 <= time_decimal < 9:
        sessions["tokyo"] = 1
    
    # London session: 08:00 - 16:30 UTC
    if 8 <= time_decimal < 16.5:
        sessions["london"] = 1
    
    # New York session: 13:00 - 22:00 UTC
    if 13 <= time_decimal < 22:
        sessions["new_york"] = 1
    
    # Overlaps (high volatility periods)
    # Tokyo-London overlap: 08:00 - 09:00
    if 8 <= time_decimal < 9:
        sessions["tokyo_london_overlap"] = 1
    
    # London-NY overlap: 13:00 - 16:30 (most liquid)
    if 13 <= time_decimal < 16.5:
        sessions["london_ny_overlap"] = 1
    
    # Active session count
    sessions["active_sessions"] = sum([
        sessions["tokyo"],
        sessions["london"],
        sessions["new_york"]
    ])
    
    # Primary session
    if sessions["london_ny_overlap"]:
        sessions["primary_session"] = "london_ny_overlap"
    elif sessions["tokyo_london_overlap"]:
        sessions["primary_session"] = "tokyo_london_overlap"
    elif sessions["london"]:
        sessions["primary_session"] = "london"
    elif sessions["new_york"]:
        sessions["primary_session"] = "new_york"
    elif sessions["tokyo"]:
        sessions["primary_session"] = "tokyo"
    else:
        sessions["primary_session"] = "off_hours"
    
    return sessions


def extract_session_features(timestamps):
    """
    Extract market session features from timestamps
    
    Args:
        timestamps: Array or Series of timestamps
        
    Returns:
        dict: Session features
    """
    features = {}
    
    if isinstance(timestamps, (list, np.ndarray)):
        timestamps = pd.to_datetime(timestamps)
    
    if len(timestamps) == 0:
        return features
    
    # Use most recent timestamp
    latest = timestamps.iloc[-1] if isinstance(timestamps, pd.Series) else timestamps[-1]
    
    # Get session info
    session_info = get_market_session(latest)
    
    # Add as features
    features["is_tokyo_session"] = session_info["tokyo"]
    features["is_london_session"] = session_info["london"]
    features["is_ny_session"] = session_info["new_york"]
    features["is_london_ny_overlap"] = session_info["london_ny_overlap"]
    features["is_tokyo_london_overlap"] = session_info["tokyo_london_overlap"]
    features["active_sessions_count"] = session_info["active_sessions"]
    
    # Session time elapsed/remaining (for current session)
    hour = latest.hour
    minute = latest.minute
    time_decimal = hour + minute / 60
    
    # Calculate time in session
    if session_info["london"]:
        # London: 08:00 - 16:30 (8.5 hours)
        session_start = 8.0
        session_end = 16.5
        session_duration = 8.5
    elif session_info["new_york"]:
        # NY: 13:00 - 22:00 (9 hours)
        session_start = 13.0
        session_end = 22.0
        session_duration = 9.0
    elif session_info["tokyo"]:
        # Tokyo: 00:00 - 09:00 (9 hours)
        session_start = 0.0
        session_end = 9.0
        session_duration = 9.0
    else:
        session_start = 0.0
        session_end = 0.0
        session_duration = 1.0
    
    if session_duration > 0:
        elapsed = (time_decimal - session_start) / session_duration
        remaining = (session_end - time_decimal) / session_duration
        
        features["session_time_elapsed"] = float(max(0, min(1, elapsed)))
        features["session_time_remaining"] = float(max(0, min(1, remaining)))
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎯 COMBINED FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_all_temporal_features(timestamps):
    """
    Extract all temporal and session features
    
    Args:
        timestamps: Array or Series of timestamps
        
    Returns:
        dict: All temporal features
    """
    features = {}
    
    # Temporal features
    temporal = extract_temporal_features(timestamps)
    features.update(temporal)
    
    # Session features
    session = extract_session_features(timestamps)
    features.update(session)
    
    return features
