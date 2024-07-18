import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import time
import base64
import json

# Function to fetch data from Google Sheets
def fetch_data_from_google_sheet(sheet_url):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Fetch the base64 encoded credentials from the environment variable
    encoded_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not encoded_credentials:
        raise FileNotFoundError("Google application credentials not found in environment variable")

    # Decode the base64 string
    credentials_json = base64.b64decode(encoded_credentials).decode('utf-8')
    credentials_dict = json.loads(credentials_json)

    # Save the credentials to a temporary file
    with open("temp_credentials.json", "w") as temp_file:
        json.dump(credentials_dict, temp_file)

    # Add your credentials here
    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_credentials.json", scope)

    # Authorize the client
    client = gspread.authorize(creds)

    # Get the instance of the Spreadsheet
    sheet = client.open_by_url(sheet_url)

    # Fetch data from all worksheets and store in a dictionary
    worksheets_data = {}
    for worksheet in sheet.worksheets():
        worksheet_name = worksheet.title
        data = worksheet.get_all_values()  # Fetch all values without considering header
        df = pd.DataFrame(data[1:], columns=['timestamp', 'total_buy_quantity', 'total_sell_quantity', 'other_col1', 'other_col2'])
        worksheets_data[worksheet_name] = df

    # Remove the temporary credentials file
    os.remove("temp_credentials.json")
    
    return worksheets_data

# Streamlit App
st.set_page_config(page_title="Prashanth Stock Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
        animation: fadeIn 2s;
    }
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    .shining {
        animation: shining 1.5s infinite;
    }
    @keyframes shining {
        0% { background-color: #ffffff; }
        50% { background-color: #00ff00; }
        100% { background-color: #ffffff; }
    }
    .red-shining {
        animation: red-shining 1.5s infinite;
    }
    @keyframes red-shining {
        0% { background-color: #ffffff; }
        50% { background-color: #ff0000; }
        100% { background-color: #ffffff; }
    }
    .data-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin: 10px 0;
    }
    .data-column {
        margin: 0 10px;
        text-align: center;
        font-size: 14px;
    }
    .data-column h3 {
        margin: 5px 0;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("Prashanth Stock Dashboard")

# Google Sheet URL
google_sheet_url = "https://docs.google.com/spreadsheets/d/1-7G6PmYXYJEouA10PKtxporBjtYSAubzIl_q1GkIkE0/edit#gid=1849083928"

while True:
    # Fetch data from Google Sheet
    worksheets_data = fetch_data_from_google_sheet(google_sheet_url)

    # Display data from all worksheets
    for worksheet_name, data in worksheets_data.items():
        st.subheader(worksheet_name)
        
        if not data.empty:
            # Ensure columns are numeric for calculation
            data[['total_buy_quantity', 'total_sell_quantity']] = data[['total_buy_quantity', 'total_sell_quantity']].apply(pd.to_numeric, errors='coerce')
            
            # Show only the latest row
            latest_data = data.tail(1)

            # Calculate buy_percentage and sell_percentage if they don't exist
            if 'total_buy_quantity' in latest_data.columns and 'total_sell_quantity' in latest_data.columns:
                total_quantity = latest_data['total_buy_quantity'] + latest_data['total_sell_quantity']
                latest_data['buy_percentage'] = (latest_data['total_buy_quantity'] / total_quantity) * 100
                latest_data['sell_percentage'] = (latest_data['total_sell_quantity'] / total_quantity) * 100

            # Display data
            total_buy_quantity = latest_data.iloc[0]['total_buy_quantity']
            total_sell_quantity = latest_data.iloc[0]['total_sell_quantity']
            buy_percentage = latest_data.iloc[0]['buy_percentage']
            sell_percentage = latest_data.iloc[0]['sell_percentage']

            st.markdown(f"""
                <div class="data-container">
                    <div class="data-column">
                        <h3>Total Buy Quantity</h3>
                        <p>{total_buy_quantity}</p>
                    </div>
                    <div class="data-column">
                        <h3>Total Sell Quantity</h3>
                        <p>{total_sell_quantity}</p>
                    </div>
                    <div class="data-column">
                        <h3>Buy Percentage</h3>
                        <p class="shining">{buy_percentage:.2f}%</p>
                    </div>
                    <div class="data-column">
                        <h3>Sell Percentage</h3>
                        <p class="red-shining">{sell_percentage:.2f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No data available in this worksheet.")

    # Wait for 1 second before refreshing
    time.sleep(1)
    st.experimental_rerun()  # Rerun the script to refresh data
