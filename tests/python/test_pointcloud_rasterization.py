import unittest
import numpy as np
from pathlib import Path

import dtcc_wrangler
import dtcc_io as io

data_dir = (Path(__file__).parent / "../data").resolve()


class TestRasterize(unittest.TestCase):
    def test_rasterize(self):
        pc = io.load_pointcloud(data_dir / "MinimalCase" / "pointcloud.las")
        raster = pc.rasterize(1)
        self.assertEqual(raster.width, 24)
        self.assertEqual(raster.height, 21)
