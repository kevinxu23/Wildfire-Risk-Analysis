import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import geopandas as gpd
import requests
from io import StringIO

"""
backend_processing.py

Description:
    This script processes wildfire data from CSV files, 
    sorts it geographically, runs a KMeans model on it,
    and then outputs a GeoJSON file that can be used 
    later with the visualization options of the frontend.
"""


def load_data(path): #Loads data from a csv into a dataframe for processing
    wildfire_df = pd.read_csv(path)
    return wildfire_df

def preprocess(dataframe): #Sorts the data geographically
    dataframe = dataframe.dropna(subset=['latitude', 'longitude'])
    dataframe = dataframe.sort_values(by=['latitude', 'longitude'])

    # new - intensity_score if both brightness and frp columns exist
    if 'brightness' in dataframe.columns and 'frp' in dataframe.columns:
        dataframe['intensity_score'] = (dataframe['brightness'] * 0.6 + dataframe['frp'] * 0.4).round(2)

    return dataframe

# new -   Creates a scatter plot of Brightness vs FRP (Fire Radiative Power) colored by Risk Level.
def plot_wildfire_summary(dataframe, output_path="wildfire_summary_plot.png"):
    if 'brightness' not in dataframe.columns or 'frp' not in dataframe.columns:
        print("Error: Missing required columns 'brightness' and 'frp'. Cannot plot.")
        return
    
    if 'risk_label' not in dataframe.columns:
        # If risk_label isn't there, create it quickly
        dataframe['risk_label'] = dataframe['brightness'].apply(assign_risk_label)
    
    plt.figure(figsize=(10, 6))
    for label in dataframe['risk_label'].unique():
        subset = dataframe[dataframe['risk_label'] == label]
        plt.scatter(subset['brightness'], subset['frp'], label=label, alpha=0.6)
    
    plt.xlabel('Brightness')
    plt.ylabel('Fire Radiative Power (FRP)')
    plt.title('Wildfire Brightness vs FRP by Risk Level')
    plt.legend(title="Risk Level")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Wildfire summary plot saved to {output_path}")

# new function - cluster summary statistics - compuytes avg values for each cluster
def get_cluster_summary(dataframe):
    if 'intensity_score' not in dataframe.columns:
        dataframe['intensity_score'] = (dataframe['brightness'] * 0.6 + dataframe['frp'] * 0.4).round(2)

    # groupby
    summary = dataframe.groupby("cluster_mapping").agg({
        "brightness": "mean",
        "frp": "mean",
        "intensity_score": "mean"
    }).reset_index()

    summary = summary.rename(columns={
        'brightness': 'avg_brightness',
        'frp': 'avg_frp',
        'intensity_score': 'avg_risk'
    })
    
    summary = summary.round(2)
    return summary


def convert_geodata(dataframe): #Convert this to a usable dataframe format for displaying
    geo_df = gpd.GeoDataFrame(dataframe, geometry=gpd.points_from_xy(dataframe.longitude, dataframe.latitude), crs='EPSG:4326')
    return geo_df

# added a risk label helper function
def assign_risk_label(brightness):
    if brightness >= 400:
        return "High Risk"
    elif brightness >= 200:
        return "Medium Risk"
    else:
        return "Low Risk"
    
# new - created a cluster color mapping function
def generate_cluster_colors(cluster_ids):
    import matplotlib.pyplot as plt
    num_clusters = len(cluster_ids)
    color_map = plt.get_cmap('tab20', num_clusters)
    cluster_colors = {
        str(cluster): [int(c * 255) for c in color_map(i)[:3]] + [160]
        for i, cluster in enumerate(cluster_ids)
    }
    return cluster_colors

def run_model(dataframe, clusters=10, scale_features=True): #Machine learning model that will cluster the wildfire data and should provide some insight on similarities
    coordinates = dataframe[['latitude', 'longitude']].values
    if scale_features:
        scaler = StandardScaler()
        coordinates_scaled = scaler.fit_transform(coordinates)
    else:
        coordinates_scaled = coordinates
    new_model = KMeans(n_clusters=clusters, random_state=9)
    dataframe['cluster_mapping'] = new_model.fit_predict(coordinates_scaled)

    #compute sillohuette score to determine the best number of clusters
    score = silhouette_score(coordinates_scaled, dataframe['cluster_mapping'])
    print("KMeans Silhouette Score:", score)

     # new - risk labels 
    dataframe['risk_label'] = dataframe['brightness'].apply(assign_risk_label)

    # new - cluster color mapping
    unique_clusters = sorted(dataframe['cluster_mapping'].unique())
    cluster_colors = generate_cluster_colors(unique_clusters)
    dataframe['color'] = dataframe['cluster_mapping'].astype(str).map(cluster_colors)
    
    return dataframe, new_model, score

def auto_update_and_train(url, clusters=10, scale_features=True, output_geojson="processed_wildfire_usable.json"):
    """
    Automatically pulls a new dataset from the given URL, processes the data,
    trains the KMeans model, and outputs a GeoJSON file along with the model's outputs
    url (str): URL pointing to the CSV dataset.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data_string = response.content.decode('utf-8')
        wildfire_df = pd.read_csv(StringIO(data_string))
        print("New dataset downloaded and loaded successfully.")
    except Exception as e:
        print("Failed to download new dataset:", e)
        return None, None, None, None

    wildfire_df = preprocess(wildfire_df)
    cluster_df, wildfire_model, score = run_model(wildfire_df, clusters=clusters, scale_features=scale_features)
    geo_wildfire_df = convert_geodata(cluster_df)
    geo_wildfire_df["latitude"] = geo_wildfire_df.geometry.y
    geo_wildfire_df["longitude"] = geo_wildfire_df.geometry.x

    cluster_stats = get_cluster_summary(cluster_df)

    geo_wildfire_df.to_file(output_geojson, driver='GeoJSON')
    print("Output GeoJSON saved to", output_geojson)
    
    return geo_wildfire_df, wildfire_model, score, cluster_stats

def load_water_resources(filepath, max_sites=2000):
    df = pd.read_csv(filepath)
    df = df[['name', 'latitude', 'longitude']].dropna()
    df = df.head(max_sites)
    return df


def main_wf(path): 
    wildfire_df = load_data(path)
    geo_wildfire = preprocess(wildfire_df)
    cluster_df, wildfire_model, score = run_model(geo_wildfire)
    geo_wildfire_df = convert_geodata(cluster_df)
    geo_wildfire_df["latitude"] = geo_wildfire_df.geometry.y
    geo_wildfire_df["longitude"] = geo_wildfire_df.geometry.x

    # new - obtain cluster summary stats
    cluster_stats = get_cluster_summary(cluster_df)

    plot_wildfire_summary(cluster_df)

    # Convert the dataframe to JSON and return
    return geo_wildfire_df, wildfire_model, score, cluster_stats


if __name__ == "__main__": #Run the whole pipeline
    file = '' #input wildfire data source here
    wildfire_geo_df, wildfire_model = main_wf(file)
    wildfire_geo_df.to_file('processed_wildfire_usable.json', driver='GeoJSON')