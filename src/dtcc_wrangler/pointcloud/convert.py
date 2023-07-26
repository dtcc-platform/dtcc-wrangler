from pypoints2grid import points2grid
import numpy as np
import dtcc_model as model
import rasterio.transform
from dtcc_model import PointCloud, Bounds
from dtcc_wrangler.register import register_model_method


@register_model_method
def rasterize(
    pc: PointCloud,
    cell_size: float,
    bounds: Bounds = None,
    window_size: int = 3,
    radius: float = 0,
    ground_only: bool = True,
) -> model.Raster:
    """Rasterize a pointcloud"""
    if (
        ground_only
        and (len(pc.classification) == len(pc.points))
        and 2 in pc.used_classifications()
    ):
        ground_point_idx = np.where(np.isin(pc.classification, [2, 9]))[0]
        ground_points = pc.points[ground_point_idx]
    else:
        ground_points = pc.points
    if bounds is None:
        bounds = pc.bounds

    dem = points2grid(
        ground_points, cell_size, bounds.tuple, window_size=window_size, radius=radius
    )
    dem_raster = model.Raster()
    dem_raster.data = dem
    dem_raster.nodata = 0
    dem_raster.georef = rasterio.transform.from_origin(
        bounds.west, bounds.north, cell_size, cell_size
    )
    dem_raster = dem_raster.fill_holes()
    # print(f"Rasterized pointcloud to {dem_raster}")
    return dem_raster
