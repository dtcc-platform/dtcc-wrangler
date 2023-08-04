from dtcc_wrangler.geometry.polygons import (
    merge_polygon_list,
    simplify_polygon,
    remove_slivers,
    remove_holes,
)
from dtcc_wrangler.register import register_model_method
from dtcc_model import City, Building
from statistics import mean
import dataclasses
from copy import deepcopy


@register_model_method
def simplify_buildings(city: City, tolerance=0.1) -> City:
    """Simplify buildings
    args:
        city: City
        tolerance: float tolerance for simplification
    returns:
        City
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
    """Remove small buildings
    args:
        city: City
        min_area: float minimum area of building
    returns:
        City
    """
    filtered_city = deepcopy(city)
    filtered_city.buildings = []
    for b in city.buildings:
        print(b.footprint.area)
        if b.footprint.area > min_area:
            filtered_city.buildings.append(b)
    return filtered_city


@register_model_method
def merger_buildings(
    city: City, max_distance=0.15, simplify=True, remove_interior_holes=False
) -> City:
    """Merge buildings that are close together
    args:
        city: City
        max_distance: float maximum distance between buildings
    returns:
        City
    """
    merged_city = deepcopy(city)
    footprints = [b.footprint for b in city.buildings]
    merged_polygons, merged_polygons_idx = merge_polygon_list(footprints, max_distance)

    merged_city.buildings = []
    for idx, merged_polygon in enumerate(merged_polygons):
        if remove_interior_holes:
            merged_polygon = remove_holes(merged_polygon)
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
        merged_city.buildings.append(b)
    if simplify:
        merged_city = simplify_buildings(merged_city, max_distance / 2)
    return merged_city
