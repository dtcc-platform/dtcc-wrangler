import unittest
import numpy as np
from dtcc_wrangler.pointcloud.filters import _find_vegetation, PointCloud


class TestFindVegetation(unittest.TestCase):
    def test_no_vegetation(self):
        # Test case where there is no vegetation in the point cloud
        pc = PointCloud(points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]))
        indices = _find_vegetation(pc)
        self.assertEqual(len(indices), 0)

    def test_classification_filter(self):
        # Test case where vegetation is filtered by classification
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            classification=np.array([0, 3, 4]),
        )
        indices = _find_vegetation(pc)
        self.assertEqual(len(indices), 2)
        self.assertTrue(np.all(np.isin(pc.classification[indices], [3, 4])))

    def test_return_number_filter(self):
        # Test case where vegetation is filtered by return number
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            return_number=np.array([2, 1, 1]),
            num_returns=np.array([2, 2, 2]),
        )
        indices = _find_vegetation(pc)
        self.assertEqual(len(indices), 2)
        self.assertEqual(indices[0], 1)
        self.assertEqual(indices[1], 2)

    def test_no_classification(self):
        # Test case where classification is not set for all points
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            return_number=np.array([2, 1, 1]),
            num_returns=np.array([2, 2, 2]),
        )
        indices = _find_vegetation(pc)
        self.assertEqual(len(indices), 2)
        self.assertEqual(indices[0], 1)
        self.assertEqual(indices[1], 2)

    def test_no_return_number(self):
        # Test case where return number is not set for all points
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            classification=np.array([0, 3, 4]),
        )
        indices = _find_vegetation(pc)
        self.assertEqual(len(indices), 2)
        self.assertTrue(np.all(np.isin(pc.classification[indices], [3, 4])))


if __name__ == "__main__":
    unittest.main()
