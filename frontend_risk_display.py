import streamlit as st
import pandas as pd

def main():
    # Set the page title and icon
    st.set_page_config(page_title="Wildfire Risk Dashboard", page_icon="🔥")
    st.title("Wildfire Risk Dashboard")
    st.write("This dashboard displays wildfire risk data across different regions.")

    # Dummy data for the risk levels, temperature, and humidity
    data = {
        "Region": ["Ohio", "California", "Kentucky", "Idaho", "Texas"],
        "Risk Level": ["High", "Medium", "Low", "High", "Medium"],
        "Temperature (°F)": [102, 95, 88, 105, 99],
        "Humidity (%)": [20, 35, 50, 18, 30]
    }
    df = pd.DataFrame(data)

    # Displayingn the risk data in a table
    st.subheader("Risk Data Table")
    st.dataframe(df)

    # Mapping each risk level to a numerical value 
    risk_score_mapping = {"Low": 1, "Medium": 2, "High": 3}
    df["Risk Score"] = df["Risk Level"].map(risk_score_mapping)

    # Bar chart of risk scores by region
    st.subheader("Risk Score Chart")
    st.bar_chart(df.set_index("Region")["Risk Score"])

    #Geographical map of the wildfire risk
    st.subheader("Wildfire Risk Map")
    # Fake location data
    map_data = pd.DataFrame({
        "lat": [40.4173, 36.7783, 37.8393, 44.0682, 31.9686],
        "lon": [-82.9071, -119.4179, -84.27, -114.7420, -99.9018]
    })
    st.map(map_data)

if __name__ == "__main__":
    main()