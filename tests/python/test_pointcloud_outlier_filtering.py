import unittest
import numpy as np

from dtcc_wrangler.pointcloud.filters import statistical_outlier_filter
from dtcc_model import PointCloud


class TestStatisticalOutlierFilter(unittest.TestCase):
    def test_no_outliers(self):
        # Test case where there are no outliers in the point cloud
        pc = PointCloud(points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]))
        filtered_pc = statistical_outlier_filter(pc)
        self.assertEqual(len(filtered_pc), 3)

    def test_remove_outliers(self):
        # Test case where outliers are removed from the point cloud
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [100, 100, 100]]),
        )
        filtered_pc = pc.statistical_outlier_filter(k=2, std_mul=1.0)
        self.assertEqual(len(filtered_pc), 3)
        self.assertTrue(
            np.all(filtered_pc.points == np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]))
        )
