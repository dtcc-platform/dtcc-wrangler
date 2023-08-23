import unittest
import numpy as np
from dtcc_wrangler.pointcloud.classify import classify_vegetation, PointCloud


class TestClassifyVegetation(unittest.TestCase):
    def test_no_vegetation(self):
        # Test case where there is no vegetation in the point cloud
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            classification=np.array([1, 1, 1]),
        )
        classified_pc = classify_vegetation(pc)
        self.assertTrue(np.all(classified_pc.classification == 1))

    def test_classification_filter(self):
        # Test case where vegetation is filtered by classification
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            classification=np.array([0, 3, 4]),
        )
        classified_pc = classify_vegetation(pc)
        self.assertTrue(np.all(classified_pc.classification == np.array([0, 3, 3])))

    def test_return_number_filter(self):
        # Test case where vegetation is filtered by return number
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            return_number=np.array([1, 1, 2]),
            num_returns=np.array([2, 2, 2]),
        )
        classified_pc = classify_vegetation(pc)
        self.assertTrue(np.all(classified_pc.classification == np.array([3, 3, 1])))

    def test_no_classification(self):
        # Test case where classification is not set for all points
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            return_number=np.array([1, 1, 2]),
            num_returns=np.array([2, 2, 2]),
        )
        classified_pc = classify_vegetation(pc)
        self.assertTrue(np.all(classified_pc.classification == np.array([3, 3, 1])))

    def test_no_return_number(self):
        # Test case where return number is not set for all points
        pc = PointCloud(
            points=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]),
            classification=np.array([0, 3, 4]),
        )
        classified_pc = classify_vegetation(pc)
        self.assertTrue(np.all(classified_pc.classification == np.array([0, 3, 3])))


if __name__ == "__main__":
    unittest.main()
