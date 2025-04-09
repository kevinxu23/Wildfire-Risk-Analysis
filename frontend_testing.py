import unittest
import matplotlib.pyplot as plt
from frontend_risk_display import generate_cluster_colors
from frontend_risk_display import label_cluster

class TestFrontendRiskDisplay(unittest.TestCase):

    def test_generate_cluster_colors_basic(self):
        cluster_ids = ['0', '1', '2']
        result = generate_cluster_colors(cluster_ids)

        self.assertEqual(set(result.keys()), set(cluster_ids)) #Verify that the clusters match up

        # Check the actual colors themselves
        for color in result.values():
            self.assertEqual(len(color), 4)  # R, G, B, A
            self.assertTrue(all(isinstance(c, int) for c in color))
            self.assertTrue(all(0 <= c <= 255 for c in color))\

    def test_generate_cluster_colors_empty(self):
        cluster_ids = []
        result = generate_cluster_colors(cluster_ids)
        self.assertEqual(result, {}) 

    def test_generate_cluster_colors_single_cluster(self):
        cluster_ids = ['A']
        result = generate_cluster_colors(cluster_ids)
        self.assertIn('A', result)
        self.assertEqual(len(result['A']), 4)
        self.assertTrue(all(0 <= c <= 255 for c in result['A']))

    def test_generate_cluster_colors_non_numeric_ids(self):
        cluster_ids = ['A', 'B', 'C']
        result = generate_cluster_colors(cluster_ids)
        self.assertEqual(set(result.keys()), set(cluster_ids))
        for color in result.values():
            self.assertEqual(len(color), 4)

class TestLabelCluster(unittest.TestCase):
    def test_high_risk(self):
        brightness_map = {'A': 401}
        self.assertEqual(label_cluster('A', brightness_map), "High Risk")

    def test_medium_risk_upper_bound(self):
        brightness_map = {'B': 399}
        self.assertEqual(label_cluster('B', brightness_map), "Medium Risk")

    def test_medium_risk_lower_bound(self):
        brightness_map = {'C': 201}
        self.assertEqual(label_cluster('C', brightness_map), "Medium Risk")

    def test_low_risk_upper_bound(self):
        brightness_map = {'D': 199}
        self.assertEqual(label_cluster('D', brightness_map), "Low Risk")


if __name__ == '__main__':
    unittest.main()