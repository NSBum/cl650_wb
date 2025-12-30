"""
Weight and balance calculations for Challenger 650 aircraft.
Computes Operating Empty Weight (OEW) and related parameters.

Copyright (c) 2025 Alan Duncan
Licensed under MIT License with Non-Commercial Use Restriction.
See LICENSE file for details.
"""

# Fixed aircraft parameters (from planning/oew.md)
TEW_WEIGHT = 25480.0  # lbs
TEW_XARM = 524.9  # inches

OUTFITTING_WEIGHT = 3550.0  # lbs
OUTFITTING_XARM = 430.0  # inches

UNUSABLE_FUEL_WEIGHT = 128.0  # lbs
UNUSABLE_FUEL_XARM = 536.6  # inches

OIL_WEIGHT = 47.0  # lbs
OIL_XARM = 673.7  # inches

OTHER_OPERATING_ITEMS_WEIGHT = 650.0  # lbs
OTHER_OPERATING_ITEMS_XARM = 450.0  # inches

# Fixed station positions (Xarm)
FLIGHT_CREW_XARM = 255.0  # inches
CREW_BAGGAGE_XARM = 290.0  # inches
PASSENGER_XARM = 450.0  # inches
BAGGAGE_XARM = 605.0  # inches

# Standard passenger weights
ADULT_WEIGHT = 190.0  # lbs
CHILD_WEIGHT = 87.0  # lbs

# Fuel tank stations (Xarm)
MAIN_FUEL_XARM = 506.1  # inches (combined R/L main tanks)
AUX_FUEL_XARM = 450.6  # inches
TAIL_FUEL_XARM = 771.7  # inches

# %MAC calculation constants
MAC_LEADING_EDGE_IMPERIAL = 488.025  # inches
MAC_LENGTH_IMPERIAL = 92.64  # inches
MAC_LEADING_EDGE_METRIC = 12.40  # meters
MAC_LENGTH_METRIC = 2.35  # meters

# Configuration: Include outfitting, oil, and unusable fuel in OEW calculation
# Set to False to exclude these components (for now)
INCLUDE_OUTFITTING_OIL_UNUSABLE_FUEL = False


def calculate_oew(pilot_weight_lbs=0.0, copilot_weight_lbs=0.0, 
                  pilot_baggage_lbs=0.0, copilot_baggage_lbs=0.0):
    """
    Calculate Operating Empty Weight (OEW) and center of gravity.
    
    OEW = TEW + Flight Crew + Crew Baggage + Other Operating Items
    (Outfitting, Oil, and Unusable Fuel are excluded when INCLUDE_OUTFITTING_OIL_UNUSABLE_FUEL = False)
    
    Parameters:
    -----------
    pilot_weight_lbs : float
        Pilot weight in pounds. Default is 0.0.
    copilot_weight_lbs : float
        Copilot weight in pounds. Default is 0.0.
    pilot_baggage_lbs : float
        Pilot baggage weight in pounds. Default is 0.0.
    copilot_baggage_lbs : float
        Copilot baggage weight in pounds. Default is 0.0.
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'oew': Operating Empty Weight in pounds
        - 'total_moment': Total moment in pound-inches
        - 'cg_xarm': Center of gravity Xarm in inches
        - 'components': Dictionary with individual component weights and moments
    """
    # Calculate flight crew total weight
    flight_crew_weight = pilot_weight_lbs + copilot_weight_lbs
    
    # Calculate crew baggage total weight
    crew_baggage_weight = pilot_baggage_lbs + copilot_baggage_lbs
    
    # Calculate moments for each component
    tew_moment = TEW_WEIGHT * TEW_XARM
    flight_crew_moment = flight_crew_weight * FLIGHT_CREW_XARM
    crew_baggage_moment = crew_baggage_weight * CREW_BAGGAGE_XARM
    other_operating_items_moment = OTHER_OPERATING_ITEMS_WEIGHT * OTHER_OPERATING_ITEMS_XARM
    
    # Initialize totals
    total_weight = TEW_WEIGHT + flight_crew_weight + crew_baggage_weight + OTHER_OPERATING_ITEMS_WEIGHT
    total_moment = tew_moment + flight_crew_moment + crew_baggage_moment + other_operating_items_moment
    
    # Conditionally include outfitting, oil, and unusable fuel
    if INCLUDE_OUTFITTING_OIL_UNUSABLE_FUEL:
        outfitting_moment = OUTFITTING_WEIGHT * OUTFITTING_XARM
        unusable_fuel_moment = UNUSABLE_FUEL_WEIGHT * UNUSABLE_FUEL_XARM
        oil_moment = OIL_WEIGHT * OIL_XARM
        
        total_weight += OUTFITTING_WEIGHT + UNUSABLE_FUEL_WEIGHT + OIL_WEIGHT
        total_moment += outfitting_moment + unusable_fuel_moment + oil_moment
    else:
        # Set to zero when excluded
        outfitting_moment = 0.0
        unusable_fuel_moment = 0.0
        oil_moment = 0.0
    
    # Calculate center of gravity (CG) Xarm
    cg_xarm = total_moment / total_weight if total_weight > 0 else 0.0
    
    # Build components dictionary for detailed breakdown
    components = {
        'tew': {
            'weight': TEW_WEIGHT,
            'xarm': TEW_XARM,
            'moment': tew_moment
        },
        'flight_crew': {
            'weight': flight_crew_weight,
            'xarm': FLIGHT_CREW_XARM,
            'moment': flight_crew_moment
        },
        'crew_baggage': {
            'weight': crew_baggage_weight,
            'xarm': CREW_BAGGAGE_XARM,
            'moment': crew_baggage_moment
        },
        'other_operating_items': {
            'weight': OTHER_OPERATING_ITEMS_WEIGHT,
            'xarm': OTHER_OPERATING_ITEMS_XARM,
            'moment': other_operating_items_moment
        }
    }
    
    # Conditionally add outfitting, oil, and unusable fuel to components
    if INCLUDE_OUTFITTING_OIL_UNUSABLE_FUEL:
        components['outfitting'] = {
            'weight': OUTFITTING_WEIGHT,
            'xarm': OUTFITTING_XARM,
            'moment': outfitting_moment
        }
        components['unusable_fuel'] = {
            'weight': UNUSABLE_FUEL_WEIGHT,
            'xarm': UNUSABLE_FUEL_XARM,
            'moment': unusable_fuel_moment
        }
        components['oil'] = {
            'weight': OIL_WEIGHT,
            'xarm': OIL_XARM,
            'moment': oil_moment
        }
    
    return {
        'oew': total_weight,
        'total_moment': total_moment,
        'cg_xarm': cg_xarm,
        'components': components
    }


def get_standard_oew():
    """
    Get the standard OEW with default crew weights (170 lbs each, no baggage).
    
    Returns:
    --------
    dict
        Same format as calculate_oew() with standard crew weights
    """
    return calculate_oew(
        pilot_weight_lbs=170.0,
        copilot_weight_lbs=170.0,
        pilot_baggage_lbs=0.0,
        copilot_baggage_lbs=0.0
    )


def calculate_zfw(oew_result, num_adults=0, num_children=0, baggage_weight_lbs=0.0, 
                  total_passenger_weight_lbs=None):
    """
    Calculate Zero Fuel Weight (ZFW) from OEW plus passengers and baggage.
    
    ZFW = OEW + Passengers (adults + children) + Baggage
    
    Parameters:
    -----------
    oew_result : dict
        Result dictionary from calculate_oew() containing 'oew', 'total_moment', 'cg_xarm', and 'components'
    num_adults : int
        Number of adult passengers. Default is 0. Ignored if total_passenger_weight_lbs is provided.
    num_children : int
        Number of child passengers. Default is 0. Ignored if total_passenger_weight_lbs is provided.
    baggage_weight_lbs : float
        Baggage weight in pounds. Default is 0.0.
    total_passenger_weight_lbs : float, optional
        Total passenger weight in pounds. If provided, overrides num_adults and num_children calculation.
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'zfw': Zero Fuel Weight in pounds
        - 'total_moment': Total moment in pound-inches
        - 'cg_xarm': Center of gravity Xarm in inches
        - 'oew': OEW value (from input)
        - 'components': Dictionary with individual component weights and moments
    """
    # Get OEW values
    oew_weight = oew_result['oew']
    oew_moment = oew_result['total_moment']
    
    # Calculate passenger weights
    if total_passenger_weight_lbs is not None:
        # Use provided total passenger weight
        total_passenger_weight = total_passenger_weight_lbs
        adult_total_weight = 0.0
        child_total_weight = 0.0
        num_adults = 0
        num_children = 0
    else:
        # Calculate from number of adults and children
        adult_total_weight = num_adults * ADULT_WEIGHT
        child_total_weight = num_children * CHILD_WEIGHT
        total_passenger_weight = adult_total_weight + child_total_weight
    
    # Calculate moments
    if total_passenger_weight_lbs is not None:
        # Use total passenger weight for moment calculation
        passenger_moment = total_passenger_weight * PASSENGER_XARM
        adult_moment = 0.0
        child_moment = 0.0
    else:
        # Calculate moments separately for adults and children
        adult_moment = adult_total_weight * PASSENGER_XARM
        child_moment = child_total_weight * PASSENGER_XARM
        passenger_moment = adult_moment + child_moment
    
    baggage_moment = baggage_weight_lbs * BAGGAGE_XARM
    
    # Calculate total weight (ZFW)
    zfw_weight = oew_weight + total_passenger_weight + baggage_weight_lbs
    
    # Calculate total moment
    total_moment = oew_moment + passenger_moment + baggage_moment
    
    # Calculate center of gravity (CG) Xarm
    cg_xarm = total_moment / zfw_weight if zfw_weight > 0 else 0.0
    
    # Build components dictionary
    components = {
        'oew': {
            'weight': oew_weight,
            'xarm': oew_result['cg_xarm'],
            'moment': oew_moment
        },
        'adults': {
            'weight': adult_total_weight,
            'xarm': PASSENGER_XARM,
            'moment': adult_moment if total_passenger_weight_lbs is None else 0.0,
            'count': num_adults
        },
        'children': {
            'weight': child_total_weight,
            'xarm': PASSENGER_XARM,
            'moment': child_moment if total_passenger_weight_lbs is None else 0.0,
            'count': num_children
        },
        'passengers': {
            'weight': total_passenger_weight,
            'xarm': PASSENGER_XARM,
            'moment': passenger_moment
        },
        'baggage': {
            'weight': baggage_weight_lbs,
            'xarm': BAGGAGE_XARM,
            'moment': baggage_moment
        }
    }
    
    return {
        'zfw': zfw_weight,
        'total_moment': total_moment,
        'cg_xarm': cg_xarm,
        'oew': oew_weight,
        'components': components
    }


def calculate_tow(zfw_result, main_fuel_lbs=0.0, aux_fuel_lbs=0.0, tail_fuel_lbs=0.0):
    """
    Calculate Takeoff Weight (TOW) from ZFW plus fuel.
    
    TOW = ZFW + Main Fuel + Aux Fuel + Tail Fuel
    
    Parameters:
    -----------
    zfw_result : dict
        Result dictionary from calculate_zfw() containing 'zfw', 'total_moment', 'cg_xarm', and 'components'
    main_fuel_lbs : float
        Total main tank fuel weight (R/L combined) in pounds. Default is 0.0.
    aux_fuel_lbs : float
        Auxiliary tank fuel weight in pounds. Default is 0.0.
    tail_fuel_lbs : float
        Tail tank fuel weight in pounds. Default is 0.0.
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'tow': Takeoff Weight in pounds
        - 'total_moment': Total moment in pound-inches
        - 'cg_xarm': Center of gravity Xarm in inches
        - 'zfw': ZFW value (from input)
        - 'components': Dictionary with individual component weights and moments
    """
    # Get ZFW values
    zfw_weight = zfw_result['zfw']
    zfw_moment = zfw_result['total_moment']
    
    # Calculate fuel moments
    main_fuel_moment = main_fuel_lbs * MAIN_FUEL_XARM
    aux_fuel_moment = aux_fuel_lbs * AUX_FUEL_XARM
    tail_fuel_moment = tail_fuel_lbs * TAIL_FUEL_XARM
    
    # Calculate total weight (TOW)
    tow_weight = zfw_weight + main_fuel_lbs + aux_fuel_lbs + tail_fuel_lbs
    
    # Calculate total moment
    total_moment = zfw_moment + main_fuel_moment + aux_fuel_moment + tail_fuel_moment
    
    # Calculate center of gravity (CG) Xarm
    cg_xarm = total_moment / tow_weight if tow_weight > 0 else 0.0
    
    # Build components dictionary
    components = {
        'zfw': {
            'weight': zfw_weight,
            'xarm': zfw_result['cg_xarm'],
            'moment': zfw_moment
        },
        'main_fuel': {
            'weight': main_fuel_lbs,
            'xarm': MAIN_FUEL_XARM,
            'moment': main_fuel_moment
        },
        'aux_fuel': {
            'weight': aux_fuel_lbs,
            'xarm': AUX_FUEL_XARM,
            'moment': aux_fuel_moment
        },
        'tail_fuel': {
            'weight': tail_fuel_lbs,
            'xarm': TAIL_FUEL_XARM,
            'moment': tail_fuel_moment
        }
    }
    
    return {
        'tow': tow_weight,
        'total_moment': total_moment,
        'cg_xarm': cg_xarm,
        'zfw': zfw_weight,
        'components': components
    }


def calculate_percent_mac(cg_xarm, unit_system='imperial'):
    """
    Calculate %MAC (Mean Aerodynamic Chord percentage) from CG Xarm.
    
    For imperial: %MAC = [(XarmCG - 488.025) / 92.64] × 100
    For metric: %MAC = [(XarmCG - 12.40) / 2.35] × 100
    
    Parameters:
    -----------
    cg_xarm : float
        Center of gravity Xarm position
    unit_system : str
        'imperial' (inches) or 'metric' (meters). Default is 'imperial'.
    
    Returns:
    --------
    float
        %MAC value (percentage)
    """
    if unit_system == 'metric':
        percent_mac = ((cg_xarm - MAC_LEADING_EDGE_METRIC) / MAC_LENGTH_METRIC) * 100
    else:  # imperial
        percent_mac = ((cg_xarm - MAC_LEADING_EDGE_IMPERIAL) / MAC_LENGTH_IMPERIAL) * 100
    
    return percent_mac

