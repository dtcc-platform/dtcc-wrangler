import unittest
from pathlib import Path
import dtcc_io
import dtcc_wrangler
import shapely


class TestWidenGap(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "poly_fix" / "small_gap.shp"
        ).resolve()
        testcase_city = dtcc_io.load_city(building_shp_file)
        cls.test_poly = testcase_city.buildings[0].footprint

    def test_widen_gap1(self):
        new_poly = dtcc_wrangler.geometry.polygons.widen_gaps(self.test_poly, 1.0)
        self.assertGreaterEqual(shapely.minimum_clearance(new_poly), 1.0)

    def test_widen_gap2(self):
        new_poly = dtcc_wrangler.geometry.polygons.widen_gaps(self.test_poly, 2.0)
        self.assertGreaterEqual(shapely.minimum_clearance(new_poly), 2.0)


class TestLengthenEdges(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "poly_fix" / "short_edges.shp"
        ).resolve()
        testcase_city = dtcc_io.load_city(building_shp_file)
        cls.test_poly = testcase_city.buildings[0].footprint

    def test_lengthen_edges1(self):
        new_poly = dtcc_wrangler.geometry.polygons.lengthen_edges(self.test_poly, 1.0)
        self.assertGreaterEqual(shapely.minimum_clearance(new_poly) + 1e-2, 1.0)

    def test_lengthen_edges2(self):
        new_poly = dtcc_wrangler.geometry.polygons.lengthen_edges(self.test_poly, 2.0)
        self.assertGreaterEqual(shapely.minimum_clearance(new_poly) + 2 * (1e-2), 2.0)


class TestSharpAngle(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "poly_fix" / "sharp_angle.shp"
        ).resolve()
        testcase_city = dtcc_io.load_city(building_shp_file)
        cls.test_poly = testcase_city.buildings[0].footprint

    def test_sharp_angle1(self):
        new_poly = dtcc_wrangler.geometry.polygons.flatten_sharp_angles(
            self.test_poly, 10, 2.0
        )
        self.assertGreaterEqual(shapely.minimum_clearance(new_poly) + 1e-1, 2.0)


class TestFixCity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "poly_fix" / "testcase1.shp"
        ).resolve()
        testcase_city = dtcc_io.load_city(building_shp_file)
        cls.test_city = testcase_city

    def test_fix_city(self):
        fixed_city = self.test_city.merge_buildings(1).fix_building_clearance(1, 20)
        self.assertEqual(len(fixed_city.buildings), 2)
        for b in fixed_city.buildings:
            self.assertGreaterEqual(shapely.minimum_clearance(b.footprint) + 1e-2, 1)


if __name__ == "__main__":
    unittest.main()
