from dtcc_wrangler.pointcloud.convert import rasterize
from dtcc_model import City, PointCloud, Raster
from dtcc_wrangler.register import register_model_method


@register_model_method
def terrain_from_pointcloud(
    city: City,
    pc: PointCloud,
    cell_size: float,
    window_size=3,
    radius=0,
    ground_only=True,
) -> City:
    """
    Generate a terrain model from a point cloud using interpolation.

    Args:
        pc (PointCloud): The `PointCloud` object to use for terrain generation.
        cell_size (float): The cell size in meters for the terrain model.
        window_size (int): The window size for interpolation (default 3).
        radius (float): The radius for interpolation (default 0).
        ground_only (bool): Whether to use only ground points for terrain generation (default True).

    Returns:
        City: The `City` object enriched with the terrain model.
    """
    dem = rasterize(
        pc,
        cell_size,
        bounds=city.bounds,
        window_size=window_size,
        radius=radius,
        ground_only=ground_only,
    )
    city.terrain = dem
    return city
