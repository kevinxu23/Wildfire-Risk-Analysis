import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from backend_processing import main_wf  # Import the backend processing function
from backend_processing import run_model
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px  # Added for histogram visualization

#Function to make new cluster colors to differentiate
def generate_cluster_colors(cluster_ids):
    num_clusters = len(cluster_ids)
    color_map = plt.get_cmap('tab20', num_clusters)
    cluster_colors = {
        str(cluster): [int(c * 255) for c in color_map(i)[:3]] + [160]
        for i, cluster in enumerate(cluster_ids)
    }
    return cluster_colors

def label_cluster(cluster_id, cluster_brightness):
    avg_brightness = cluster_brightness.get(cluster_id, 0)
    if avg_brightness >= 400:
        return "High Risk"
    elif avg_brightness >= 200:
        return "Medium Risk"
    else:
        return "Low Risk"

# New function to create a brightness histogram by cluster
def create_brightness_histogram(dataframe):
    fig = px.histogram(
        dataframe, 
        x="brightness", 
        color="risk_label",
        nbins=30,
        opacity=0.7,
        barmode="overlay",
        title="Distribution of Brightness Values by Risk Level",
        labels={"brightness": "Brightness", "count": "Number of Observations"}
    )
    fig.update_layout(legend_title="Risk Level")
    return fig

def main():
    # Set the page title and icon
    st.set_page_config(page_title="Wildfire Risk Dashboard", page_icon="🔥")
    st.title("Wildfire Risk Dashboard")
    st.write("This dashboard displays wildfire risk data across different regions.")

    # Load and process data from the backend
    file_path = "MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"  # Replace with the actual data file
    df, _, silhouette, cluster_stats = main_wf(file_path) # Call backend to get processed data
    df["geometry"] = df["geometry"].apply(lambda geom: geom.wkt if geom is not None else None)

    # Display silhouette score if available
    if silhouette is not None:
        st.markdown(f"**KMeans Silhouette Score:** {silhouette:.3f}")
    
    # new - Display cluster summary statistics if available
    if not cluster_stats.empty:
        st.subheader("Cluster Summary Statistics")
        st.dataframe(cluster_stats)
    else:
        st.write("No cluster statistics available.")

    # 🆕 Display the wildfire summary scatter plot
    st.markdown("---")
    st.subheader("Wildfire Brightness vs FRP Scatter Plot")

    try:
        st.image("wildfire_summary_plot.png", caption="Wildfire Brightness vs Fire Radiative Power (FRP)", use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load wildfire summary plot: {e}")

    #New interactive UI stuff by Taran Sooranahalli
    st.markdown("---")
    st.header("Interactive Wildfire Explorer")

    st.sidebar.header("Controls") #Might add more modularity in the future
    number = st.sidebar.slider("Number of Clusters", min_value=2, max_value=20, value=9) #New slider bar to adjust number of clusters
    df, model, _ = run_model(df, clusters=number) #Run the model with the updated cluster number
    df['cluster_mapping'] = df['cluster_mapping'].astype(str) #Save the mapping to the df
    cluster_brightness = df.groupby('cluster_mapping')['brightness'].mean()


    df['risk_label'] = df['cluster_mapping'].apply(lambda cid: label_cluster(cid, cluster_brightness))

    unique = sorted(df['cluster_mapping'].unique()) #Generating colors
    cluster_colors = generate_cluster_colors(unique)
    df['color'] = df['cluster_mapping'].map(cluster_colors)

    
    min_brightness = float(df['brightness'].min())
    max_brightness = float(df['brightness'].max())
    brightness_range = st.sidebar.slider("Brightness Range", min_brightness, max_brightness, (min_brightness, max_brightness)) #Used ChatGPT to debug this feature
    df = df[(df['brightness'] >= brightness_range[0]) & (df['brightness'] <= brightness_range[1])]

    map_theme = st.sidebar.selectbox("Map Theme", ["Dark", "Light"]) #Toggle for making the map light or dark mode
    


    st.subheader("Clustered Wildfire Map") #Displaying map, allows you to hover on points too
    st.pydeck_chart(pdk.Deck(
        map_style = "mapbox://styles/mapbox/light-v9" if map_theme == "Light" else "mapbox://styles/mapbox/dark-v9",
        initial_view_state=pdk.ViewState(
            latitude=df['latitude'].mean(),
            longitude=df['longitude'].mean(),
            zoom=3,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[longitude, latitude]",
                get_color="color",
                get_radius=20000,
                pickable=True,
            )
        ],
        tooltip={"text": "Lat: {latitude}\nLon: {longitude}\nBrightness: {brightness}\nCluster: {cluster_mapping}\nRisk: {risk_label}"}
    ))
    
    
    st.markdown("---")
    # Display the processed risk data in a table
    st.subheader("Processed Wildfire Data")
    st.dataframe(df)
    
    st.markdown("---")
    st.subheader("Wildfire Brightness Levels")

    # Ensure 'latitude' and 'brightness' exist in the DataFrame
    if 'brightness' in df.columns:
        st.bar_chart(df[['latitude', 'brightness']].set_index('latitude'))
    
    # New feature: Display brightness distribution histogram
    st.markdown("---")
    st.subheader("Brightness Distribution by Risk Level")
    histogram = create_brightness_histogram(df)
    st.plotly_chart(histogram, use_container_width=True)


if __name__ == "__main__":
    main()