from dtcc_model import Landuse, Building
from collections import defaultdict
from statistics import mean, median, stdev
from dtcc_wrangler.register import register_model_method
from dtcc_model import City


@register_model_method
def summarize_landuse(city: City, print_summary=True):
    """
    Summarize the land use of a `City` object.

    Args:
        city (City): The `City` object to summarize the land use of.
        print_summary (bool): Whether to print the summary to the console (default True).

    Returns:
        Dict[str, float]: A dictionary containing the area of each land use type in square meters.
    """
    landuse_summaries = defaultdict(float)
    for lu in city.landuse:
        landuse_summaries[lu.landuse.name] += lu.area
    if print_summary:
        print("Landuse summary:")
        for k, v in landuse_summaries.items():
            print(f"  {k}: {v:.0f} m²")
    return landuse_summaries


@register_model_method
def summarize_buildings(city: City, print_summary=True):
    """
    Summarize the buildings of a `City` object.

    Args:
        city (City): The `City` object to summarize the buildings of.
        print_summary (bool): Whether to print the summary to the console (default True).

    Returns:
        Dict[str, float]: A dictionary containing the number of buildings, total footprint area, average footprint area, median footprint area, and standard deviation of footprint area in square meters.
    """
    building_footprint_areas = [b.area for b in city.buildings]
    summary = {
        "number": len(building_footprint_areas),
        "total_area": sum(building_footprint_areas),
        "average_area": mean(building_footprint_areas),
        "median_area": median(building_footprint_areas),
        "std_area": stdev(building_footprint_areas),
    }
    if print_summary:
        print("Building summary:")
        print(f"  Number of buildings: {len(building_footprint_areas)}")
        print(f"  Total footprint area: {sum(building_footprint_areas):.0f} m²")
        print(f"  Average footprint area: {mean(building_footprint_areas):.0f} m²")
        print(f"  Median footprint area: {median(building_footprint_areas):.0f} m²")
        print(
            f"  Standard deviation footprint area: {stdev(building_footprint_areas):.0f} m²"
        )
    return summary
