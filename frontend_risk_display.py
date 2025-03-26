import streamlit as st
import pandas as pd
import json
from backend_processing import main_wf  # Import the backend processing function

def main():
    # Set the page title and icon
    st.set_page_config(page_title="Wildfire Risk Dashboard", page_icon="🔥")
    st.title("Wildfire Risk Dashboard")
    st.write("This dashboard displays wildfire risk data across different regions.")

    # Load and process data from the backend
    file_path = "MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"  # Replace with the actual data file
    df, _ = main_wf(file_path)  # Call backend to get processed data

    # Convert JSON to Pandas DataFrame
    
    

    # Display the processed risk data in a table
    st.subheader("Processed Wildfire Data")
    st.dataframe(df)

    st.subheader("Wildfire Brightness Levels")

# Ensure 'latitude' and 'brightness' exist in the DataFrame
    if 'brightness' in df.columns:
        st.bar_chart(df[['latitude', 'brightness']].set_index('latitude'))

    # Display a map with wildfire risk locations
    st.subheader("Wildfire Risk Map")
    st.map(df[['latitude', 'longitude']])

if __name__ == "__main__":
    main()
