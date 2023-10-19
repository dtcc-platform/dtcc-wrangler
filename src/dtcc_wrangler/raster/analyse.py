import numpy as np
from scipy.signal import convolve2d
from dtcc_model import Raster
from dtcc_wrangler.register import register_model_method


@register_model_method
def slope_aspect(dem: Raster) -> tuple[Raster, Raster]:
    cell_size = dem.cell_size[0]
    kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) / (8.0 * cell_size)
    kernel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]) / (8.0 * cell_size)

    dzdx = convolve2d(dem.data, kernel_x, mode="same", boundary="symm")
    dzdy = convolve2d(dem.data, kernel_y, mode="same", boundary="symm")

    slope = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
    aspect = np.arctan2(-dzdy, dzdx)

    slope_raster = dem.copy(no_data=True)
    slope_raster.data = slope

    aspect_raster = dem.copy(no_data=True)
    aspect_raster.data = aspect

    return slope_raster, aspect_raster


@register_model_method
def TRI(dem: Raster, window_size=3) -> Raster:
    """
    Compute the Terrain Roughness Index (TRI) of a DEM using optimized array operations.

    Parameters:
    - dem: a Raster object representing the DEM.

    Returns:
    - A Raster object representing the TRI.
    """

    if (window_size % 2) == 0 or window_size < 2:
        raise ValueError("Window size must be odd and greater than 1.")

    # Create a kernel that has ones in all positions but the center.
    kernel = np.ones((window_size, window_size))
    center_index = window_size // 2
    kernel[center_index, center_index] = 0

    # Compute the squared difference between each cell and its neighbors.
    squared_diff = (
        convolve2d(dem.data**2, kernel, mode="same", boundary="symm")
        - 2 * convolve2d(dem.data, kernel, mode="same", boundary="symm")
        + (window_size * window_size) * dem.data**2
    )

    # Compute the TRI.
    tri = np.sqrt(squared_diff)

    tri_raster = dem.copy(no_data=True)
    tri_raster.data = tri

    return tri_raster


@register_model_method
def TPI(dem: Raster, window_size=3):
    """Compute the Topographic Position Index (TPI) of a DEM."""

    # Define averaging kernel
    kernel = np.ones((window_size, window_size)) / (window_size**2)

    # Compute the mean elevation of the neighborhood
    mean_elevation = convolve2d(dem.data, kernel, mode="same", boundary="symm")

    # Compute TPI
    tpi = dem.data - mean_elevation
    tpi_raster = dem.copy(no_data=True)
    tpi_raster.data = tpi

    return tpi_raster
