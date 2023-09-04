from dtcc_wrangler.register import register_model_method
import numpy as np
from dtcc_model import Mesh


@register_model_method
def triangulate(mesh: Mesh):
    """Triangulate the mesh.

    Returns:
        Mesh: The triangulated mesh.
    """
    new_mesh = mesh.copy()
    new_faces = []
    for face in mesh.faces:
        if len(face) > 3:
            for i in range(1, len(face) - 1):
                new_faces.append([face[0], face[i], face[i + 1]])
        else:
            new_faces.append(face)
    new_mesh.faces = np.array(new_faces)
    return new_mesh
