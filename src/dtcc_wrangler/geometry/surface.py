from dtcc_model.geometry import Surface, Mesh
from dtcc_wrangler.register import register_model_method
import numpy as np
@register_model_method
def triangulate(s: Surface) -> Mesh:
    """Triangulate a Surface.

    Args:
        s (Surface): The Surface to triangulate.

    Returns:
        Mesh: a triangular Mesh representation of the Surface.
    """
    m = Mesh()
    if len(s.vertices) < 3:
        return m
    m.vertices = s.vertices.flatten()
    if len(s.vertices) == 3:
        m.faces = np.array([[0, 1, 2]])
    if len(s.vertices) == 4:
        m.faces = np.array([[0, 1, 2], [0, 2, 3]])
    if len(s.vertices) > 4:
        #TODO: implement triangulation
        pass
    return m

