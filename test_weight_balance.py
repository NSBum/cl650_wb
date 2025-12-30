"""
Unit tests for weight and balance calculations.
"""
import unittest
from weight_balance import (
    calculate_oew,
    get_standard_oew,
    calculate_zfw,
    calculate_tow,
    calculate_percent_mac,
    TEW_WEIGHT,
    OUTFITTING_WEIGHT,
    UNUSABLE_FUEL_WEIGHT,
    OIL_WEIGHT,
    OTHER_OPERATING_ITEMS_WEIGHT,
    FLIGHT_CREW_XARM,
    CREW_BAGGAGE_XARM,
    PASSENGER_XARM,
    BAGGAGE_XARM,
    ADULT_WEIGHT,
    CHILD_WEIGHT,
    MAIN_FUEL_XARM,
    AUX_FUEL_XARM,
    TAIL_FUEL_XARM
)


class TestWeightBalance(unittest.TestCase):
    """Test cases for weight and balance calculations."""
    
    def test_zero_crew_oew(self):
        """Test OEW calculation with zero crew weights."""
        result = calculate_oew(
            pilot_weight_lbs=0.0,
            copilot_weight_lbs=0.0,
            pilot_baggage_lbs=0.0,
            copilot_baggage_lbs=0.0
        )
        
        # OEW should be sum of fixed components (excluding outfitting, oil, unusable fuel)
        expected_oew = (TEW_WEIGHT + OTHER_OPERATING_ITEMS_WEIGHT)
        
        self.assertAlmostEqual(result['oew'], expected_oew, places=1)
        self.assertGreater(result['total_moment'], 0)
        self.assertGreater(result['cg_xarm'], 0)
    
    def test_standard_crew_oew(self):
        """Test OEW calculation with standard crew weights (170 lbs each)."""
        result = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=0.0,
            copilot_baggage_lbs=0.0
        )
        
        # OEW should include 2 * 170 lbs for crew (excluding outfitting, oil, unusable fuel)
        expected_oew = (TEW_WEIGHT + 340.0 + OTHER_OPERATING_ITEMS_WEIGHT)
        
        self.assertAlmostEqual(result['oew'], expected_oew, places=1)
        self.assertGreater(result['total_moment'], 0)
        self.assertGreater(result['cg_xarm'], 0)
    
    def test_crew_with_baggage(self):
        """Test OEW calculation with crew and baggage."""
        result = calculate_oew(
            pilot_weight_lbs=180.0,
            copilot_weight_lbs=175.0,
            pilot_baggage_lbs=20.0,
            copilot_baggage_lbs=15.0
        )
        
        # Verify crew weight is included
        crew_weight = 180.0 + 175.0
        baggage_weight = 20.0 + 15.0
        
        expected_oew = (TEW_WEIGHT + crew_weight + baggage_weight + 
                       OTHER_OPERATING_ITEMS_WEIGHT)
        
        self.assertAlmostEqual(result['oew'], expected_oew, places=1)
        self.assertEqual(result['components']['flight_crew']['weight'], crew_weight)
        self.assertEqual(result['components']['crew_baggage']['weight'], baggage_weight)
    
    def test_cg_calculation(self):
        """Test that CG is calculated correctly (moment / weight)."""
        result = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=10.0,
            copilot_baggage_lbs=10.0
        )
        
        # CG should equal total moment divided by total weight
        calculated_cg = result['total_moment'] / result['oew']
        self.assertAlmostEqual(result['cg_xarm'], calculated_cg, places=2)
    
    def test_components_structure(self):
        """Test that components dictionary has correct structure."""
        result = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=0.0,
            copilot_baggage_lbs=0.0
        )
        
        # Check that all expected components are present
        # Note: outfitting, unusable_fuel, and oil are excluded when INCLUDE_OUTFITTING_OIL_UNUSABLE_FUEL = False
        expected_components = [
            'tew', 'flight_crew', 'crew_baggage', 'other_operating_items'
        ]
        
        for component in expected_components:
            self.assertIn(component, result['components'])
            self.assertIn('weight', result['components'][component])
            self.assertIn('xarm', result['components'][component])
            self.assertIn('moment', result['components'][component])
    
    def test_get_standard_oew(self):
        """Test the get_standard_oew convenience function."""
        standard = get_standard_oew()
        manual = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=0.0,
            copilot_baggage_lbs=0.0
        )
        
        self.assertAlmostEqual(standard['oew'], manual['oew'], places=1)
        self.assertAlmostEqual(standard['cg_xarm'], manual['cg_xarm'], places=2)
    
    def test_moment_calculations(self):
        """Test that moments are calculated correctly (weight * xarm)."""
        result = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=20.0,
            copilot_baggage_lbs=20.0
        )
        
        # Verify flight crew moment
        expected_crew_moment = 340.0 * FLIGHT_CREW_XARM
        self.assertAlmostEqual(
            result['components']['flight_crew']['moment'], 
            expected_crew_moment, 
            places=1
        )
        
        # Verify crew baggage moment
        expected_baggage_moment = 40.0 * CREW_BAGGAGE_XARM
        self.assertAlmostEqual(
            result['components']['crew_baggage']['moment'], 
            expected_baggage_moment, 
            places=1
        )
    
    def test_specific_scenario_two_pilots_with_baggage(self):
        """
        Test specific scenario: Two pilots at 170 lbs each, each with 15 lbs baggage.
        Expected: OEW = 26500 lbs, Xarm = 519.3 inches, Moment = 13762.5 lb-inches
        
        NOTE: This test currently shows a discrepancy. Calculated values differ from expected.
        Verify which values are correct - either the constants need adjustment or the expected values.
        """
        result = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        # Expected values from user specification
        expected_oew = 26500.0  # lbs
        expected_xarm = 519.3  # inches
        expected_moment = 13762.5  # lb-inches
        
        # Calculated values
        calculated_oew = result['oew']
        calculated_xarm = result['cg_xarm']
        calculated_moment = result['total_moment']
        
        # Print comparison for debugging
        print(f"\n=== Scenario: Two pilots (170 lbs each) with baggage (15 lbs each) ===")
        print(f"Expected OEW: {expected_oew} lbs | Calculated: {calculated_oew} lbs | Difference: {calculated_oew - expected_oew} lbs")
        print(f"Expected Xarm: {expected_xarm} inches | Calculated: {calculated_xarm:.2f} inches | Difference: {calculated_xarm - expected_xarm:.2f} inches")
        print(f"Expected Moment: {expected_moment} lb-inches | Calculated: {calculated_moment:.2f} lb-inches")
        print(f"Note: Expected moment seems low. OEW * Xarm = {expected_oew * expected_xarm:.2f} lb-inches")
        print(f"Component breakdown:")
        for name, comp in result['components'].items():
            print(f"  {name}: {comp['weight']} lbs @ {comp['xarm']} in = {comp['moment']:.2f} lb-in")
        
        # Test with calculated values to verify the calculation logic is correct
        # The test will pass if the calculation matches expected, or fail with detailed info
        self.assertAlmostEqual(result['oew'], expected_oew, places=1, 
                              msg=f"OEW mismatch: expected {expected_oew} lbs, calculated {calculated_oew} lbs. "
                                  f"Check if constants need adjustment or if OEW definition differs.")
        self.assertAlmostEqual(result['cg_xarm'], expected_xarm, places=1,
                              msg=f"Xarm mismatch: expected {expected_xarm} inches, calculated {calculated_xarm:.2f} inches")
        
        # Moment check - expected_moment is in thousands (13,762.5 = 13,762,500 lb-inches)
        # Allow for small rounding differences (within 200 lb-inches tolerance)
        expected_moment_full = expected_moment * 1000
        moment_diff = abs(calculated_moment - expected_moment_full)
        self.assertLess(moment_diff, 200.0,
                       msg=f"Moment: expected {expected_moment_full:.0f} (or {expected_moment} in thousands), got {calculated_moment:.2f}. "
                           f"Difference: {moment_diff:.2f} lb-inches (tolerance: 200 lb-inches)")


class TestZeroFuelWeight(unittest.TestCase):
    """Test cases for Zero Fuel Weight (ZFW) calculations."""
    
    def test_zfw_with_no_passengers_no_baggage(self):
        """Test ZFW calculation with no passengers or baggage (should equal OEW)."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        zfw = calculate_zfw(oew, num_adults=0, num_children=0, baggage_weight_lbs=0.0)
        
        self.assertAlmostEqual(zfw['zfw'], oew['oew'], places=1)
        self.assertAlmostEqual(zfw['cg_xarm'], oew['cg_xarm'], places=2)
        self.assertAlmostEqual(zfw['total_moment'], oew['total_moment'], places=1)
    
    def test_zfw_with_passengers(self):
        """Test ZFW calculation with passengers."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        zfw = calculate_zfw(oew, num_adults=2, num_children=1, baggage_weight_lbs=0.0)
        
        # Expected passenger weight: 2 * 190 + 1 * 87 = 467 lbs
        from weight_balance import ADULT_WEIGHT, CHILD_WEIGHT
        expected_passenger_weight = 2 * ADULT_WEIGHT + 1 * CHILD_WEIGHT
        expected_zfw = oew['oew'] + expected_passenger_weight
        
        self.assertAlmostEqual(zfw['zfw'], expected_zfw, places=1)
        self.assertEqual(zfw['components']['adults']['weight'], 2 * ADULT_WEIGHT)
        self.assertEqual(zfw['components']['children']['weight'], 1 * CHILD_WEIGHT)
        self.assertEqual(zfw['components']['adults']['count'], 2)
        self.assertEqual(zfw['components']['children']['count'], 1)
    
    def test_zfw_with_baggage(self):
        """Test ZFW calculation with baggage."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        baggage_weight = 200.0
        zfw = calculate_zfw(oew, num_adults=0, num_children=0, baggage_weight_lbs=baggage_weight)
        
        expected_zfw = oew['oew'] + baggage_weight
        self.assertAlmostEqual(zfw['zfw'], expected_zfw, places=1)
        self.assertEqual(zfw['components']['baggage']['weight'], baggage_weight)
        from weight_balance import BAGGAGE_XARM
        self.assertEqual(zfw['components']['baggage']['xarm'], BAGGAGE_XARM)
    
    def test_zfw_moment_calculations(self):
        """Test that ZFW moments are calculated correctly."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        from weight_balance import ADULT_WEIGHT, CHILD_WEIGHT, PASSENGER_XARM, BAGGAGE_XARM
        num_adults = 2
        num_children = 1
        baggage_weight = 200.0
        
        zfw = calculate_zfw(oew, num_adults=num_adults, num_children=num_children, 
                           baggage_weight_lbs=baggage_weight)
        
        # Verify passenger moments
        expected_adult_moment = num_adults * ADULT_WEIGHT * PASSENGER_XARM
        expected_child_moment = num_children * CHILD_WEIGHT * PASSENGER_XARM
        expected_baggage_moment = baggage_weight * BAGGAGE_XARM
        
        self.assertAlmostEqual(zfw['components']['adults']['moment'], expected_adult_moment, places=1)
        self.assertAlmostEqual(zfw['components']['children']['moment'], expected_child_moment, places=1)
        self.assertAlmostEqual(zfw['components']['baggage']['moment'], expected_baggage_moment, places=1)
        
        # Verify total moment
        expected_total_moment = (oew['total_moment'] + expected_adult_moment + 
                                expected_child_moment + expected_baggage_moment)
        self.assertAlmostEqual(zfw['total_moment'], expected_total_moment, places=1)
    
    def test_zfw_cg_calculation(self):
        """Test that ZFW CG is calculated correctly (moment / weight)."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        zfw = calculate_zfw(oew, num_adults=2, num_children=1, baggage_weight_lbs=200.0)
        
        # CG should equal total moment divided by total weight
        calculated_cg = zfw['total_moment'] / zfw['zfw']
        self.assertAlmostEqual(zfw['cg_xarm'], calculated_cg, places=2)
    
    def test_zfw_components_structure(self):
        """Test that ZFW components dictionary has correct structure."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        zfw = calculate_zfw(oew, num_adults=2, num_children=1, baggage_weight_lbs=200.0)
        
        # Check that all expected components are present
        expected_components = ['oew', 'adults', 'children', 'baggage']
        
        for component in expected_components:
            self.assertIn(component, zfw['components'])
            self.assertIn('weight', zfw['components'][component])
            self.assertIn('xarm', zfw['components'][component])
            self.assertIn('moment', zfw['components'][component])
        
        # Check that passenger components have count
        self.assertIn('count', zfw['components']['adults'])
        self.assertIn('count', zfw['components']['children'])
    
    def test_specific_scenario_zfw_with_total_passenger_weight(self):
        """
        Test specific scenario: OEW with crew (170 lbs each, 15 lbs baggage each),
        passengers 850 lbs total, baggage 150 lbs.
        Expected: ZFW = 27500 lbs, Xarm = 517.7 inches, Moment = 14235.9 thousands
        """
        # Calculate OEW with crew: 2 pilots at 170 lbs each, 15 lbs baggage each
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        # Calculate ZFW with 850 lbs passengers and 150 lbs baggage
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        # Expected values
        expected_zfw = 27500.0  # lbs
        expected_xarm = 517.7  # inches
        expected_moment_thousands = 14235.9  # in thousands
        
        print(f"\n=== ZFW Scenario: 850 lbs passengers + 150 lbs baggage ===")
        print(f"Expected ZFW: {expected_zfw} lbs | Calculated: {zfw['zfw']} lbs")
        print(f"Expected Xarm: {expected_xarm} inches | Calculated: {zfw['cg_xarm']:.2f} inches")
        print(f"Expected Moment: {expected_moment_thousands} thousands | Calculated: {zfw['total_moment']/1000:.1f} thousands")
        
        self.assertAlmostEqual(zfw['zfw'], expected_zfw, places=1,
                              msg=f"ZFW: expected {expected_zfw} lbs, got {zfw['zfw']} lbs")
        self.assertAlmostEqual(zfw['cg_xarm'], expected_xarm, places=1,
                              msg=f"Xarm: expected {expected_xarm} inches, got {zfw['cg_xarm']:.2f} inches")
        
        # Moment check - allow for small rounding differences (within 1 thousand)
        expected_moment_full = expected_moment_thousands * 1000
        moment_diff = abs(zfw['total_moment'] - expected_moment_full)
        self.assertLess(moment_diff, 1000.0,
                       msg=f"Moment: expected {expected_moment_full:.0f} (or {expected_moment_thousands} thousands), "
                           f"got {zfw['total_moment']:.2f}. Difference: {moment_diff:.2f} lb-inches")


class TestTakeoffWeight(unittest.TestCase):
    """Test cases for Takeoff Weight (TOW) calculations."""
    
    def test_tow_with_no_fuel(self):
        """Test TOW calculation with no fuel (should equal ZFW)."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        tow = calculate_tow(zfw, main_fuel_lbs=0.0, aux_fuel_lbs=0.0, tail_fuel_lbs=0.0)
        
        self.assertAlmostEqual(tow['tow'], zfw['zfw'], places=1)
        self.assertAlmostEqual(tow['cg_xarm'], zfw['cg_xarm'], places=2)
        self.assertAlmostEqual(tow['total_moment'], zfw['total_moment'], places=1)
    
    def test_tow_with_fuel(self):
        """Test TOW calculation with fuel."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        main_fuel = 9620.0
        aux_fuel = 7168.0
        tail_fuel = 3112.0
        
        tow = calculate_tow(zfw, main_fuel_lbs=main_fuel, aux_fuel_lbs=aux_fuel, tail_fuel_lbs=tail_fuel)
        
        expected_tow = zfw['zfw'] + main_fuel + aux_fuel + tail_fuel
        self.assertAlmostEqual(tow['tow'], expected_tow, places=1)
        self.assertEqual(tow['components']['main_fuel']['weight'], main_fuel)
        self.assertEqual(tow['components']['aux_fuel']['weight'], aux_fuel)
        self.assertEqual(tow['components']['tail_fuel']['weight'], tail_fuel)
    
    def test_tow_moment_calculations(self):
        """Test that TOW moments are calculated correctly."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        from weight_balance import MAIN_FUEL_XARM, AUX_FUEL_XARM, TAIL_FUEL_XARM
        main_fuel = 9620.0
        aux_fuel = 7168.0
        tail_fuel = 3112.0
        
        tow = calculate_tow(zfw, main_fuel_lbs=main_fuel, aux_fuel_lbs=aux_fuel, tail_fuel_lbs=tail_fuel)
        
        # Verify fuel moments
        expected_main_moment = main_fuel * MAIN_FUEL_XARM
        expected_aux_moment = aux_fuel * AUX_FUEL_XARM
        expected_tail_moment = tail_fuel * TAIL_FUEL_XARM
        
        self.assertAlmostEqual(tow['components']['main_fuel']['moment'], expected_main_moment, places=1)
        self.assertAlmostEqual(tow['components']['aux_fuel']['moment'], expected_aux_moment, places=1)
        self.assertAlmostEqual(tow['components']['tail_fuel']['moment'], expected_tail_moment, places=1)
        
        # Verify total moment
        expected_total_moment = (zfw['total_moment'] + expected_main_moment + 
                                expected_aux_moment + expected_tail_moment)
        self.assertAlmostEqual(tow['total_moment'], expected_total_moment, places=1)
    
    def test_tow_cg_calculation(self):
        """Test that TOW CG is calculated correctly (moment / weight)."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        tow = calculate_tow(zfw, main_fuel_lbs=9620.0, aux_fuel_lbs=7168.0, tail_fuel_lbs=3112.0)
        
        # CG should equal total moment divided by total weight
        calculated_cg = tow['total_moment'] / tow['tow']
        self.assertAlmostEqual(tow['cg_xarm'], calculated_cg, places=2)
    
    def test_tow_components_structure(self):
        """Test that TOW components dictionary has correct structure."""
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        tow = calculate_tow(zfw, main_fuel_lbs=9620.0, aux_fuel_lbs=7168.0, tail_fuel_lbs=3112.0)
        
        # Check that all expected components are present
        expected_components = ['zfw', 'main_fuel', 'aux_fuel', 'tail_fuel']
        
        for component in expected_components:
            self.assertIn(component, tow['components'])
            self.assertIn('weight', tow['components'][component])
            self.assertIn('xarm', tow['components'][component])
            self.assertIn('moment', tow['components'][component])
    
    def test_specific_scenario_tow(self):
        """
        Test specific scenario: ZFW (27500 lbs @ 517.7 in) + fuel
        (main: 9620 lbs, aux: 7168 lbs, tail: 3112 lbs).
        Expected: TOW = 47400 lbs, Xarm = 521.8 inches, Moment = 24736.5 thousands
        """
        # Calculate OEW with crew: 2 pilots at 170 lbs each, 15 lbs baggage each
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        
        # Calculate ZFW with 850 lbs passengers and 150 lbs baggage
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        
        # Calculate TOW with fuel
        main_fuel = 9620.0
        aux_fuel = 7168.0
        tail_fuel = 3112.0
        
        tow = calculate_tow(zfw, main_fuel_lbs=main_fuel, aux_fuel_lbs=aux_fuel, tail_fuel_lbs=tail_fuel)
        
        # Expected values
        expected_tow = 47400.0  # lbs
        expected_xarm = 521.8  # inches
        expected_moment_thousands = 24736.5  # in thousands
        
        print(f"\n=== TOW Scenario: Main {main_fuel} lbs, Aux {aux_fuel} lbs, Tail {tail_fuel} lbs ===")
        print(f"Expected TOW: {expected_tow} lbs | Calculated: {tow['tow']} lbs")
        print(f"Expected Xarm: {expected_xarm} inches | Calculated: {tow['cg_xarm']:.2f} inches")
        print(f"Expected Moment: {expected_moment_thousands} thousands | Calculated: {tow['total_moment']/1000:.1f} thousands")
        
        self.assertAlmostEqual(tow['tow'], expected_tow, places=1,
                              msg=f"TOW: expected {expected_tow} lbs, got {tow['tow']} lbs")
        # Allow small rounding difference (within 0.1 inches)
        xarm_diff = abs(tow['cg_xarm'] - expected_xarm)
        self.assertLess(xarm_diff, 0.1,
                       msg=f"Xarm: expected {expected_xarm} inches, got {tow['cg_xarm']:.2f} inches. "
                           f"Difference: {xarm_diff:.3f} inches")
        
        # Moment check - allow for small rounding differences (within 2 thousands)
        expected_moment_full = expected_moment_thousands * 1000
        moment_diff = abs(tow['total_moment'] - expected_moment_full)
        self.assertLess(moment_diff, 2000.0,
                       msg=f"Moment: expected {expected_moment_full:.0f} (or {expected_moment_thousands} thousands), "
                           f"got {tow['total_moment']:.2f}. Difference: {moment_diff:.2f} lb-inches")


class TestPercentMAC(unittest.TestCase):
    """Test cases for %MAC (Mean Aerodynamic Chord) calculations."""
    
    def test_percent_mac_imperial(self):
        """Test %MAC calculation in imperial units."""
        # Test with the known scenario: Xarm = 521.8 inches should give ~36.5%
        cg_xarm = 521.8
        percent_mac = calculate_percent_mac(cg_xarm, unit_system='imperial')
        
        expected_percent_mac = 36.5
        
        print(f"\n=== %MAC Calculation (Imperial) ===")
        print(f"CG Xarm: {cg_xarm} inches")
        print(f"Expected %MAC: {expected_percent_mac}% | Calculated: {percent_mac:.2f}%")
        
        self.assertAlmostEqual(percent_mac, expected_percent_mac, places=1,
                              msg=f"%MAC: expected {expected_percent_mac}%, got {percent_mac:.2f}%")
    
    def test_percent_mac_metric(self):
        """Test %MAC calculation in metric units."""
        # Convert 521.8 inches to meters: 521.8 / 39.3701 ≈ 13.2537 meters
        # Or use the metric formula directly
        cg_xarm_meters = 13.2537  # approximately 521.8 inches
        percent_mac = calculate_percent_mac(cg_xarm_meters, unit_system='metric')
        
        # Verify the calculation
        expected_percent_mac = ((cg_xarm_meters - 12.40) / 2.35) * 100
        
        self.assertAlmostEqual(percent_mac, expected_percent_mac, places=2)
    
    def test_percent_mac_at_leading_edge(self):
        """Test %MAC at MAC leading edge (should be 0%)."""
        from weight_balance import MAC_LEADING_EDGE_IMPERIAL
        percent_mac = calculate_percent_mac(MAC_LEADING_EDGE_IMPERIAL, unit_system='imperial')
        
        self.assertAlmostEqual(percent_mac, 0.0, places=2)
    
    def test_percent_mac_at_trailing_edge(self):
        """Test %MAC at MAC trailing edge (should be 100%)."""
        from weight_balance import MAC_LEADING_EDGE_IMPERIAL, MAC_LENGTH_IMPERIAL
        trailing_edge_xarm = MAC_LEADING_EDGE_IMPERIAL + MAC_LENGTH_IMPERIAL
        percent_mac = calculate_percent_mac(trailing_edge_xarm, unit_system='imperial')
        
        self.assertAlmostEqual(percent_mac, 100.0, places=2)
    
    def test_percent_mac_integration_with_tow(self):
        """Test %MAC calculation integrated with TOW calculation."""
        # Use the scenario from previous tests
        oew = calculate_oew(
            pilot_weight_lbs=170.0,
            copilot_weight_lbs=170.0,
            pilot_baggage_lbs=15.0,
            copilot_baggage_lbs=15.0
        )
        zfw = calculate_zfw(oew, total_passenger_weight_lbs=850.0, baggage_weight_lbs=150.0)
        tow = calculate_tow(zfw, main_fuel_lbs=9620.0, aux_fuel_lbs=7168.0, tail_fuel_lbs=3112.0)
        
        # Calculate %MAC from TOW CG
        percent_mac = calculate_percent_mac(tow['cg_xarm'], unit_system='imperial')
        
        expected_percent_mac = 36.5
        
        print(f"\n=== %MAC from TOW ===")
        print(f"TOW CG Xarm: {tow['cg_xarm']:.2f} inches")
        print(f"Expected %MAC: {expected_percent_mac}% | Calculated: {percent_mac:.2f}%")
        
        self.assertAlmostEqual(percent_mac, expected_percent_mac, places=1,
                              msg=f"%MAC: expected {expected_percent_mac}%, got {percent_mac:.2f}%")


if __name__ == '__main__':
    unittest.main()

