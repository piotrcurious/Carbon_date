import requests
import csv
from datetime import datetime, timedelta
from io import StringIO
import numpy as np

# Constants
TARGET_YEAR = 2100  # Paris Agreement target year
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
                # We are interested in the year and monthly anomalies (index 0 and 1-12 for months)
                year = int(row[0])
                monthly_anomalies = []
                for i in range(1, 13):
                    try:
                        monthly_anomalies.append(float(row[i]))
                    except ValueError:
                        monthly_anomalies.append(None)  # Handle missing data
                temperature_data.append({"year": year, "monthly_anomalies": monthly_anomalies})
        
        return temperature_data
    else:
        raise Exception(f"Failed to fetch data from NASA GISTEMP, status code: {response.status_code}")

# Function to get the current year's monthly anomalies
def get_monthly_anomalies(current_year):
    # Fetch temperature data
    temperature_data = fetch_global_temperature_data()

    # Look for the current year's anomalies
    for record in temperature_data:
        if record['year'] == current_year:
            return record['monthly_anomalies']

    raise ValueError(f"No temperature anomaly data available for the year {current_year}")

# Function to calculate monthly derivatives
def calculate_monthly_derivatives(anomalies):
    derivatives = []
    for i in range(1, len(anomalies)):
        if anomalies[i] is not None and anomalies[i - 1] is not None:
            derivative = anomalies[i] - anomalies[i - 1]
        else:
            derivative = None  # Missing data, can't calculate derivative
        derivatives.append(derivative)
    return derivatives

# Function to predict missing data using derivatives
def predict_missing_data(anomalies, derivatives):
    predicted_anomalies = anomalies.copy()
    for i in range(1, len(predicted_anomalies)):
        if predicted_anomalies[i] is None and derivatives[i - 1] is not None:
            # Use the previous month's anomaly + derivative to predict current anomaly
            predicted_anomalies[i] = predicted_anomalies[i - 1] + derivatives[i - 1]
    return predicted_anomalies

# Function to shift the date based on the monthly anomalies and target anomaly
def adjust_date_based_on_anomaly(input_date=None):
    # Use current date if no input date is provided
    if input_date is None:
        input_date = datetime.now()
    
    current_year = input_date.year
    current_month = input_date.month - 1  # Convert to 0-based index for the anomaly array
    
    # Get the monthly anomalies for the current year
    monthly_anomalies = get_monthly_anomalies(current_year)
    
    # Calculate the derivatives of the monthly anomalies
    derivatives = calculate_monthly_derivatives(monthly_anomalies)
    
    # Predict missing data based on derivatives
    predicted_anomalies = predict_missing_data(monthly_anomalies, derivatives)
    
    # Get the anomaly for the current month (use predicted if actual is missing)
    current_anomaly = predicted_anomalies[current_month]
    
    # Calculate the proportion of the current anomaly relative to the 1.5°C target
    if current_anomaly >= TARGET_TEMP:
        # If the anomaly has already reached or exceeded 1.5°C, return 2100
        adjusted_year = TARGET_YEAR
    else:
        # Proportional shift in years relative to the 1.5°C target
        proportion = current_anomaly / TARGET_TEMP
        adjusted_year = 1880 + proportion * (TARGET_YEAR - 1880)  # 1880 is the baseline year in the dataset
    
    # Calculate the year offset
    year_offset = adjusted_year - current_year
    
    # Shift the input date by this year offset
    days_shift = year_offset * 365.25  # Approximate days in a year accounting for leap years
    adjusted_date = input_date + timedelta(days=days_shift)
    
    return adjusted_date, current_anomaly, derivatives

# Example of using the script
if __name__ == "__main__":
    input_date_str = input("Enter a date (YYYY-MM-DD) or press Enter for today: ")
    
    if input_date_str:
        input_date = datetime.strptime(input_date_str, '%Y-%m-%d')
    else:
        input_date = None  # Use current date if no input provided
    
    adjusted_date, current_anomaly, derivatives = adjust_date_based_on_anomaly(input_date)
    print(f"Current anomaly: {current_anomaly:.2f}°C")
    print(f"Adjusted date based on anomaly proportion: {adjusted_date.strftime('%Y-%m-%d')}")
    print(f"Monthly derivatives: {derivatives}")
