import streamlit as st
import pandas as pd
import json
import pydeck as pdk
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
    st.set_page_config(page_title="Wildfire Risk Dashboard", page_icon="🔥")
    st.title("Wildfire Risk Dashboard")
    st.write("This dashboard displays wildfire risk data across different regions.")

    st.sidebar.header("Data Input")
    data_mode = st.sidebar.radio("Choose data source:", ["Use default file", "Upload by URL"])

    df, model, silhouette, cluster_stats = None, None, None, None

    if data_mode == "Use default file":
        file_path = "MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"
        df, model, silhouette, cluster_stats = main_wf(file_path)

    elif data_mode == "Upload by URL":
        url = st.sidebar.text_input("Enter CSV URL:")
        if st.sidebar.button("Load Data from URL"):
            df, model, silhouette, cluster_stats = auto_update_and_train(url)
            if df is None:
                st.error("Failed to load dataset from the URL.")
                return

    if df is None:
        st.warning("No data loaded.")
        return

    st.sidebar.header("Data Input")
    data_mode = st.sidebar.radio("Choose data source:", ["Use default file", "Upload by URL"])

    df, model, silhouette, cluster_stats = None, None, None, None

    if data_mode == "Use default file":
        file_path = "MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"
        df, model, silhouette, cluster_stats = main_wf(file_path)

    elif data_mode == "Upload by URL":
        url = st.sidebar.text_input("Enter CSV URL:")
        if st.sidebar.button("Load Data from URL"):
            df, model, silhouette, cluster_stats = auto_update_and_train(url)
            if df is None:
                st.error("Failed to load dataset from the URL.")
                return

    if df is None:
        st.warning("No data loaded.")
        return

    df["geometry"] = df["geometry"].apply(lambda geom: geom.wkt if geom is not None else None)

    if silhouette is not None:
        st.markdown(f"**KMeans Silhouette Score:** {silhouette:.3f}")


    if not cluster_stats.empty:
        st.subheader("Cluster Summary Statistics")
        st.dataframe(cluster_stats)
    else:
        st.write("No cluster statistics available.")

    st.markdown("---")
    st.header("Interactive Wildfire Explorer")

    st.sidebar.header("Controls")
    number = st.sidebar.slider("Number of Clusters", min_value=2, max_value=20, value=9)
    df, model, _ = run_model(df, clusters=number)
    df['cluster_mapping'] = df['cluster_mapping'].astype(str)

    st.sidebar.header("Controls")
    number = st.sidebar.slider("Number of Clusters", min_value=2, max_value=20, value=9)
    df, model, _ = run_model(df, clusters=number)
    df['cluster_mapping'] = df['cluster_mapping'].astype(str)

    cluster_brightness = df.groupby('cluster_mapping')['brightness'].mean()
    df['risk_label'] = df['cluster_mapping'].apply(lambda cid: label_cluster(cid, cluster_brightness))

    unique = sorted(df['cluster_mapping'].unique())
    unique = sorted(df['cluster_mapping'].unique())
    cluster_colors = generate_cluster_colors(unique)
    df['color'] = df['cluster_mapping'].map(cluster_colors)


    min_brightness = float(df['brightness'].min())
    max_brightness = float(df['brightness'].max())
    brightness_range = st.sidebar.slider("Brightness Range", min_brightness, max_brightness, (min_brightness, max_brightness))
    brightness_range = st.sidebar.slider("Brightness Range", min_brightness, max_brightness, (min_brightness, max_brightness))
    df = df[(df['brightness'] >= brightness_range[0]) & (df['brightness'] <= brightness_range[1])]

    map_theme = st.sidebar.selectbox("Map Theme", ["Dark", "Light"])

    st.subheader("Clustered Wildfire Map")
    map_theme = st.sidebar.selectbox("Map Theme", ["Dark", "Light"])

    st.subheader("Clustered Wildfire Map")
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9" if map_theme == "Light" else "mapbox://styles/mapbox/dark-v9",
        map_style="mapbox://styles/mapbox/light-v9" if map_theme == "Light" else "mapbox://styles/mapbox/dark-v9",
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