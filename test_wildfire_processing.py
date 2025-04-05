import unittest
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

from backend_processing import preprocess, run_model

class TestWildfireProcessing(unittest.TestCase):
    
    def test_preprocess(self):
        #Testing preprocess function in backend, which drops rows w/missing latitude or longitude and tests whether the data is sored
        data = {
            'latitude': [34.5, np.nan, 32.1, 33.0],
            'longitude': [-117.5, -118.0, -115.5, np.nan],
            'other_data': [1, 2, 3, 4]
        }
        df = pd.DataFrame(data)
        
        # Dataframe processing
        processed_df = preprocess(df)
        
        # Verify that latitude/longitude has no missing values
        self.assertTrue(processed_df['latitude'].notna().all(), "Latitude column still contains NaN values.")
        self.assertTrue(processed_df['longitude'].notna().all(), "Longitude column still contains NaN values.")
        
        # Verify the dataframe is sorted by ascending order in longitude/latitude
        sorted_df = processed_df.sort_values(by=['latitude', 'longitude']).reset_index(drop=True)
        pd.testing.assert_frame_equal(processed_df.reset_index(drop=True), sorted_df,
                                      "Dataframe is not sorted correctly by latitude and longitude.")
    
    def test_run_model(self):
        """Test that run_model adds a cluster mapping column, returns a valid KMeans model, and computes a silhouette score."""
        # Create a small dataframe with valid latitude and longitude values
        data = {
            'latitude': [34.0, 35.0, 36.0, 37.0],
            'longitude': [-120.0, -121.0, -122.0, -123.0]
        }
        df = pd.DataFrame(data)
        
        # Run the KMeans model with 2 clusters and without scaling features for simplicity
        result_df, model, score = run_model(df, clusters=2, scale_features=False)
        
        # Verify that a new column 'cluster_mapping' has been added to the dataframe
        self.assertIn('cluster_mapping', result_df.columns,
                      "The 'cluster_mapping' column was not added to the dataframe.")
        
        # Check that the returned model is indeed a KMeans instance
        self.assertIsInstance(model, KMeans, "The returned model is not an instance of KMeans.")
        
        # Check that the silhouette score is a float
        self.assertIsInstance(score, float, "Silhouette score is not a float.")
        
        # Optionally, ensure the cluster values are either 0 or 1 since we are using 2 clusters
        unique_clusters = set(result_df['cluster_mapping'].unique())
        self.assertTrue(unique_clusters.issubset({0, 1}),
                        "Cluster mapping contains values outside of the expected range (0, 1).")

if __name__ == '__main__':
    unittest.main()