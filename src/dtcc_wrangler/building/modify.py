from dtcc_model import Building, GeometryType, MultiSurface, Surface
from dtcc_wrangler.geometry.multisurface import project2D
from shapely.geometry import Polygon
from logging import debug, info, warning, error


def get_building_footprint(building: Building, geom_type: GeometryType = None):
    if geom_type is not None:
        geom = building.flatten_geometry(geom_type)
    else:
        lod_levels = [GeometryType.LOD0, GeometryType.LOD1, GeometryType.LOD2]
        for lod in lod_levels:
            geom = building.flatten_geometry(lod)
            if geom is not None:
                break

    if geom is None:
        warning(f"Building {building.id} has no LOD geometry.")
        return None
    if isinstance(geom, Surface):
        try:
            p = Polygon(geom.vertices, geom.holes)
        except:
            print(geom.vertices.shape)
            # print(geom.holes)
        else:
            return Polygon(geom.vertices, geom.holes)
    if isinstance(geom, MultiSurface):
        return geom.project2D()
