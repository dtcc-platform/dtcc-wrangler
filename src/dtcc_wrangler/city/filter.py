from dtcc_model import City, Building
from shapely.geometry import Point, Polygon
from dtcc_wrangler.register import register_model_method

from typing import Union

import shapely


@register_model_method
def surrounding_buildings(
    city: City,
    center: Union[Building, Point, tuple],
    distance: float,
    exclude_center_building=False,
) -> list:
    """
    Get a list of buildings surrounding a given building.

    Args:
        city (City): The city to search in.
        center (Union[Building, Point, tuple]): The center of the search.
        distance (float): The distance to search around the building.

    Returns:
        list: A list of buildings surrounding the given building.
    """
    surrounding = []
    if isinstance(center, Building):
        center = center.footprint.centroid

    elif isinstance(center, tuple):
        center = Point(center)
    elif isinstance(center, Point):
        pass
    else:
        raise TypeError(
            f"Expected Building, Point, or tuple, got {type(center)} instead"
        )
    for b in city.buildings:
        if exclude_center_building and b.footprint.contains(center):
            continue
        if b.footprint.centroid.distance(center) < distance:
            surrounding.append(b)
    return surrounding
