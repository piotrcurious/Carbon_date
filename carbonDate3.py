import requests
import csv
from datetime import datetime, timedelta
from io import StringIO

# Constants
PARIS_AGREEMENT = 2016
TARGET_YEAR = 2050
TARGET_TEMP = 1.5  # The 1.5°C target anomaly

# Function to fetch global temperature anomaly data from NASA GISTEMP
def fetch_global_temperature_data():
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    
    # Add headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://data.giss.nasa.gov/gistemp/",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    
    # Fetch the CSV data from NASA GISTEMP
    response = requests.get(url, headers=headers)
    
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
        raise Exception(f"Failed to fetch data from NASA GISTEMP, status code: {response.status_code}")

# Function to get the current temperature anomaly
def get_current_anomaly(current_year):
    # Fetch temperature data
    temperature_data = fetch_global_temperature_data()

    # Look for the current year's anomaly
    for record in temperature_data:
        if record['year'] == current_year:
            return record['anomaly']

    raise ValueError(f"No temperature anomaly data available for the year {current_year}")

# Function to shift the date based on the current anomaly and the 1.5°C target
def adjust_date_based_on_anomaly(input_date=None):
    # Use current date if no input date is provided
    if input_date is None:
        input_date = datetime.now()
    
    current_year = input_date.year
    
    # Get the current temperature anomaly for this year
    current_anomaly = get_current_anomaly(current_year)
    
    # Calculate the proportion of the current anomaly relative to the 1.5°C target
    if current_anomaly >= TARGET_TEMP:
        # If the anomaly has already reached or exceeded 1.5°C, we return 2050
        adjusted_year = TARGET_YEAR
    else:
        # Proportional shift in years relative to the 1.5°C target
        proportion = current_anomaly / TARGET_TEMP
        adjusted_year = PARIS_AGREEMENT + proportion * (TARGET_YEAR - PARIS_AGREEMENT)  # 1880 is the baseline year in the dataset
    
    # Calculate the year offset
    year_offset = adjusted_year - current_year
    
    # Shift the input date by this year offset
    days_shift = year_offset * 365.25  # Approximate days in a year accounting for leap years
    adjusted_date = input_date + timedelta(days=days_shift)
    
    return adjusted_date, current_anomaly

# Example of using the script
if __name__ == "__main__":
    input_date_str = input("Enter a date (YYYY-MM-DD) or press Enter for today: ")
    
    if input_date_str:
        input_date = datetime.strptime(input_date_str, '%Y-%m-%d')
    else:
        input_date = None  # Use current date if no input provided
    
    adjusted_date, current_anomaly = adjust_date_based_on_anomaly(input_date)
    print(f"Current anomaly: {current_anomaly:.2f}°C")
    print(f"Adjusted date based on anomaly proportion: {adjusted_date.strftime('%Y-%m-%d')}")
