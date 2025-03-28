import unittest
import matplotlib.pyplot as plt
from frontend_risk_display import generate_cluster_colors

class TestFrontendRiskDisplay(unittest.TestCase):

    def test_generate_cluster_colors_basic(self):
        cluster_ids = ['0', '1', '2']
        result = generate_cluster_colors(cluster_ids)

        self.assertEqual(set(result.keys()), set(cluster_ids)) #Verify that the clusters match up

        # Check the actual colors themselves
        for color in result.values():
            self.assertEqual(len(color), 4)  # R, G, B, A
            self.assertTrue(all(isinstance(c, int) for c in color))
            self.assertTrue(all(0 <= c <= 255 for c in color))


if __name__ == '__main__':
    unittest.main()