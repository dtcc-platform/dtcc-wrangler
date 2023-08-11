from dtcc_wrangler.geometry.polygons import (
    polygon_merger,
    simplify_polygon,
    remove_slivers,
    remove_holes,
)

from dtcc_wrangler.register import register_model_method
from dtcc_model import City, Building
from statistics import mean
import dataclasses
from copy import deepcopy
from collections import defaultdict


@register_model_method
def simplify_buildings(city: City, tolerance=0.1) -> City:
    """
    Simplify the footprint of buildings in a `City` object.

    Args:
        city (City): The `City` object to simplify the buildings of.
        tolerance (float): The tolerance for simplification (default 0.1).

    Returns:
        City: A new `City` object with the simplified buildings.
    """
    simplified_city = deepcopy(city)
    simplified_city.buildings = []
    for b in city.buildings:
        b = dataclasses.replace(b)
        b.footprint = simplify_polygon(b.footprint, tolerance)
        simplified_city.buildings.append(b)
    return simplified_city


@register_model_method
def remove_small_buildings(city: City, min_area=10) -> City:
    """
    Remove small buildings from a `City` object.

    Args:
        city (City): The `City` object to remove small buildings from.
        min_area (float): The minimum area in square meters for a building to be kept (default 10).

    Returns:
        City: A new `City` object with the small buildings removed.
    """
    filtered_city = deepcopy(city)
    filtered_city.buildings = []
    for b in city.buildings:
        if b.footprint.area > min_area:
            filtered_city.buildings.append(b)
    return filtered_city


@register_model_method
def merge_buildings(
    city: City, max_distance=0.15, simplify=True, properties_merge_strategy="list"
) -> City:
    """
    Merge buildings that are close together.

    Parameters
    ----------
    max_distance : float, optional
        The maximum distance in meters between buildings to consider them close enough to merge (default 0.15).
    simplify : bool, optional
        Whether to simplify the merged buildings (default True).
    properties_merge_strategy : str, optional
        The strategy for merging properties. Options are 'list' and 'sample'. 'list' will create a list of all properties for the merged building. 'sample' will pick a property value from a random building (default "list").

    Returns
    -------
    City
        A new `City` object with the merged buildings.
    """
    merged_city = deepcopy(city)
    footprints = [b.footprint for b in city.buildings]
    merged_polygons, merged_polygons_idx = polygon_merger(footprints, max_distance)

    merged_city.buildings = []
    for idx, merged_polygon in enumerate(merged_polygons):
        merged_polygon = remove_slivers(merged_polygon, max_distance / 2)

        b = dataclasses.replace(city.buildings[merged_polygons_idx[idx][0]])
        b.footprint = merged_polygon
        b.height = mean([city.buildings[i].height for i in merged_polygons_idx[idx]])
        b.ground_level = min(
            [city.buildings[i].ground_level for i in merged_polygons_idx[idx]]
        )
        b.roofpoints = city.buildings[merged_polygons_idx[idx][0]].roofpoints
        for i in merged_polygons_idx[idx][1:]:
            b.roofpoints.merge(city.buildings[i].roofpoints)

        property_dicts = [
            city.buildings[i].properties for i in merged_polygons_idx[idx]
        ]
        if properties_merge_strategy == "list":
            merged_properties = defaultdict(list)
            for p in property_dicts:
                for k, v in p.items():
                    merged_properties[k].append(v)
        elif properties_merge_strategy == "sample":
            merged_properties = {}
            for p in property_dicts:
                for k, v in p.items():
                    if v:
                        merged_properties[k] = v
        b.properties = dict(merged_properties)

        merged_city.buildings.append(b)
    if simplify:
        merged_city = simplify_buildings(merged_city, max_distance / 2)
    return merged_city
