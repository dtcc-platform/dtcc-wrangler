import unittest
import numpy as np
import rasterio
from shapely.geometry import Polygon
import dtcc_wrangler
from dtcc_model import Raster


class TestBurnPolygons(unittest.TestCase):
    def test_burn_polygons(self):
        # Create a test raster
        in_raster = Raster()
        in_raster.data = np.zeros((10, 10), dtype=np.uint8)
        in_raster.georef = rasterio.transform.from_bounds(0, 0, 10, 10, 10, 10)

        # Define test polygons and values
        poly1 = Polygon([(1, 1), (1, 3), (3, 3), (3, 1)])
        poly2 = Polygon([(6, 6), (6, 8), (8, 8), (8, 6)])
        poly_values = [(poly1, 1), (poly2, 2)]

        # Burn the polygons into the test raster
        out_raster = in_raster.burn_polygons(poly_values, all_touched=False)
        # Check that the burned values are correct
        expected_data = np.zeros((10, 10), dtype=np.uint8)
        expected_data[1:3, 1:3] = 1
        expected_data[6:8, 6:8] = 2
        expected_data = np.flipud(expected_data)
        self.assertTrue(np.array_equal(out_raster.data, expected_data))
