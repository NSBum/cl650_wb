"""
Unit conversion utilities for weight and balance calculations.
All internal calculations are done in pounds (lbs) and gallons (gal).

Copyright (c) 2025 Alan Duncan
Licensed under MIT License with Non-Commercial Use Restriction.
See LICENSE file for details.
"""

# Conversion constants
LBS_TO_KG = 0.453592
KG_TO_LBS = 1 / LBS_TO_KG
GAL_TO_L = 3.78541
L_TO_GAL = 1 / GAL_TO_L


def lbs_to_kg(lbs):
    """Convert pounds to kilograms."""
    return lbs * LBS_TO_KG


def kg_to_lbs(kg):
    """Convert kilograms to pounds."""
    return kg * KG_TO_LBS


def gal_to_l(gallons):
    """Convert gallons to liters."""
    return gallons * GAL_TO_L


def l_to_gal(liters):
    """Convert liters to gallons."""
    return liters * L_TO_GAL


def normalize_weight_to_lbs(value, unit):
    """
    Normalize a weight value to pounds.
    
    Parameters:
    -----------
    value : float
        The weight value
    unit : str
        'lbs' or 'kg'
    
    Returns:
    --------
    float
        Weight in pounds
    """
    if unit == 'kg':
        return kg_to_lbs(value)
    return value  # Already in lbs


def normalize_fuel_to_gallons(value, unit):
    """
    Normalize a fuel volume to gallons.
    
    Parameters:
    -----------
    value : float
        The fuel volume value
    unit : str
        'gal' or 'l'
    
    Returns:
    --------
    float
        Fuel volume in gallons
    """
    if unit == 'l':
        return l_to_gal(value)
    return value  # Already in gallons


def format_weight(value_lbs, unit, decimals=1):
    """
    Format a weight value for display in the specified unit.
    
    Parameters:
    -----------
    value_lbs : float
        Weight in pounds
    unit : str
        'lbs' or 'kg'
    decimals : int
        Number of decimal places
    
    Returns:
    --------
    str
        Formatted weight string
    """
    if unit == 'kg':
        return f"{lbs_to_kg(value_lbs):.{decimals}f} kg"
    return f"{value_lbs:.{decimals}f} lbs"


def format_fuel(value_gal, unit, decimals=1):
    """
    Format a fuel volume for display in the specified unit.
    
    Parameters:
    -----------
    value_gal : float
        Fuel volume in gallons
    unit : str
        'gal' or 'l'
    decimals : int
        Number of decimal places
    
    Returns:
    --------
    str
        Formatted fuel volume string
    """
    if unit == 'l':
        return f"{gal_to_l(value_gal):.{decimals}f} L"
    return f"{value_gal:.{decimals}f} gal"

