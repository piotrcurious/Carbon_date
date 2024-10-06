import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
import csv
from io import StringIO
from datetime import datetime, timedelta

# Constants
TARGET_YEAR = 2050
TARGET_TEMP = 1.5  # The 1.5°C target anomaly

# Function to fetch global temperature anomaly data from NASA GISTEMP
def fetch_global_temperature_data():
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    
    try:
        # Fetch the CSV data from NASA GISTEMP
        response = requests.get(url)
        response.raise_for_status()  # Raise error if request fails

        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        temperature_data = []
        
        # Skip the first few header lines and then read the data
        for row in reader:
            if len(row) > 1 and row[0].isdigit():
                year = int(row[0])
                try:
                    anomaly = float(row[13]) if row[13] else None
                except ValueError:
                    anomaly = None  # Handle missing or invalid data
                if anomaly is not None:
                    temperature_data.append({"year": year, "anomaly": anomaly})
        
        if not temperature_data:
            raise ValueError("No valid temperature data found.")

        return temperature_data

    except Exception as e:
        raise Exception(f"Failed to fetch or parse data: {e}")

# Function to get the anomaly for a given year from the dataset
def get_anomaly_for_year(year, temperature_data):
    for record in temperature_data:
        if record['year'] == year:
            return record['anomaly']
    return None

# Function to calculate the expected anomaly for a given year
def calculate_expected_anomaly(current_year, current_anomaly):
    years_to_2050 = TARGET_YEAR - current_year
    anomaly_increase = TARGET_TEMP - current_anomaly
    shift_per_year = anomaly_increase / years_to_2050 if years_to_2050 != 0 else 0
    return current_anomaly + shift_per_year

# Function to calculate the warped date and anomaly difference
def adjust_date_based_on_anomaly(temperature_data):
    current_year = datetime.now().year
    current_anomaly = get_anomaly_for_year(current_year, temperature_data)
    
    if current_anomaly is None:
        raise ValueError(f"No anomaly data available for year {current_year}.")
    
    expected_anomaly = calculate_expected_anomaly(current_year, current_anomaly)
    anomaly_difference = current_anomaly - expected_anomaly
    days_shift = anomaly_difference * 365  # Days shifted based on anomaly difference
    adjusted_date = datetime.now() + timedelta(days=days_shift)
    
    return adjusted_date, anomaly_difference

# Function to calculate the time warp rate for the last 12 months
def calculate_time_warp_data(temperature_data):
    current_year = datetime.now().year
    months = []
    warp_rates = []
    
    for i in range(12):
        year = current_year - i
        anomaly = get_anomaly_for_year(year, temperature_data)
        if anomaly is not None:
            expected_anomaly = calculate_expected_anomaly(year, anomaly)
            anomaly_difference = anomaly - expected_anomaly
            warp_rate = anomaly_difference * 365  # Days shifted based on anomaly difference
            warp_rates.append(warp_rate)
            months.append(f"{year}")
    
    if not warp_rates:
        raise ValueError("Not enough valid data to calculate warp rates.")

    return months[::-1], warp_rates[::-1]

# Function to create the Tkinter window with the carbon clock and derivative graph
def create_gui_window(temperature_data):
    root = tk.Tk()
    root.title("Carbon Clock with Time Warp")

    # Frame for carbon clock display
    frame_clock = tk.Frame(root)
    frame_clock.pack(pady=10)

    # Carbon clock display
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        warped_date, _ = adjust_date_based_on_anomaly(temperature_data)
        warped_date_str = warped_date.strftime('%Y-%m-%d')
    except ValueError as e:
        warped_date_str = "N/A (Insufficient data)"
    
    clock_label = tk.Label(frame_clock, text=f"Current Date: {current_date}", font=("Helvetica", 16))
    clock_label.grid(row=0, column=0, padx=10)
    
    warped_label = tk.Label(frame_clock, text=f"Warped Date: {warped_date_str}", font=("Helvetica", 16))
    warped_label.grid(row=0, column=1, padx=10)

    # Calculate time warp data for the last 12 months
    try:
        months, warp_rates = calculate_time_warp_data(temperature_data)
    except ValueError as e:
        months, warp_rates = [], []
        print(f"Warning: {e}")

    # Create Matplotlib figure for the derivative graph
    fig, ax = plt.subplots(figsize=(6, 4))

    if months and warp_rates:
        ax.plot(months, warp_rates, marker='o')
        ax.set_title("Time Warp Rate Over Last 12 Months")
        ax.set_xlabel("Year")
        ax.set_ylabel("Days Shifted")
        plt.xticks(rotation=45)
    else:
        ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', fontsize=12)
    
    # Embed the Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    # Start Tkinter event loop
    root.mainloop()

# Main script entry point
if __name__ == "__main__":
    try:
        temperature_data = fetch_global_temperature_data()
        create_gui_window(temperature_data)
    except Exception as e:
        print(f"Error: {e}")
