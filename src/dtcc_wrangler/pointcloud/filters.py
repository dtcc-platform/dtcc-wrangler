import numpy as np
from typing import List

from dtcc_model import PointCloud
from dtcc_io.logging import info, warning, error
from dtcc_wrangler.register import register_model_method


@register_model_method
def remove_global_outliers(pc: PointCloud, margin: float):
    """Remove outliers from a pointcloud using a global margin."""
    z_pts = pc.points[:, 2]
    z_mean = np.mean(z_pts)
    z_std = np.std(z_pts)
    outliers = np.where(np.abs(z_pts - z_mean) > margin * z_std)[0]
    pc.remove_points(outliers)
    return pc


@register_model_method
def classification_filter(pc: PointCloud, classes: List[int], keep: bool = False):
    """Remove points from a pointcloud based on their classification.
    @param pc: PointCloud
    @param classes: List of classes to remove
    @param keep: If True, keep only the specified classes
    """
    if len(pc.points) != len(pc.classification):
        warning("Pointcloud not classified, returning original pointcloud.")
        return pc
    mask = np.isin(pc.classification, classes)
    if keep:
        mask = np.logical_not(mask)
    pc.remove_points(mask)
    return pc
