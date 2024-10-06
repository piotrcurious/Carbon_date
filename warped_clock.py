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
    
    # Fetch the CSV data from NASA GISTEMP
    response = requests.get(url)
    
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        temperature_data = []
        
        # Skip the first few header lines and then read the data
        for row in reader:
            if len(row) > 1 and row[0].isdigit():
                year = int(row[0])
                try:
                    anomaly = float(row[13])
                except ValueError:
                    anomaly = None  # Handle missing data
                if anomaly is not None:
                    temperature_data.append({"year": year, "anomaly": anomaly})
        
        return temperature_data
    else:
        raise Exception("Failed to fetch data from NASA GISTEMP")

# Function to get the current temperature anomaly
def get_anomaly_for_year(year, temperature_data):
    for record in temperature_data:
        if record['year'] == year:
            return record['anomaly']
    return None

# Function to calculate the expected anomaly for a given year
def calculate_expected_anomaly(current_year, current_anomaly):
    years_to_2050 = TARGET_YEAR - current_year
    anomaly_increase = TARGET_TEMP - current_anomaly
    shift_per_year = anomaly_increase / years_to_2050  # Linear rate of anomaly increase per year
    return current_anomaly + shift_per_year

# Function to calculate date shift and derivative for the past 12 months
def calculate_time_warp_data(temperature_data):
    current_year = datetime.now().year
    months = []
    warp_rates = []
    
    for i in range(12):
        year = current_year - i // 12  # Handle previous year(s) if necessary
        anomaly = get_anomaly_for_year(year, temperature_data)
        if anomaly:
            expected_anomaly = calculate_expected_anomaly(year, anomaly)
            anomaly_difference = anomaly - expected_anomaly
            warp_rate = anomaly_difference * 365  # Days shifted based on anomaly difference
            warp_rates.append(warp_rate)
            months.append(f"{year}")
    
    return months[::-1], warp_rates[::-1]

# Function to create a Tkinter window with carbon clock and derivative graph
def create_gui_window(temperature_data):
    # Create Tkinter window
    root = tk.Tk()
    root.title("Carbon Clock with Time Warp")

    # Carbon Clock: display current date and warped date
    current_date = datetime.now().strftime("%Y-%m-%d")
    warped_date, _ = adjust_date_based_on_anomaly(temperature_data)

    clock_label = tk.Label(root, text=f"Current Date: {current_date}", font=("Helvetica", 16))
    clock_label.pack(pady=10)

    warped_label = tk.Label(root, text=f"Warped Date: {warped_date.strftime('%Y-%m-%d')}", font=("Helvetica", 16))
    warped_label.pack(pady=10)

    # Calculate the derivative of time warp for the last 12 months
    months, warp_rates = calculate_time_warp_data(temperature_data)
    
    # Create Matplotlib figure for the derivative graph
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(months, warp_rates, marker='o')
    ax.set_title("Time Warp Rate Over Last 12 Months")
    ax.set_xlabel("Month")
    ax.set_ylabel("Days Shifted")
    plt.xticks(rotation=45)

    # Embed the Matplotlib figure in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    # Start the Tkinter event loop
    root.mainloop()

# Function to adjust the date based on temperature anomaly
def adjust_date_based_on_anomaly(temperature_data):
    current_year = datetime.now().year
    current_anomaly = get_anomaly_for_year(current_year, temperature_data)
    
    # Calculate the expected anomaly if temperature were increasing linearly to 1.5°C by 2050
    expected_anomaly = calculate_expected_anomaly(current_year, current_anomaly)
    
    # Calculate the difference between current anomaly and expected anomaly
    anomaly_difference = current_anomaly - expected_anomaly

    # Calculate the days shifted based on the anomaly difference
    days_shift = anomaly_difference * 365
    adjusted_date = datetime.now() + timedelta(days=days_shift)
    
    return adjusted_date, anomaly_difference

if __name__ == "__main__":
    # Fetch the temperature data
    temperature_data = fetch_global_temperature_data()
    
    # Create the GUI window with carbon clock and derivative graph
    create_gui_window(temperature_data)
