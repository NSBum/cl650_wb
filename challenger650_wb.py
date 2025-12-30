"""
Chart generation functions for Challenger 650 weight and balance visualization.

Copyright (c) 2025 Alan Duncan
Licensed under MIT License with Non-Commercial Use Restriction.
See LICENSE file for details.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import textwrap
from utils import lbs_to_kg


def draw_wb_grid(figsize=(6.7, 7.5), dpi=100):
    """
    Create a weight and balance chart for the Challenger 650 aircraft. This draws the grid and the axes.
    
    Parameters:
    -----------
    figsize : tuple, optional
        Figure size in inches (width, height). Default is (6.7, 7.5) to match 
        the portrait aspect ratio of 1184:1326 (approximately 0.892) while 
        fitting vertically in a typical window.
    dpi : int, optional
        Resolution of the figure. Default is 100.
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object containing the chart
    ax : matplotlib.axes.Axes
        The main axes object (left y-axis)
    ax2 : matplotlib.axes.Axes
        The secondary axes object (right y-axis)
    """
    # Create figure and axes
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Set up horizontal axis: AIRCRAFT GG %MAC from 15 to 40
    ax.set_xlim(15, 40)
    ax.set_xlabel('AIRCRAFT GG %MAC', fontsize=12, fontweight='bold')
    # Ticks at each 1 % MAC, but labels only every 5 %MAC
    ax.set_xticks(np.arange(15, 41, 1))
    ax.set_xticklabels([f'{int(x)}' if x % 5 == 0 else '' for x in np.arange(15, 41, 1)], fontsize=9)
    ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.7, color='#B5B5B5')
    ax.grid(True, which='minor', linestyle='--', linewidth=0.3, alpha=0.5, color='#B5B5B5')
    ax.set_xticks(np.arange(15, 41, 1), minor=True)
    
    # Set up left vertical axis: AIRCRAFT WEIGHT (1,000 LB) from 25 to 50
    ax.set_ylim(25, 50)
    ax.set_ylabel('AIRCRAFT WEIGHT (1,000 LB)', fontsize=12, fontweight='bold')
    # Ticks every 1000 lbs (every 1 unit) and labels every 5000 lbs (every 5 units)
    ax.set_yticks(np.arange(25, 51, 1))
    ax.set_yticklabels([f'{int(y)}' if y % 5 == 0 else '' for y in np.arange(25, 51, 1)], fontsize=10)
    ax.grid(True, which='major', axis='y', linestyle='-', linewidth=0.5, alpha=0.7, color='#B5B5B5')
    ax.grid(True, which='minor', axis='y', linestyle='--', linewidth=0.3, alpha=0.5, color='#B5B5B5')
    ax.set_yticks(np.arange(25, 51, 1), minor=True)
    
    # Set up right vertical axis: AIRCRAFT WEIGHT (1,000 KG)
    # Conversion: 1 lb = LBS_TO_KG kg, so 1,000 lb = 1000 * LBS_TO_KG kg ≈ 0.454 (1,000 KG units)
    # Range: 25,000 lb = 25 * 1000 * LBS_TO_KG kg ≈ 11.34 (1,000 KG units)
    #         50,000 lb = 50 * 1000 * LBS_TO_KG kg ≈ 22.68 (1,000 KG units)
    ax2 = ax.twinx()
    ax2.set_ylim(lbs_to_kg(25), lbs_to_kg(50))  # Convert from 1,000 LB to 1,000 KG
    ax2.set_ylabel('AIRCRAFT WEIGHT (1,000 KG)', fontsize=12, fontweight='bold')
    # Ticks every 1000 lbs equivalent (every LBS_TO_KG units) and labels every 5000 lbs equivalent
    kg_ticks = lbs_to_kg(np.arange(25, 51, 1))
    ax2.set_yticks(kg_ticks)
    ax2.set_yticklabels([f'{lbs_to_kg(y):.1f}' if y % 5 == 0 else '' for y in np.arange(25, 51, 1)], fontsize=10)
    ax2.set_yticks(kg_ticks, minor=True)
    ax2.grid(False)  # Don't duplicate grid lines from left axis
    
    # Set title
    ax.set_title('CHALLENGER 650 WEIGHT AND BALANCE', fontsize=14, fontweight='bold', pad=15)
    
    # Add note below X axis in italics
    note_text = '[✲ For zero fuel weight in that region, refer to Figure 3, 01−20−20, Auxiliary and Tail Tank Admissible Ratio (for ZFW CG inside lower aft zone of CG envelope)]'
    
    # Wrap text to 75% of graph width
    # Graph width is 6.7 inches, 75% = 5.025 inches
    # At fontsize 8, approximate character width is ~0.07 inches per character
    # So 5.025 / 0.07 ≈ 72 characters per line
    # Using a slightly conservative estimate for better wrapping
    wrapped_text = textwrap.fill(note_text, width=65)
    
    ax.text(0.5, -0.08, wrapped_text, transform=ax.transAxes, 
            fontsize=8, style='italic', ha='center', va='top')
    
    # Adjust layout to fit in window
    plt.tight_layout()
    
    return fig, ax, ax2


def draw_envelope(ax, linewidth=1.0, color='black'):
    """
    Draw the weight and balance envelope polygon on the chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    linewidth : float, optional
        Line width for the envelope outline. Default is 1.0 (heavier than grid lines).
    color : str, optional
        Color of the envelope outline. Default is 'black'.
    
    Returns:
    --------
    polygon : matplotlib.patches.Polygon
        The polygon object representing the envelope
    """
    # Envelope vertices (X: %MAC, Y: Weight in 1,000 LB)
    envelope_vertices = [
        (20, 26),
        (20, 38),
        (16, 39.5),
        (16, 44.75),
        (21, 48.2),
        (38, 48.2),
        (38, 43),
        (35, 38),
        (35, 26)
    ]
    
    # Create polygon patch (unfilled, outline only)
    polygon = mpatches.Polygon(envelope_vertices, closed=True, 
                               fill=False, edgecolor=color, 
                               linewidth=linewidth, zorder=10)
    
    # Add polygon to axes
    ax.add_patch(polygon)
    
    return polygon


def draw_no_takeoff_zone(ax, color='#A4A4A4', edgecolor='black', linewidth=1.0):
    """
    Draw the no-takeoff zone (stippled zone) on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    color : str, optional
        Color of the stipple dots. Default is '#A4A4A4' (light gray).
    edgecolor : str, optional
        Color of the zone outline. Default is 'black'.
    linewidth : float, optional
        Line width for the zone outline. Default is 1.0.
    
    Returns:
    --------
    tuple : (stippled_polygon, outline_polygon)
        Tuple containing the stippled polygon and outline polygon objects
    """
    # Zone vertices (X: %MAC, Y: Weight in 1,000 LB)
    zone_vertices = [
        (16, 39.5),
        (16, 44.75),
        (21, 48.2),
        (29, 48.2)
    ]
    
    # Create polygon patch with stippled fill pattern
    # Using '.' hatch pattern for dots (stippling)
    # The pattern creates dots with approximately 25% area coverage
    # Note: hatch color is controlled by edgecolor in matplotlib
    # First draw the stippled pattern with lighter color
    stippled_polygon = mpatches.Polygon(zone_vertices, closed=True,
                                        facecolor='none',  # No solid fill
                                        edgecolor=color,  # Use lighter color for stipples
                                        linewidth=0.5,  # Thinner for stipples
                                        hatch='...',  # Multiple dots for stippled pattern
                                        zorder=5)  # Draw behind envelope but above grid
    
    # Then draw the outline in black
    outline_polygon = mpatches.Polygon(zone_vertices, closed=True,
                                      fill=False,  # No fill
                                      edgecolor=edgecolor,
                                      linewidth=linewidth,
                                      zorder=6)  # Draw on top of stipples
    
    # Add polygons to axes
    ax.add_patch(stippled_polygon)
    ax.add_patch(outline_polygon)
    
    # Add "TAKE-OFF LIMIT" text along and below the line from (16, 39.5) to (29, 48.2)
    x1, y1 = 16, 39.5
    x2, y2 = 29, 48.2
    
    # Calculate midpoint of the line
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # Calculate angle of the line in display coordinates for proper visual alignment
    # Transform the two points to display coordinates
    trans = ax.transData
    point1_display = trans.transform([x1, y1])
    point2_display = trans.transform([x2, y2])
    
    # Calculate angle in display coordinates
    dx_display = point2_display[0] - point1_display[0]
    dy_display = point2_display[1] - point1_display[1]
    angle_deg = np.degrees(np.arctan2(dy_display, dx_display))
    
    # Calculate angle in data coordinates for offset calculation
    dx = x2 - x1
    dy = y2 - y1
    angle_rad = np.arctan2(dy, dx)
    
    # Position text below and to the right of the line (offset perpendicular to the line)
    # Offset distance in data coordinates
    offset_distance = 0.8
    # Perpendicular offset: vector perpendicular to line pointing below and to the right
    # For a line with direction (dx, dy), perpendicular is (-dy, dx) or (dy, -dx)
    # We want below and right, so use (dy, -dx) normalized and scaled
    perp_length = np.sqrt(dx**2 + dy**2)
    offset_x = offset_distance * dy / perp_length  # Positive = right
    offset_y = -offset_distance * dx / perp_length  # Negative = below (y increases upward)
    
    text_x = mid_x + offset_x
    text_y = mid_y + offset_y
    
    # Add text rotated to match the line angle (using display coordinate angle)
    ax.text(text_x, text_y, 'TAKE-OFF LIMIT', 
            rotation=angle_deg, rotation_mode='anchor',
            ha='center', va='center',
            fontsize=9, fontweight='bold',
            zorder=7)  # Draw above polygons
    
    return stippled_polygon, outline_polygon


def draw_min_zone(ax, color='#A4A4A4', edgecolor='black', linewidth=1.0):
    """
    Draw the minimum zone (stippled zone) on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    color : str, optional
        Color of the stipple dots. Default is '#A4A4A4' (light gray).
    edgecolor : str, optional
        Color of the zone outline. Default is 'black'.
    linewidth : float, optional
        Line width for the zone outline. Default is 1.0.
    
    Returns:
    --------
    tuple : (stippled_polygon, outline_polygon)
        Tuple containing the stippled polygon and outline polygon objects
    """
    # Zone vertices (X: %MAC, Y: Weight in 1,000 LB)
    zone_vertices = [
        (32.5, 26),
        (34, 28),
        (34, 30),
        (35, 32),
        (35, 26)
    ]
    
    # Create polygon patch with stippled fill pattern
    # Using '.' hatch pattern for dots (stippling)
    # The pattern creates dots with approximately 25% area coverage
    # First draw the stippled pattern with lighter color
    stippled_polygon = mpatches.Polygon(zone_vertices, closed=True,
                                        facecolor='none',  # No solid fill
                                        edgecolor=color,  # Use lighter color for stipples
                                        linewidth=0.5,  # Thinner for stipples
                                        hatch='...',  # Multiple dots for stippled pattern
                                        zorder=5)  # Draw behind envelope but above grid
    
    # Then draw the outline in black
    outline_polygon = mpatches.Polygon(zone_vertices, closed=True,
                                      fill=False,  # No fill
                                      edgecolor=edgecolor,
                                      linewidth=linewidth,
                                      zorder=6)  # Draw on top of stipples
    
    # Add polygons to axes
    ax.add_patch(stippled_polygon)
    ax.add_patch(outline_polygon)
    
    # Add symbol "✲" at (34.5, 27.6)
    ax.text(34.5, 27.6, '✲', 
            ha='center', va='center',
            fontsize=12,
            zorder=7)  # Draw above polygons
    
    return stippled_polygon, outline_polygon


def draw_mfw_text(ax, x=21.6, y=26.6, fontsize=9):
    """
    Draw the Maximum Fuel Weight (MFW) text on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    x : float, optional
        X position for the text. Default is 21.6 (%MAC).
    y : float, optional
        Y position for the text. Default is 26.6 (Weight in 1,000 LB).
    fontsize : int, optional
        Font size for the text. Default is 9.
    
    Returns:
    --------
    text : matplotlib.text.Text
        The text object representing the MFW label
    """
    mfw_text = ax.text(x, y, 'MFW (26 000 lb/11 794 kg)', 
                       ha='left', va='bottom',
                       fontsize=fontsize, fontweight='bold',
                       zorder=7)  # Draw above polygons
    
    return mfw_text


def draw_mzfw_line(ax, x1=20, y=32, x2=35, linewidth=1.0, color='black', fontsize=9, 
                   point_x=None, point_y=None):
    """
    Draw the Maximum Zero Fuel Weight (MZFW) line and text on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    x1 : float, optional
        Starting X position of the line. Default is 20 (%MAC).
    y : float, optional
        Y position of the line. Default is 32 (Weight in 1,000 LB).
    x2 : float, optional
        Ending X position of the line. Default is 35 (%MAC).
    linewidth : float, optional
        Line width. Default is 1.0.
    color : str, optional
        Color of the line. Default is 'black'.
    fontsize : int, optional
        Font size for the text. Default is 9.
    point_x : float, optional
        X coordinate of plotted point to check for collision. If None, no collision check.
    point_y : float, optional
        Y coordinate of plotted point to check for collision. If None, no collision check.
    
    Returns:
    --------
    tuple : (line, text)
        Tuple containing the line and text objects
    """
    # Draw the horizontal line
    line = ax.plot([x1, x2], [y, y], 
                   color=color, linewidth=linewidth,
                   zorder=7)  # Draw above polygons
    
    # Calculate midpoint for text positioning
    mid_x = (x1 + x2) / 2
    
    # Check if point would overlap with the label area
    # Label is positioned at y + 0.3 with va='bottom', so text extends upward from there
    # We check if point is in the label's vertical space (line to line + offset + text height margin)
    label_offset = 0.3
    label_height_margin = 0.5  # Approximate text height in data coordinates
    label_top = y + label_offset + label_height_margin
    
    point_near_label = False
    if point_x is not None and point_y is not None:
        # Check if point is within the line's x-range and in the label's vertical space
        if (x1 <= point_x <= x2) and (y <= point_y <= label_top):
            point_near_label = True
    
    # Position text above or below the line based on collision detection
    if point_near_label:
        text_y = y - label_offset  # Offset below the line
        va = 'top'  # Align text top to the line
    else:
        text_y = y + label_offset  # Offset above the line
        va = 'bottom'  # Align text bottom to the line
    
    # Add bold text
    text = ax.text(mid_x, text_y, 'MZFW (32 000 lb/14 515 kg)', 
                   ha='center', va=va,
                   fontsize=fontsize, fontweight='bold',
                   zorder=8)  # Draw above the line
    
    return line[0], text


def draw_mlw_line(ax, x1=20, y=38, x2=35, linewidth=1.0, color='black', fontsize=9,
                  point_x=None, point_y=None):
    """
    Draw the Maximum Landing Weight (MLW) line and text on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    x1 : float, optional
        Starting X position of the line. Default is 20 (%MAC).
    y : float, optional
        Y position of the line. Default is 38 (Weight in 1,000 LB).
    x2 : float, optional
        Ending X position of the line. Default is 35 (%MAC).
    linewidth : float, optional
        Line width. Default is 1.0.
    color : str, optional
        Color of the line. Default is 'black'.
    fontsize : int, optional
        Font size for the text. Default is 9.
    point_x : float, optional
        X coordinate of plotted point to check for collision. If None, no collision check.
    point_y : float, optional
        Y coordinate of plotted point to check for collision. If None, no collision check.
    
    Returns:
    --------
    tuple : (line, text)
        Tuple containing the line and text objects
    """
    # Draw the horizontal line
    line = ax.plot([x1, x2], [y, y], 
                   color=color, linewidth=linewidth,
                   zorder=7)  # Draw above polygons
    
    # Calculate midpoint for text positioning
    mid_x = (x1 + x2) / 2
    
    # Check if point would overlap with the label area
    # Label is positioned at y + 0.3 with va='bottom', so text extends upward from there
    # We check if point is in the label's vertical space (line to line + offset + text height margin)
    label_offset = 0.3
    label_height_margin = 0.5  # Approximate text height in data coordinates
    label_top = y + label_offset + label_height_margin
    
    point_near_label = False
    if point_x is not None and point_y is not None:
        # Check if point is within the line's x-range and in the label's vertical space
        if (x1 <= point_x <= x2) and (y <= point_y <= label_top):
            point_near_label = True
    
    # Position text above or below the line based on collision detection
    if point_near_label:
        text_y = y - label_offset  # Offset below the line
        va = 'top'  # Align text top to the line
    else:
        text_y = y + label_offset  # Offset above the line
        va = 'bottom'  # Align text bottom to the line
    
    # Add bold text
    text = ax.text(mid_x, text_y, 'MLW (38 000 lb/17 237 kg)', 
                   ha='center', va=va,
                   fontsize=fontsize, fontweight='bold',
                   zorder=8)  # Draw above the line
    
    return line[0], text


def draw_point(ax, x, y, color='#0885A0', diameter=0.25):
    """
    Draw a filled circle (point) on the weight and balance chart.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to draw on (should be the main axes with left y-axis)
    x : float
        X position of the center (%MAC).
    y : float
        Y position of the center (Weight in 1,000 LB).
    color : str, optional
        Fill color of the circle. Default is '#0885A0' (blue).
    diameter : float, optional
        Diameter of the circle in data coordinates. Default is 0.25.
    
    Returns:
    --------
    circle : matplotlib.patches.Circle
        The circle object representing the point
    """
    radius = diameter / 2
    
    circle = mpatches.Circle((x, y), radius,
                            color=color,
                            zorder=9)  # Draw above most elements
    
    ax.add_patch(circle)
    
    return circle


if __name__ == '__main__':
    # Example usage: create and display the chart
    fig, ax, ax2 = draw_wb_grid()
    draw_no_takeoff_zone(ax)
    draw_min_zone(ax)
    draw_mfw_text(ax)
    draw_mzfw_line(ax)
    draw_mlw_line(ax)
    draw_envelope(ax)
    # Test point: plot in main zone but not in stippled regions (e.g., around 25, 30)
    draw_point(ax, 25, 30)
    plt.show()

