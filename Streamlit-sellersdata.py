import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Function to fetch data from Google Sheets
def fetch_data_from_google_sheet(sheet_url, sheet_name):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Specify the correct path to the JSON key file
    file_path = r'C:\Users\user\Downloads\bank-425212-8f01cc3efacc.json'  # Adjust the path accordingly
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Add your credentials here
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_path, scope)

    # Authorize the client
    client = gspread.authorize(creds)

    # Get the instance of the Spreadsheet
    sheet = client.open_by_url(sheet_url)

    # Get the specified sheet of the Spreadsheet
    worksheet = sheet.worksheet(sheet_name)

    # Get all values in the sheet
    data = worksheet.get_all_records()

    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    
    return df

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
    </style>
    """, unsafe_allow_html=True
)

st.title("Prashanth Stock Dashboard")

# Update the sidebar menu to include options for four sheets
menu = ["Select Option", "FII DATA 01/07/2024", "FII DATA 02/07/2024", "FII DATA 03/07/2024", "FII DATA 04/07/2024", "FII DATA 05/07/2024"]
choice = st.sidebar.selectbox("Menu", menu)

# Google Sheet URL
google_sheet_url = "https://docs.google.com/spreadsheets/d/1-7G6PmYXYJEouA10PKtxporBjtYSAubzIl_q1GkIkE0/edit#gid=1849083928"

# Dictionary to map choices to sheet names
sheet_name_mapping = {
    "FII DATA 01/07/2024": "FII DATA 01072024",
    "FII DATA 02/07/2024": "FII DATA 02072024",
    "FII DATA 03/07/2024": "FII DATA 03072024",
    "FII DATA 04/07/2024": "FII DATA 04072024",
    "FII DATA 05/07/2024": "FII DATA 05072024"
}

if choice != "Select Option":
    st.subheader(choice)

    # Specify the sheet name based on the selection
    sheet_name = sheet_name_mapping[choice]
    
    # Fetch data from Google Sheet
    data = fetch_data_from_google_sheet(google_sheet_url, sheet_name)
    
    st.dataframe(data)
