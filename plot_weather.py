import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd # Using pandas simplifies datetime handling and data access
import os
from datetime import datetime

# --- Configuration ---
JSON_INPUT_FILE = 'weather_data.json'
CHART_OUTPUT_FILE = 'weather_chart.png'
CHART_TITLE = 'Hourly Temperature Forecast (Shanghai)'
X_LABEL = 'Time'
Y_LABEL = 'Temperature (°C)'
# --- End Configuration ---

print(f"Starting weather chart generation...")
print(f"Input JSON: {JSON_INPUT_FILE}")
print(f"Output Chart: {CHART_OUTPUT_FILE}")

# Check if input file exists
if not os.path.exists(JSON_INPUT_FILE):
    print(f"Error: Input file '{JSON_INPUT_FILE}' not found.")
    exit(1)

try:
    # Read the JSON data using pandas for easier handling
    with open(JSON_INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Extract hourly data into a pandas DataFrame
    hourly_data = data.get('hourly', {})
    if not hourly_data or 'time' not in hourly_data or 'temperature_2m' not in hourly_data:
        print("Error: JSON structure is missing 'hourly', 'time', or 'temperature_2m' keys.")
        exit(1)

    df = pd.DataFrame({
        'time': pd.to_datetime(hourly_data['time']), # Convert time strings to datetime objects
        'temperature_2m': hourly_data['temperature_2m']
    })

    if df.empty:
        print("Error: No hourly data found in the JSON file.")
        exit(1)

    print(f"Successfully parsed {len(df)} hourly data points.")

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(15, 7)) # Adjust figure size as needed

    # Plot the temperature data
    ax.plot(df['time'], df['temperature_2m'], marker='.', linestyle='-', color='tab:blue', label='Temperature (°C)')

    # Formatting the plot
    ax.set_title(CHART_TITLE)
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel(Y_LABEL)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    # Formatting the x-axis (dates/times)
    # Auto-format dates for better readability
    fig.autofmt_xdate(rotation=45)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) # Customize format if needed
    # Optional: Set major locator frequency (e.g., every 6 hours)
    # ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))

    plt.tight_layout() # Adjust layout to prevent labels overlapping

    # Save the plot to a file
    plt.savefig(CHART_OUTPUT_FILE, dpi=100) # Adjust dpi for resolution
    print(f"Chart successfully saved to '{CHART_OUTPUT_FILE}'")

    plt.close(fig) # Close the plot figure to free memory

except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from '{JSON_INPUT_FILE}'. Is it valid JSON?")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during plotting: {e}")
    exit(1)

print("Chart generation script finished successfully.")
