import unittest
import numpy as np
from dtcc_model import Raster
import dtcc_wrangler


class TestComputeSlopeAspect(unittest.TestCase):
    def test_compute_slope_aspect(self):
        # Create test DEM
        dem_data = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
        dem = Raster(data=dem_data)

        # Compute slope and aspect
        slope, aspect = dem.slope_aspect()

        # Check slope and aspect values
        expected_slope_data = np.array(
            [
                [0.46364761, 0.46364761, 0.46364761],
                [0.78539816, 0.78539816, 0.78539816],
                [0.46364761, 0.46364761, 0.46364761],
            ]
        )
        expected_aspect_data = np.array(
            [
                [-1.57079633, -1.57079633, -1.57079633],
                [-1.57079633, -1.57079633, -1.57079633],
                [-1.57079633, -1.57079633, -1.57079633],
            ]
        )
        np.testing.assert_allclose(slope.data, expected_slope_data)
        np.testing.assert_allclose(aspect.data, expected_aspect_data)

    def test_tri(self):
        dem_data = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
        dem = Raster(data=dem_data)
        tri = dem.TRI()
        expected_tri_data = np.array(
            [[2, 2, 2], [6.480741, 6.480741, 6.480741], [9.797959, 9.797959, 9.797959]]
        )
        np.testing.assert_allclose(tri.data, expected_tri_data)

    def test_tpi(self):
        dem_data = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
        dem = Raster(data=dem_data)
        tpi = dem.TPI()
        expected_tpi_data = np.array(
            [[-1 / 3, -1 / 3, -1 / 3], [0, 0, 0], [1 / 3, 1 / 3, 1 / 3]]
        )
        np.testing.assert_allclose(
            tpi.data,
            expected_tpi_data,
            rtol=1e-05,
            atol=1e-08,
        )
