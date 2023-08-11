import numpy as np
from typing import List

from dtcc_model import PointCloud
from dtcc_io.logging import info, warning, error
from dtcc_wrangler.register import register_model_method


@register_model_method
def remove_global_outliers(pc: PointCloud, margin: float):
    """
    Remove outliers from a `PointCloud` object using a global margin.

    Args:
        margin (float): The margin in standard deviations to consider a point an outlier.

    Returns:
        PointCloud: A new `PointCloud` object with the outliers removed.
    """
    z_pts = pc.points[:, 2]
    z_mean = np.mean(z_pts)
    z_std = np.std(z_pts)
    outliers = np.where(np.abs(z_pts - z_mean) > margin * z_std)[0]
    pc.remove_points(outliers)
    return pc


@register_model_method
def classification_filter(pc: PointCloud, classes: List[int], keep: bool = False):
    """
    Filter a `PointCloud` object based on its classification.

    Args:
        classes (List[int]): The classification values to keep or remove.
        keep (bool): Whether to keep the points with the specified classification values (default False, remove them).

    Returns:
        PointCloud: A new `PointCloud` object with the specified points removed.
    """
    if len(pc.points) != len(pc.classification):
        warning("Pointcloud not classified, returning original pointcloud.")
        return pc
    mask = np.isin(pc.classification, classes)
    if keep:
        mask = np.logical_not(mask)
    pc.remove_points(mask)
    return pc
