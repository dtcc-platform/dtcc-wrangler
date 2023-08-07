import unittest
import dtcc_io as io
from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon
from dtcc_wrangler.geometry.polygons import polygon_merger, simplify_polygon


class TestMergePolygons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1 = Polygon([[0, 0], [0, 1], [1, 1], [1, 0]])
        cls.p2 = Polygon([[1.1, 0], [1.1, 1], [2.1, 1], [2.1, 0]])
        cls.p3 = Polygon([[3, 3], [3, 4], [4, 4], [4, 3]])

    def test_merge_polygons(self):
        polys = [self.p1, self.p2, self.p3]
        merged_polygons, merged_polygons_idx = polygon_merger(polys, 0.15)
        self.assertEqual(len(merged_polygons), 2)
        self.assertEqual(len(merged_polygons_idx), 2)
        self.assertEqual(merged_polygons_idx[0], [0, 1])
        self.assertEqual(merged_polygons_idx[1], [2])


class TestSimplifyPolygons(unittest.TestCase):
    def test_simplify_polygon(self):
        p1 = Polygon([[0, 0], [0, 1], [1, 1], [1.001, 1.001], [1.1, 0.1], [1, 0]])
        s1 = simplify_polygon(p1, 0.1)
        s2 = simplify_polygon(p1, 0.01)
        s3 = simplify_polygon(p1, 0.2)
        s4 = simplify_polygon(p1, 5)
        self.assertEqual(len(s1.exterior.coords), 5)
        self.assertEqual(len(s2.exterior.coords), 6)
        self.assertEqual(len(s3.exterior.coords), 5)

        self.assertEqual(s4.geom_type, "Polygon")
        self.assertGreaterEqual(s4.area, 1)
