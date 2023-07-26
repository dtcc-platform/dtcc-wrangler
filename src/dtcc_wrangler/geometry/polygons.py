from shapely.geometry import Polygon
from typing import List, Tuple


def merge_polygons(
    polygons: List[Polygon], tolerance: float = 1e-6
) -> Tuple[List[Polygon], List[Tuple[int]]]:
    """Merge all polygons closer than _tolerance_ in a list of polygons into a list of polygons and a list of indices of merged polygons."""
    pass
