import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
from datetime import datetime

# Upstox API access token
access_token = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0N0JWUlMiLCJqdGkiOiI2NjhjYmU3MThjYmRlMjIwMDE1NWNmMGYiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzIwNDk5ODI1LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3MjA1NjI0MDB9.EkjAbpWVR6qqFlvVUrZUnjx8CadgSMRTCPYHi86S9V0'

# Upstox API endpoint
url = "https://api.upstox.com/v2/market-quote/quotes"

# API parameters
instrument_key = 'NSE_FO|63690'
params = {
    'instrument_key': instrument_key  # Replace 'YOUR_SYMBOL' with a valid symbol
}

# Headers for the API request
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

# Specify the correct path to the JSON key file
file_path = r'C:\Users\user\Downloads\bank-425212-8f01cc3efacc.json'  # Adjust the path accordingly
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(file_path, scope)
client = gspread.authorize(creds)
sheet = client.open("Bank").worksheet("ICICI JULY FUT")

# Function to fetch and save data
def fetch_and_save_data():
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 401:
        print("Unauthorized access. Please check your access token.")
    else:
        # Parse the response JSON
        data = response.json()
        
        # Extract total_sell_quantity and total_buy_quantity
        total_sell_quantity = data['data']['NSE_FO:ICICIBANK24JULFUT']['total_sell_quantity']
        total_buy_quantity = data['data']['NSE_FO:ICICIBANK24JULFUT']['total_buy_quantity']

        # Calculate buy % and sell %
        total_quantity = total_sell_quantity + total_buy_quantity
        if total_quantity > 0:
            buy_percentage = (total_buy_quantity / total_quantity) * 100
            sell_percentage = (total_sell_quantity / total_quantity) * 100
        else:
            buy_percentage = 0
            sell_percentage = 0

        # Create a DataFrame with the extracted data
        df = pd.DataFrame([{
            'total_sell_quantity': total_sell_quantity,
            'total_buy_quantity': total_buy_quantity,
            'buy_percentage': buy_percentage,
            'sell_percentage': sell_percentage
        }])

        # Insert the instrument key at the left
        df.insert(0, 'instrument_key', instrument_key)
        
        # Print the DataFrame to inspect its structure
        print("Type of data:", type(df))
        print("Content of data:", df)

        # Convert DataFrame to a list of lists
        data_list = df.values.tolist()

        # Optionally, include headers if the worksheet is empty
        header_list = df.columns.tolist()

        # Check if the sheet is empty and write headers if it is
        if sheet.row_count == 1 and not sheet.cell(1, 1).value:
            sheet.insert_row(header_list, index=1)

        # Append data to the Google Spreadsheet
        for row in data_list:
            sheet.append_row(row, value_input_option="RAW")

        print("Data successfully appended to the Google Spreadsheet.")

# Function to check if the market is still open
def is_market_open():
    now = datetime.now()
    market_end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return now < market_end_time

# Fetch and save data continuously until the market end time
while is_market_open():
    fetch_and_save_data()
    time.sleep(30)  # Wait for 30 seconds before fetching the data again