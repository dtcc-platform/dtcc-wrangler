import unittest
from pathlib import Path
from copy import deepcopy
import dtcc_io as io


class TestProcessCity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "MinimalCase" / "PropertyMap.shp"
        ).resolve()

        landuse_shp_file = (
            Path(__file__).parent / ".." / "data" / "landuse_testdata.shp"
        ).resolve()

        cls.city = io.load_footprints(building_shp_file, "uuid")
        cls.lu = io.load_landuse(landuse_shp_file, landuse_field="DETALJTYP")
        cls.city.landuse = cls.lu

    def test_summarize_buildings(self):
        building_summary = self.city.summarize_buildings(print_summary=False)
        self.assertEqual(building_summary["number"], 5)
        self.assertAlmostEqual(building_summary["total_area"], 118, places=0)

    def test_summarize_landuse(self):
        landuse_summary = self.city.summarize_landuse(print_summary=True)
        self.assertTrue("GRASS" in landuse_summary)
        self.assertTrue("URBAN" in landuse_summary)
        self.assertTrue("WATER" in landuse_summary)
        self.assertAlmostEqual(landuse_summary["WATER"], 8042, places=0)


class TestModifyCity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "MinimalCase" / "PropertyMap.shp"
        ).resolve()

        case1_test_file = (
            Path(__file__).parent / ".." / "data" / "poly_merging" / "testcase1.shp"
        ).resolve()
        case2_test_file = (
            Path(__file__).parent / ".." / "data" / "poly_merging" / "testcase2.shp"
        ).resolve()

        cls.city = io.load_footprints(building_shp_file, "uuid")
        cls.testcase1 = io.load_footprints(case1_test_file, "uuid")
        cls.testcase2 = io.load_footprints(case2_test_file, "uuid")

    def test_merge_nothing(self):
        merged_city = self.city.merge_buildings(0.1)
        self.assertEqual(len(merged_city.buildings), len(self.city.buildings))

    def test_merge_case1(self):
        merged_city = self.testcase1.merge_buildings(0.1, min_area=5)
        self.assertEqual(len(merged_city.buildings), 1)

    def test_merge_case2(self):
        merged_city = self.testcase2.merge_buildings(0.1,min_area=5)
        self.assertEqual(len(merged_city.buildings), 3)

        merged_city = self.testcase2.merge_buildings(1.0,min_area=5)
        self.assertEqual(len(merged_city.buildings), 2)

    def test_remove_small_buildings(self):
        filtered_city = self.testcase2.remove_small_buildings(10)

        self.assertEqual(
            len(filtered_city.buildings), len(self.testcase2.buildings) - 3
        )

    def test_merge_heights_mean(self):
        tc2 = deepcopy(self.testcase2)
        for b in tc2.buildings:
            b.height = 10
            b.ground_level = 2
        tc2.buildings[0].height = 20
        tc2.buildings[0].ground_level = 1
        merged_city = tc2.merge_buildings(0.1)
        self.assertGreater(merged_city.buildings[0].height, 10)
        self.assertEqual(merged_city.buildings[-1].height, 10)

        self.assertEqual(merged_city.buildings[0].ground_level, 1)
        self.assertEqual(merged_city.buildings[-1].ground_level, 2)

    def test_merge_heights_area_weighted(self):
        tc = deepcopy(self.testcase1)
        for b in tc.buildings:
            b.height = 10
            b.ground_level = 2
        tc.buildings[9].height = 20

        merged_city = tc.merge_buildings(0.1, height_merge_strategy="area_weighted")
        self.assertAlmostEqual(merged_city.buildings[0].height, 19.4, places=1)

    def test_merge_heights_max(self):
        tc2 = deepcopy(self.testcase2)
        for b in tc2.buildings:
            b.height = 10
            b.ground_level = 2
        tc2.buildings[0].height = 20
        tc2.buildings[0].ground_level = 1
        merged_city = tc2.merge_buildings(0.1, height_merge_strategy="max")
        self.assertEqual(merged_city.buildings[0].height, 20)


class TestCalculateBounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        building_shp_file = (
            Path(__file__).parent / ".." / "data" / "MinimalCase" / "PropertyMap.shp"
        ).resolve()

        cls.city = io.load_footprints(building_shp_file, "uuid")

    def test_calculate_bounds(self):
        self.city.calculate_bounds()
        city_bounds = self.city.bounds.tuple
        self.assertAlmostEqual(city_bounds[0], -5.142, places=3)
        self.assertAlmostEqual(city_bounds[1], -15.975, places=3)
        self.assertAlmostEqual(city_bounds[2], 12.99, places=3)
        self.assertAlmostEqual(city_bounds[3], -1.098, places=3)

    def test_calculate_bounds_with_buffer(self):
        self.city.calculate_bounds(buffer=1)
        city_bounds = self.city.bounds.tuple
        self.assertAlmostEqual(city_bounds[0], -6.142, places=3)
        self.assertAlmostEqual(city_bounds[1], -16.975, places=3)
        self.assertAlmostEqual(city_bounds[2], 13.99, places=3)
        self.assertAlmostEqual(city_bounds[3], -0.098, places=3)
