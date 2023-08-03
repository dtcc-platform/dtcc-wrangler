from dtcc_wrangler.geometry.polygons import merge_polygon_list, simplify_polygon
from dtcc_wrangler.register import register_model_method
from dtcc_model import City, Building
from statistics import mean
import dataclasses


@register_model_method
def merger_buildings(city: City, max_distance=0.15):
    """Merge buildings that are close together
    args:
        city: City
        max_distance: float maximum distance between buildings
    returns:
        City
    """
    merged_city = dataclasses.replace(city)
    footprints = [b.footprint for b in city.buildings]
    merged_polygons, merged_polygons_idx = merge_polygon_list(footprints, max_distance)

    merged_city.buildings = []
    for idx, merged_polygon in enumerate(merged_polygons):
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
    return merged_city
