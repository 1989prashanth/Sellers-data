import streamlit as st
import pandas as pd

def calculate_percentage(df, buy_column, sell_column):
    # Calculate total buy and sell quantities
    total_buy = df[buy_column].sum()
    total_sell = df[sell_column].sum()
    
    # Calculate percentages
    buy_percentage = (total_buy / (total_buy + total_sell)) * 100
    sell_percentage = (total_sell / (total_buy + total_sell)) * 100
    
    return buy_percentage, sell_percentage

st.title("Buy and Sell Quantity Percentage Calculator")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    st.write("Data preview:")
    st.dataframe(df)
    
    buy_column = st.selectbox("Select Buy Quantity Column", df.columns)
    sell_column = st.selectbox("Select Sell Quantity Column", df.columns)
    
    if st.button("Calculate Percentages"):
        buy_percent, sell_percent = calculate_percentage(df, buy_column, sell_column)
        
        st.write(f"Buy Quantity Percentage: {buy_percent:.2f}%")
        st.write(f"Sell Quantity Percentage: {sell_percent:.2f}%")

# Example usage (for local testing):
# excel_file = r'C:\python\google finance\market_quote.xlsx'  # Replace with your file path
# buy_percent, sell_percent = calculate_percentage(pd.read_excel(excel_file), 'Buy Quantity', 'Sell Quantity')
# print(f"Buy Quantity Percentage: {buy_percent:.2f}%")
# print(f"Sell Quantity Percentage: {sell_percent:.2f}%")