import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import numpy as np # Needed for wind direction potentially
from datetime import datetime

# --- Configuration ---
JSON_INPUT_FILE = 'weather_data.json'
# Define the plots we want to generate:
# 'json_key': ('Output File Name', 'Chart Title', 'Y-axis Label', 'Plot Type (line/bar)', 'Y-lim (optional tuple)')
PLOTS_TO_GENERATE = {
    # Existing Plots
    'temperature_2m': ('temperature_chart.png', 'Hourly Temperature Forecast (Shanghai)', 'Temperature (°C)', 'line', None),
    'cloud_cover': ('cloud_cover_total_chart.png', 'Hourly Total Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)', 'line', (0, 105)),
    'cloud_cover_low': ('cloud_cover_low_chart.png', 'Hourly Low Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)', 'line', (0, 105)),
    'cloud_cover_mid': ('cloud_cover_mid_chart.png', 'Hourly Mid Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)', 'line', (0, 105)),
    'cloud_cover_high': ('cloud_cover_high_chart.png', 'Hourly High Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)', 'line', (0, 105)),

    # New Plots - Wind Speed
    'wind_speed_10m': ('wind_speed_10m_chart.png', 'Hourly Wind Speed (10m) Forecast (Shanghai)', 'Wind Speed (km/h)', 'line', (0, None)),
    'wind_speed_80m': ('wind_speed_80m_chart.png', 'Hourly Wind Speed (80m) Forecast (Shanghai)', 'Wind Speed (km/h)', 'line', (0, None)),
    'wind_speed_120m': ('wind_speed_120m_chart.png', 'Hourly Wind Speed (120m) Forecast (Shanghai)', 'Wind Speed (km/h)', 'line', (0, None)),
    'wind_speed_180m': ('wind_speed_180m_chart.png', 'Hourly Wind Speed (180m) Forecast (Shanghai)', 'Wind Speed (km/h)', 'line', (0, None)),

    # New Plots - Wind Direction (Plotting as line 0-360, limitations apply)
    'wind_direction_10m': ('wind_direction_10m_chart.png', 'Hourly Wind Direction (10m) Forecast (Shanghai)', 'Direction (°)', 'line', (0, 360)),
    'wind_direction_80m': ('wind_direction_80m_chart.png', 'Hourly Wind Direction (80m) Forecast (Shanghai)', 'Direction (°)', 'line', (0, 360)),
    'wind_direction_120m': ('wind_direction_120m_chart.png', 'Hourly Wind Direction (120m) Forecast (Shanghai)', 'Direction (°)', 'line', (0, 360)),
    'wind_direction_180m': ('wind_direction_180m_chart.png', 'Hourly Wind Direction (180m) Forecast (Shanghai)', 'Direction (°)', 'line', (0, 360)),

    # New Plots - Other
    'wind_gusts_10m': ('wind_gusts_10m_chart.png', 'Hourly Wind Gusts (10m) Forecast (Shanghai)', 'Wind Gusts (km/h)', 'line', (0, None)),
    'apparent_temperature': ('apparent_temperature_chart.png', 'Hourly Apparent Temperature Forecast (Shanghai)', 'Temperature (°C)', 'line', None),
    'precipitation_probability': ('precipitation_probability_chart.png', 'Hourly Precipitation Probability Forecast (Shanghai)', 'Probability (%)', 'line', (0, 105)),

    # New Plots - Precipitation (Using bar chart might be better, but line for consistency now)
    # Consider changing plot_type to 'bar' if preferred
    'precipitation': ('precipitation_chart.png', 'Hourly Precipitation Forecast (Shanghai)', 'Precipitation (mm)', 'line', (0, None)),
    'rain': ('rain_chart.png', 'Hourly Rain Forecast (Shanghai)', 'Rain (mm)', 'line', (0, None)),
    'showers': ('showers_chart.png', 'Hourly Showers Forecast (Shanghai)', 'Showers (mm)', 'line', (0, None)),
}
# --- End Configuration ---

print(f"Starting weather chart generation...")
print(f"Input JSON: {JSON_INPUT_FILE}")

# Check if input file exists
if not os.path.exists(JSON_INPUT_FILE):
    print(f"Error: Input file '{JSON_INPUT_FILE}' not found.")
    exit(1)

# Function to generate a single plot
def generate_plot(dataframe, time_col, data_col, output_filename, title, y_label, plot_type='line', y_limits=None):
    """Generates and saves a single plot."""
    print(f"--- Generating {plot_type} plot for {data_col} -> {output_filename} ---")
    if data_col not in dataframe.columns or dataframe[data_col].isnull().all():
        print(f"Warning: Data column '{data_col}' not found or contains only null values in DataFrame. Skipping plot.")
        return False # Indicate failure/skip

    fig, ax = plt.subplots(figsize=(15, 7))

    # Plot the data based on type
    if plot_type == 'line':
        ax.plot(dataframe[time_col], dataframe[data_col], marker='.', linestyle='-', label=y_label)
    elif plot_type == 'bar':
         # Calculate width based on time difference for better spacing
        time_diff = dataframe[time_col].diff().median() # Get typical time step
        width = time_diff / np.timedelta64(1, 'D') * 0.8 # Bar width as fraction of day (adjust 0.8 factor as needed)
        ax.bar(dataframe[time_col], dataframe[data_col], label=y_label, width=width, align='center')
    else:
        print(f"Warning: Unknown plot type '{plot_type}' for {data_col}. Defaulting to line plot.")
        ax.plot(dataframe[time_col], dataframe[data_col], marker='.', linestyle='-', label=y_label)

    # Formatting the plot
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5) # Grid lines horizontal only often looks cleaner
    if plot_type != 'bar': # Legend might overlap bars
         ax.legend()

    # Apply Y-axis limits if specified
    if y_limits:
        ax.set_ylim(y_limits)
    elif y_label == 'Direction (°)': # Specific handling for Direction
        ax.set_ylim(0, 360)
        ax.set_yticks(np.arange(0, 361, 45)) # Set ticks at 45 degree intervals (N, NE, E, SE, S, SW, W, NW)
    elif 'mm' in y_label or 'km/h' in y_label: # Precipitation/Wind Speed shouldn't go below 0
        ax.set_ylim(bottom=0)

    # Formatting the x-axis (dates/times)
    fig.autofmt_xdate(rotation=45)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    # ax.xaxis.set_major_locator(mdates.HourLocator(interval=6)) # Optional

    plt.tight_layout() # Adjust layout

    # Save the plot to a file
    try:
        plt.savefig(output_filename, dpi=100)
        print(f"Chart successfully saved to '{output_filename}'")
        success = True
    except Exception as e:
        print(f"Error saving plot {output_filename}: {e}")
        success = False

    plt.close(fig) # Close the plot figure
    return success


# --- Main script execution ---
# (Keep the main execution block from the previous version, it should work fine)
# It reads the JSON, creates the DataFrame, checks for missing keys,
# and iterates through PLOTS_TO_GENERATE calling generate_plot.
generated_files = []
try:
    # Read the JSON data
    with open(JSON_INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Extract hourly data
    hourly_data = data.get('hourly', {})
    if not hourly_data or 'time' not in hourly_data:
        print("Error: JSON structure is missing 'hourly' or 'hourly.time' key.")
        exit(1)

    # Get list of all keys we *want* to plot (plus 'time')
    required_keys = ['time'] + list(PLOTS_TO_GENERATE.keys())
    # Find which of these keys are *actually available* in the fetched data
    available_keys = [key for key in required_keys if key in hourly_data]
    missing_keys = [key for key in required_keys if key not in hourly_data]

    if missing_keys:
        print(f"Warning: The following expected keys are missing in the 'hourly' data: {', '.join(missing_keys)}")
        # Allow script to continue if some data is missing, just skip those plots

    # Create DataFrame *only* with available data columns to prevent errors
    # Convert potentially missing columns to None before creating DataFrame to ensure all keys exist if needed later?
    # Safer: Create dict with only available data
    df_data = {}
    for key in available_keys:
      # Check if the value associated with the key is not None and is iterable (list)
      # Handle case where API might return null for a variable sometimes
      if hourly_data[key] is not None and isinstance(hourly_data[key], list):
        df_data[key] = hourly_data[key]
      else:
        print(f"Warning: Data for key '{key}' is null or not a list. Skipping this variable.")
        if key in available_keys: available_keys.remove(key) # Remove from available list

    # Ensure 'time' data is valid before proceeding
    if 'time' not in df_data:
        print(f"Error: Critical key 'time' is missing or invalid in the fetched data. Cannot proceed.")
        exit(1)

    # Check for length consistency (important!)
    first_key_len = len(df_data['time'])
    for key, values in df_data.items():
        if len(values) != first_key_len:
            print(f"Error: Data length mismatch for key '{key}' (expected {first_key_len}, got {len(values)}). API data inconsistent?")
            # Optionally remove the inconsistent key:
            # del df_data[key]
            # available_keys.remove(key)
            # For now, let pandas handle potential errors or proceed with caution
            # Depending on pandas version, it might raise an error or fill with NaN
            pass # Let it proceed, pandas might handle it.

    try:
        df = pd.DataFrame(df_data)
    except ValueError as ve:
        print(f"Error creating DataFrame, likely due to inconsistent data lengths: {ve}")
        exit(1)


    df['time'] = pd.to_datetime(df['time']) # Convert time strings to datetime objects

    if df.empty or 'time' not in df.columns:
        print("Error: No time data found or DataFrame is empty after processing.")
        exit(1)

    print(f"Successfully parsed {len(df)} hourly data points.")
    print(f"Available data columns for plotting: {', '.join(df.columns)}")

    # Loop through the defined plots and generate each one
    for json_key, (output_file, title, y_label, plot_type, y_limits) in PLOTS_TO_GENERATE.items():
        if json_key in df.columns: # Only attempt to plot if data column exists in DataFrame
            if generate_plot(df, 'time', json_key, output_file, title, y_label, plot_type, y_limits):
                generated_files.append(output_file) # Keep track of successfully generated files
        # No need for an else here, missing keys handled earlier

except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from '{JSON_INPUT_FILE}'. Is it valid JSON?")
    exit(1)
except KeyError as e:
    print(f"Error: Missing expected key in JSON data: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during script execution: {e}")
    # import traceback # Uncomment for detailed debugging
    # traceback.print_exc() # Uncomment for detailed debugging
    exit(1)

if not generated_files:
    print("Warning: No chart files were generated successfully.")
    # Don't exit with error code 1 here, maybe the JSON was valid but empty for all plot vars
    # The commit step will handle the "no files found" case.
    # exit(1) # Changed to not exit with error

print(f"Chart generation script finished. Generated files: {', '.join(generated_files)}")
