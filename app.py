"""
Flask application for Challenger 650 weight and balance calculations.

Copyright (c) 2025 Alan Duncan
Licensed under MIT License with Non-Commercial Use Restriction.
See LICENSE file for details.
"""
import os
import uuid
from flask import Flask, render_template, request, session, send_from_directory
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

from challenger650_wb import (
    draw_wb_grid,
    draw_no_takeoff_zone,
    draw_min_zone,
    draw_mfw_text,
    draw_mzfw_line,
    draw_mlw_line,
    draw_envelope,
    draw_point
)
from utils import (
    normalize_weight_to_lbs,
    format_weight,
    lbs_to_kg,
    kg_to_lbs
)
from weight_balance import (
    calculate_oew,
    calculate_zfw,
    calculate_tow,
    calculate_percent_mac,
    ADULT_WEIGHT,
    CHILD_WEIGHT
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure static/charts directory exists
os.makedirs('static/charts', exist_ok=True)


def generate_chart(percent_mac=None, tow_lbs=None, show_label=True):
    """
    Generate the weight and balance chart with calculated point.
    
    Parameters:
    -----------
    percent_mac : float, optional
        %MAC value to plot. If None, plots a test point.
    tow_lbs : float, optional
        Takeoff weight in pounds. If None, uses test value.
    show_label : bool, optional
        Whether to show TOW and %MAC labels at the point. Default is True.
    
    Returns:
    --------
    str
        Path to the saved chart image
    """
    # Generate unique filename
    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join('static', 'charts', filename)
    
    # Determine point coordinates first (needed for collision detection)
    if percent_mac is not None and tow_lbs is not None:
        # Use calculated values
        x_coord = percent_mac
        y_coord = tow_lbs / 1000.0  # Convert to thousands of pounds
    else:
        # Use test point
        x_coord = 25
        y_coord = 30
    
    # Create chart
    fig, ax, ax2 = draw_wb_grid()
    draw_no_takeoff_zone(ax)
    draw_min_zone(ax)
    draw_mfw_text(ax)
    # Pass point coordinates for collision detection
    draw_mzfw_line(ax, point_x=x_coord, point_y=y_coord)
    draw_mlw_line(ax, point_x=x_coord, point_y=y_coord)
    draw_envelope(ax)
    
    # Add point
    draw_point(ax, x_coord, y_coord)
    
    # Add label with TOW and %MAC if requested
    if show_label and percent_mac is not None and tow_lbs is not None:
        label_text = f'TOW: {tow_lbs:.0f} lbs\n%MAC: {percent_mac:.1f}%'
        # Position label to the right and above the point, but keep it within chart bounds
        label_x = min(x_coord + 1.5, 38)  # Don't go beyond x-axis limit
        label_y = min(y_coord + 0.8, 49)  # Don't go beyond y-axis limit
        ax.text(label_x, label_y, label_text,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#0885A0', linewidth=1.5),
                fontsize=9, fontweight='bold',
                verticalalignment='bottom',
                horizontalalignment='left',
                zorder=10)
    
    # Save chart
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return filename


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with form and chart display."""
    # Initialize session defaults
    if 'unit_preference' not in session:
        session['unit_preference'] = 'imperial'
    
    # Get form data if submitted
    form_data = {}
    chart_filename = None
    calculation_results = {}
    
    if request.method == 'POST':
        # Get previous unit preference to detect changes
        previous_unit = session.get('unit_preference', 'imperial')
        
        # Handle unit preference selection
        if 'unit_preference' in request.form:
            session['unit_preference'] = request.form['unit_preference']
        
        # Get current unit preference
        unit = session.get('unit_preference', 'imperial')
        unit_changed = (previous_unit != unit)
        
        # Collect form data (always, to preserve values)
        pilot_weight = float(request.form.get('pilot_weight', 0) or 0)
        copilot_weight = float(request.form.get('copilot_weight', 0) or 0)
        pilot_baggage = float(request.form.get('pilot_baggage', 0) or 0)
        copilot_baggage = float(request.form.get('copilot_baggage', 0) or 0)
        adults = int(request.form.get('adults', 0) or 0)
        children = int(request.form.get('children', 0) or 0)
        baggage = float(request.form.get('baggage', 0) or 0)
        fuel_right_main = float(request.form.get('fuel_right_main', 0) or 0)
        fuel_left_main = float(request.form.get('fuel_left_main', 0) or 0)
        fuel_tail = float(request.form.get('fuel_tail', 0) or 0)
        fuel_aux = float(request.form.get('fuel_aux', 0) or 0)
        
        # Convert values if unit preference changed
        if unit_changed and previous_unit:
            # Convert from previous unit to new unit
            if previous_unit == 'imperial' and unit == 'metric':
                # Convert lbs to kg, round to nearest 0.5 kg
                def round_to_half_kg(value):
                    return round(value * 2) / 2
                
                if pilot_weight > 0:
                    pilot_weight = round_to_half_kg(lbs_to_kg(pilot_weight))
                if copilot_weight > 0:
                    copilot_weight = round_to_half_kg(lbs_to_kg(copilot_weight))
                if pilot_baggage > 0:
                    pilot_baggage = round_to_half_kg(lbs_to_kg(pilot_baggage))
                if copilot_baggage > 0:
                    copilot_baggage = round_to_half_kg(lbs_to_kg(copilot_baggage))
                if baggage > 0:
                    baggage = round_to_half_kg(lbs_to_kg(baggage))
                if fuel_right_main > 0:
                    fuel_right_main = round_to_half_kg(lbs_to_kg(fuel_right_main))
                if fuel_left_main > 0:
                    fuel_left_main = round_to_half_kg(lbs_to_kg(fuel_left_main))
                if fuel_tail > 0:
                    fuel_tail = round_to_half_kg(lbs_to_kg(fuel_tail))
                if fuel_aux > 0:
                    fuel_aux = round_to_half_kg(lbs_to_kg(fuel_aux))
            elif previous_unit == 'metric' and unit == 'imperial':
                # Convert kg to lbs, round to nearest pound
                if pilot_weight > 0:
                    pilot_weight = round(kg_to_lbs(pilot_weight))
                if copilot_weight > 0:
                    copilot_weight = round(kg_to_lbs(copilot_weight))
                if pilot_baggage > 0:
                    pilot_baggage = round(kg_to_lbs(pilot_baggage))
                if copilot_baggage > 0:
                    copilot_baggage = round(kg_to_lbs(copilot_baggage))
                if baggage > 0:
                    baggage = round(kg_to_lbs(baggage))
                if fuel_right_main > 0:
                    fuel_right_main = round(kg_to_lbs(fuel_right_main))
                if fuel_left_main > 0:
                    fuel_left_main = round(kg_to_lbs(fuel_left_main))
                if fuel_tail > 0:
                    fuel_tail = round(kg_to_lbs(fuel_tail))
                if fuel_aux > 0:
                    fuel_aux = round(kg_to_lbs(fuel_aux))
        
        # Store form data for display
        form_data = {
            'pilot_weight': pilot_weight,
            'copilot_weight': copilot_weight,
            'pilot_baggage': pilot_baggage,
            'copilot_baggage': copilot_baggage,
            'adults': adults,
            'children': children,
            'baggage': baggage,
            'fuel_right_main': fuel_right_main,
            'fuel_left_main': fuel_left_main,
            'fuel_tail': fuel_tail,
            'fuel_aux': fuel_aux,
            'unit': unit
        }
        
        # Only perform calculations if form was submitted with data (not just unit change)
        if (pilot_weight > 0 or copilot_weight > 0 or adults > 0 or children > 0 or 
            baggage > 0 or fuel_right_main > 0 or fuel_left_main > 0 or fuel_tail > 0 or fuel_aux > 0):
            
            # Use defaults if crew weights not provided
            default_weight = 170 if unit == 'imperial' else 77.1  # 170 lbs = 77.1 kg
            if pilot_weight <= 0:
                pilot_weight = default_weight
            if copilot_weight <= 0:
                copilot_weight = default_weight
            
            # Validate max 12 passengers
            total_passengers = adults + children
            if total_passengers > 12:
                adults = min(adults, 12)
                children = min(children, 12 - adults)
            
            # Convert all inputs to pounds for calculations
            if unit == 'metric':
                pilot_weight_lbs = normalize_weight_to_lbs(pilot_weight, 'kg')
                copilot_weight_lbs = normalize_weight_to_lbs(copilot_weight, 'kg')
                pilot_baggage_lbs = normalize_weight_to_lbs(pilot_baggage, 'kg')
                copilot_baggage_lbs = normalize_weight_to_lbs(copilot_baggage, 'kg')
                baggage_lbs = normalize_weight_to_lbs(baggage, 'kg')
                fuel_right_main_lbs = normalize_weight_to_lbs(fuel_right_main, 'kg')
                fuel_left_main_lbs = normalize_weight_to_lbs(fuel_left_main, 'kg')
                fuel_tail_lbs = normalize_weight_to_lbs(fuel_tail, 'kg')
                fuel_aux_lbs = normalize_weight_to_lbs(fuel_aux, 'kg')
            else:
                pilot_weight_lbs = pilot_weight
                copilot_weight_lbs = copilot_weight
                pilot_baggage_lbs = pilot_baggage
                copilot_baggage_lbs = copilot_baggage
                baggage_lbs = baggage
                fuel_right_main_lbs = fuel_right_main
                fuel_left_main_lbs = fuel_left_main
                fuel_tail_lbs = fuel_tail
                fuel_aux_lbs = fuel_aux
            
            # Calculate weight and balance
            try:
                # Calculate OEW
                oew_result = calculate_oew(
                    pilot_weight_lbs=pilot_weight_lbs,
                    copilot_weight_lbs=copilot_weight_lbs,
                    pilot_baggage_lbs=pilot_baggage_lbs,
                    copilot_baggage_lbs=copilot_baggage_lbs
                )
                
                # Calculate passenger total weight
                total_passenger_weight_lbs = (adults * ADULT_WEIGHT + children * CHILD_WEIGHT)
                
                # Calculate ZFW
                zfw_result = calculate_zfw(
                    oew_result,
                    num_adults=adults,
                    num_children=children,
                    baggage_weight_lbs=baggage_lbs
                )
                
                # Calculate TOW
                main_fuel_total_lbs = fuel_right_main_lbs + fuel_left_main_lbs
                tow_result = calculate_tow(
                    zfw_result,
                    main_fuel_lbs=main_fuel_total_lbs,
                    aux_fuel_lbs=fuel_aux_lbs,
                    tail_fuel_lbs=fuel_tail_lbs
                )
                
                # Calculate %MAC
                percent_mac = calculate_percent_mac(tow_result['cg_xarm'], unit_system='imperial')
                
                # Store calculation results
                calculation_results = {
                    'oew': oew_result['oew'],
                    'zfw': zfw_result['zfw'],
                    'tow': tow_result['tow'],
                    'cg_xarm': tow_result['cg_xarm'],
                    'percent_mac': percent_mac,
                    'unit': unit
                }
                
                # Generate chart with calculated point
                chart_filename = generate_chart(
                    percent_mac=percent_mac,
                    tow_lbs=tow_result['tow'],
                    show_label=True
                )
            except Exception as e:
                # If calculation fails, generate chart without point
                print(f"Calculation error: {e}")
                chart_filename = generate_chart(show_label=False)
            
            # Update form_data with validated values
            form_data.update({
                'pilot_weight': pilot_weight,
                'copilot_weight': copilot_weight,
                'adults': adults,
                'children': children
            })
    
    # Generate initial chart if none exists
    if not chart_filename:
        chart_filename = generate_chart()
    
    return render_template('index.html', 
                         form_data=form_data,
                         chart_filename=chart_filename,
                         unit_preference=session.get('unit_preference', 'imperial'),
                         calculation_results=calculation_results)


@app.route('/chart/<filename>')
def serve_chart(filename):
    """Serve generated chart images."""
    return send_from_directory('static/charts', filename)


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/assets/<path:filename>')
def serve_asset(filename):
    """Serve files from the assets directory."""
    return send_from_directory('assets', filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6969))
    app.run(debug=True, host='0.0.0.0', port=port)

