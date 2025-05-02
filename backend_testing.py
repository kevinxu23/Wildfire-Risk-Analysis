import unittest
import pandas as pd
from backend_processing import preprocess, run_model, get_cluster_summary, assign_risk_label

class TestBackendProcessing(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'latitude': [34, 36, 35],
            'longitude': [-119, -121, -120],
            'brightness': [300, 450, 150],
            'frp': [10, 15, 12.5]
        })

    def test_run_model_and_assigns(self):
        df = preprocess(self.data.copy())
        clustered_df, model, score = run_model(df, clusters=2)
        self.assertIn('cluster_mapping', clustered_df.columns)
        self.assertIn('risk_label', clustered_df.columns)
        self.assertIn('color', clustered_df.columns)
        self.assertEqual(len(clustered_df['cluster_mapping'].unique()), 2)

    def test_cluster_summary_fields(self):
        df = preprocess(self.data.copy())
        clustered_df, model, score = run_model(df, clusters=2)
        summary = get_cluster_summary(clustered_df)
        self.assertIn('avg_brightness', summary.columns)
        self.assertIn('avg_frp', summary.columns)
        self.assertIn('avg_risk', summary.columns)
        self.assertEqual(len(summary), 2)

    def test_assign_risk_label(self):
        self.assertEqual(assign_risk_label(450), "High Risk")
        self.assertEqual(assign_risk_label(250), "Medium Risk")
        self.assertEqual(assign_risk_label(100), "Low Risk")


if __name__ == '__main__':
    unittest.main()