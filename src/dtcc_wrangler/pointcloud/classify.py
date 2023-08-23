from dtcc_model import PointCloud
from dtcc_wrangler.register import register_model_method
from dtcc_wrangler.pointcloud.filters import _find_vegetation
import numpy as np


@register_model_method
def classify_vegetation(pc: PointCloud) -> PointCloud:
    """
    Classify vegetation in a point cloud based on the return number.
    Warning: This method may overwrite vegetation classifications already present in the point cloud.

    Args:
        pc (PointCloud): The `PointCloud` object to classify vegetation in.

    Returns:
        PointCloud: The `PointCloud` object with the vegetation classified.
    """
    veg_indices = _find_vegetation(pc)
    if len(pc.classification) == 0:
        pc.classification = np.ones(len(pc.points))
    if len(veg_indices) > 0:
        pc.classification[veg_indices] = 3
    return pc
