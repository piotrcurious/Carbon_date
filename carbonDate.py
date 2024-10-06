import requests
import csv
from datetime import datetime, timedelta
from io import StringIO

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
                # We are interested in the year and annual anomaly (column index 0 and 13)
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
def get_current_anomaly(current_year):
    # Fetch temperature data
    temperature_data = fetch_global_temperature_data()

    # Look for the current year's anomaly
    for record in temperature_data:
        if record['year'] == current_year:
            return record['anomaly']

    raise ValueError(f"No temperature anomaly data available for the year {current_year}")

# Function to calculate the expected anomaly for a given year, assuming linear rise to 1.5°C in 2050
def calculate_expected_anomaly(current_year, current_anomaly):
    current_year = current_year  # e.g., 2024
    years_to_2050 = TARGET_YEAR - current_year
    anomaly_increase = TARGET_TEMP - current_anomaly
    shift_per_year = anomaly_increase / years_to_2050  # Linear rate of anomaly increase per year

    return current_anomaly + shift_per_year

# Function to adjust the date based on the current anomaly vs expected anomaly
def adjust_date_based_on_anomaly(input_date=None):
    # Use current date if no input date is provided
    if input_date is None:
        input_date = datetime.now()
    
    current_year = input_date.year
    
    # Get the current temperature anomaly for this year
    current_anomaly = get_current_anomaly(current_year)
    
    # Calculate the expected anomaly if temperature were increasing linearly to 1.5°C by 2050
    expected_anomaly = calculate_expected_anomaly(current_year, current_anomaly)
    
    # Calculate the difference between current anomaly and expected anomaly
    anomaly_difference = current_anomaly - expected_anomaly

    # If the current anomaly is higher than expected, move the date forward (we're ahead of schedule in warming)
    # If the current anomaly is lower than expected, move the date backward (we're behind schedule)
    # Assume 1°C difference = 365 days, so we scale the days based on the anomaly difference
    days_shift = anomaly_difference * 365

    adjusted_date = input_date + timedelta(days=days_shift)
    
    return adjusted_date, anomaly_difference

# Example of using the script
if __name__ == "__main__":
    input_date_str = input("Enter a date (YYYY-MM-DD) or press Enter for today: ")
    
    if input_date_str:
        input_date = datetime.strptime(input_date_str, '%Y-%m-%d')
    else:
        input_date = None  # Use current date if no input provided
    
    adjusted_date, anomaly_difference = adjust_date_based_on_anomaly(input_date)
    print(f"Anomaly difference: {anomaly_difference:.2f}°C")
    print(f"Adjusted date based on anomaly difference: {adjusted_date.strftime('%Y-%m-%d')}")
