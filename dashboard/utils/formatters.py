#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - FORMATTERS 💎🌟⚡

Utilities for formatting numbers, dates, and other data
"""

from typing import Union, Optional
from datetime import datetime
import pandas as pd


def format_number(value: Union[float, int], decimals: int = 2) -> str:
    """
    Format number with specified decimals
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        if decimals == 0:
            return f"{int(value):,}"
        else:
            return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: Union[float, int], decimals: int = 2) -> str:
    """
    Format number as percentage
    
    Args:
        value: Number to format (0.15 -> 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        # If value is already in percentage form (> 1), don't multiply
        if abs(value) > 1:
            return f"{float(value):.{decimals}f}%"
        else:
            return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(value: Union[float, int], symbol: str = "$", decimals: int = 2) -> str:
    """
    Format number as currency
    
    Args:
        value: Number to format
        symbol: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        formatted = f"{float(value):,.{decimals}f}"
        if value < 0:
            return f"-{symbol}{formatted[1:]}"  # Remove negative sign and add symbol
        else:
            return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return "N/A"


def format_pips(value: Union[float, int], decimals: int = 1) -> str:
    """
    Format pips value
    
    Args:
        value: Pips value
        decimals: Number of decimal places
        
    Returns:
        Formatted pips string
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        return f"{float(value):.{decimals}f} pips"
    except (ValueError, TypeError):
        return "N/A"


def format_datetime(dt: Union[str, datetime, pd.Timestamp], 
                   format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object
    
    Args:
        dt: Datetime to format
        format_str: Output format string
        
    Returns:
        Formatted datetime string
    """
    if pd.isna(dt):
        return "N/A"
    
    try:
        if isinstance(dt, str):
            # Try to parse string to datetime
            dt = pd.to_datetime(dt)
        
        if isinstance(dt, (datetime, pd.Timestamp)):
            return dt.strftime(format_str)
        
        return str(dt)
    except (ValueError, TypeError):
        return "N/A"


def format_duration(minutes: Union[float, int]) -> str:
    """
    Format duration in minutes to human-readable form
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string
    """
    if pd.isna(minutes):
        return "N/A"
    
    try:
        minutes = int(minutes)
        
        if minutes < 60:
            return f"{minutes}m"
        elif minutes < 1440:  # Less than a day
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
        else:
            days = minutes // 1440
            remaining = minutes % 1440
            hours = remaining // 60
            return f"{days}d {hours}h"
    except (ValueError, TypeError):
        return "N/A"


def color_positive_negative(value: Union[float, int]) -> str:
    """
    Return color based on positive/negative value
    
    Args:
        value: Number to check
        
    Returns:
        Color string ('green', 'red', or 'gray')
    """
    if pd.isna(value):
        return 'gray'
    
    try:
        value = float(value)
        if value > 0:
            return 'green'
        elif value < 0:
            return 'red'
        else:
            return 'gray'
    except (ValueError, TypeError):
        return 'gray'


def format_metric_delta(value: Union[float, int], 
                       is_percentage: bool = False,
                       is_currency: bool = False) -> str:
    """
    Format metric delta with appropriate sign and formatting
    
    Args:
        value: Value to format
        is_percentage: Whether to format as percentage
        is_currency: Whether to format as currency
        
    Returns:
        Formatted string with sign
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        
        if is_percentage:
            return f"{sign}{value:.2f}%"
        elif is_currency:
            return f"{sign}${abs(value):,.2f}" if value >= 0 else f"-${abs(value):,.2f}"
        else:
            return f"{sign}{value:,.2f}"
    except (ValueError, TypeError):
        return "N/A"
