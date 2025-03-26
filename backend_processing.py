import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import geopandas as gpd

"""
backend_processing.py

Description:
    This script processes wildfire data from CSV files, 
    sorts it geographically, runs a KMeans model on it,
    and then outputs a GeoJSON file that can be used 
    later with the visualization options that Varun
    has provided.
    

Author:
    Taran Sooranahalli
"""


def load_data(path): #Loads data from a csv into a dataframe for processing
    wildfire_df = pd.read_csv(path)
    return wildfire_df

def preprocess(dataframe): #Sorts the data geographically
    dataframe = dataframe.dropna(subset=['latitude', 'longitude'])
    dataframe = dataframe.sort(by=['latitude', 'longitude'])
    return dataframe

def convert_geodata(dataframe): #Convert this to a usable dataframe format for displaying
    geo_df = gpd.GeoDataFrame(dataframe, geometry=gpd.points_from_xy(dataframe.longitude, dataframe.latitude), crs='EPSG:4326')
    return geo_df

def run_model(dataframe, clusters=10): #Machine learning model that will cluster the wildfire data and should provide some insight on similarities
    coordinates = dataframe[['latitude', 'longitude']].values
    new_model = KMeans(n_clusters=clusters, random_state=9)
    dataframe['cluster_mapping'] = new_model.fit_predict(coordinates)
    return dataframe, new_model

def main_wf(path): #Runs the workflow of processing the data in order
    wildfire_df = load_data(path)
    geo_wildfire = preprocess(wildfire_df)
    cluster_df, wildfire_model = run_model(geo_wildfire)
    geo_wildfire_df = convert_geodata(cluster_df)
    return geo_wildfire_df, wildfire_model

if __name__ == "__main__": #Run the whole pipeline
    file = '' #input wildfire data source here
    wildfire_geo_df, wildfire_model = main_wf(file)
    wildfire_geo_df.to_file('processed_wildfire_usable.json', driver='GeoJSON')