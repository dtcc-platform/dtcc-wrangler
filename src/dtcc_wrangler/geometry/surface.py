from dtcc_model.geometry.surface import Surface, MultiSurface
from dtcc_wrangler.register import register_model_method
from dtcc_wrangler.geometry.polygons import merge_list_of_polygons
from shapely.geometry import Polygon, MultiPolygon

@register_model_method
def flatten(ms: MultiSurface) -> Polygon:
    """Flatten a MultiSurface to a single 2D Polygon.

    Args:
        ms (MultiSurface): The MultiSurface to flatten.

    Returns:
        Polygon: The flattened Polygon.
    """
    polygons = [Polygon(s.vertices[:, :2]).buffer(0) for s in ms.surfaces]
    polygons = [p for p in polygons if not p.is_empty and p.area > 1e-2]
    merged = merge_list_of_polygons(polygons)

    return merged