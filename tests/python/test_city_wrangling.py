import unittest
from pathlib import Path

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
        merged_city = self.city.merger_buildings(0.1)
        self.assertEqual(len(merged_city.buildings), len(self.city.buildings))

    def test_merge_case1(self):
        merged_city = self.testcase1.merger_buildings(0.1)
        self.assertEqual(len(merged_city.buildings), 1)

    def test_merge_case2(self):
        merged_city = self.testcase2.merger_buildings(0.1)
        self.assertEqual(len(merged_city.buildings), 3)

        merged_city = self.testcase2.merger_buildings(1.0)
        self.assertEqual(len(merged_city.buildings), 2)

    def test_remove_small_buildings(self):
        filtered_city = self.testcase2.remove_small_buildings(10)

        self.assertEqual(
            len(filtered_city.buildings), len(self.testcase2.buildings) - 3
        )
