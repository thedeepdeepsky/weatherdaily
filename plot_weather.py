import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
JSON_INPUT_FILE = 'weather_data.json'
# Define the plots we want to generate:
# 'json_key': ('Output File Name', 'Chart Title', 'Y-axis Label')
PLOTS_TO_GENERATE = {
    'temperature_2m': ('temperature_chart.png', 'Hourly Temperature Forecast (Shanghai)', 'Temperature (°C)'),
    'cloud_cover': ('cloud_cover_total_chart.png', 'Hourly Total Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)'),
    'cloud_cover_low': ('cloud_cover_low_chart.png', 'Hourly Low Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)'),
    'cloud_cover_mid': ('cloud_cover_mid_chart.png', 'Hourly Mid Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)'),
    'cloud_cover_high': ('cloud_cover_high_chart.png', 'Hourly High Cloud Cover Forecast (Shanghai)', 'Cloud Cover (%)'),
}
# --- End Configuration ---

print(f"Starting weather chart generation...")
print(f"Input JSON: {JSON_INPUT_FILE}")

# Check if input file exists
if not os.path.exists(JSON_INPUT_FILE):
    print(f"Error: Input file '{JSON_INPUT_FILE}' not found.")
    exit(1)

# Function to generate a single plot
def generate_plot(dataframe, time_col, data_col, output_filename, title, y_label):
    """Generates and saves a single plot."""
    print(f"--- Generating plot for {data_col} -> {output_filename} ---")
    if data_col not in dataframe.columns:
        print(f"Warning: Data column '{data_col}' not found in DataFrame. Skipping plot.")
        return False # Indicate failure/skip

    fig, ax = plt.subplots(figsize=(15, 7)) # Adjust figure size as needed

    # Plot the data
    ax.plot(dataframe[time_col], dataframe[data_col], marker='.', linestyle='-', label=y_label) # Use y_label for the legend too

    # Formatting the plot
    ax.set_title(title)
    ax.set_xlabel('Time')
    ax.set_ylabel(y_label)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    # Specific formatting for cloud cover (usually 0-100)
    if 'Cloud Cover' in y_label:
         ax.set_ylim(0, 105) # Set Y-axis limits for percentage

    # Formatting the x-axis (dates/times)
    fig.autofmt_xdate(rotation=45)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    # ax.xaxis.set_major_locator(mdates.HourLocator(interval=6)) # Optional: Adjust tick frequency

    plt.tight_layout() # Adjust layout

    # Save the plot to a file
    try:
        plt.savefig(output_filename, dpi=100) # Adjust dpi for resolution
        print(f"Chart successfully saved to '{output_filename}'")
        success = True
    except Exception as e:
        print(f"Error saving plot {output_filename}: {e}")
        success = False

    plt.close(fig) # Close the plot figure to free memory
    return success


# --- Main script execution ---
generated_files = []
try:
    # Read the JSON data
    with open(JSON_INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Extract hourly data into a pandas DataFrame
    hourly_data = data.get('hourly', {})
    if not hourly_data or 'time' not in hourly_data:
        print("Error: JSON structure is missing 'hourly' or 'hourly.time' key.")
        exit(1)

    # Ensure 'time' is present before creating DataFrame
    required_keys = ['time'] + list(PLOTS_TO_GENERATE.keys())
    available_keys = [key for key in required_keys if key in hourly_data]
    missing_keys = [key for key in required_keys if key not in hourly_data]

    if missing_keys:
         print(f"Warning: The following expected keys are missing in the 'hourly' data: {', '.join(missing_keys)}")
         # Decide if this is fatal or just means some plots won't be generated
         # if 'time' not in available_keys: exit(1) # Exit if time is missing

    # Create DataFrame only with available data columns
    df_data = {key: hourly_data[key] for key in available_keys}
    df = pd.DataFrame(df_data)
    df['time'] = pd.to_datetime(df['time']) # Convert time strings to datetime objects

    if df.empty or 'time' not in df.columns:
        print("Error: No time data found or DataFrame is empty.")
        exit(1)

    print(f"Successfully parsed {len(df)} hourly data points.")
    print(f"Available data columns for plotting: {', '.join(df.columns)}")

    # Loop through the defined plots and generate each one
    for json_key, (output_file, title, y_label) in PLOTS_TO_GENERATE.items():
        if json_key in df.columns: # Only attempt to plot if data exists
            if generate_plot(df, 'time', json_key, output_file, title, y_label):
                generated_files.append(output_file) # Keep track of successfully generated files
        else:
            print(f"Skipping plot for '{json_key}' as data is missing.")


except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from '{JSON_INPUT_FILE}'. Is it valid JSON?")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Consider printing traceback for debugging:
    # import traceback
    # traceback.print_exc()
    exit(1)

if not generated_files:
     print("Error: No chart files were generated successfully.")
     exit(1)

print(f"Chart generation script finished. Generated files: {', '.join(generated_files)}")
