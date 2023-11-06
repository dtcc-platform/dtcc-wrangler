from dtcc_model.geometry.mesh import Mesh
import numpy as np
from logging import info, warning, error
from dtcc_wrangler.register import register_model_method


@register_model_method
def get_markers(
    mesh: Mesh, markers: list = [], threshold: int = None, invert_filter=False
) -> Mesh:
    """
    Get a mesh with only the markers specified.

    Args:
        mesh (Mesh): The input mesh.
        markers (list of int): The markers to keep (default []).
        threshold (int): return mesh with markers great or equal to this value (default None).
        invert_filter (bool): Whether to invert the filter (default False).

    Returns:
        Mesh: The filtered mesh.
    """

    if len(mesh.markers) != len(mesh.faces):
        error("Mesh does not have a marker for every face. Nothing is filtered.")
        return None
    return_mesh = mesh.copy()
    marker_indices = []
    for idx, marker in enumerate(mesh.markers):
        if (marker in markers) and (not invert_filter):
            marker_indices.append(idx)
        elif (marker not in markers) and invert_filter:
            marker_indices.append(idx)
        if threshold is not None:
            if (marker >= threshold) and (not invert_filter):
                marker_indices.append(idx)
            elif (marker < threshold) and invert_filter:
                marker_indices.append(idx)
    return_mesh.faces = mesh.faces[marker_indices]
    return_mesh.markers = mesh.markers[marker_indices]
    if len(mesh.normals) == len(mesh.faces):
        return_mesh.normals = mesh.normals[marker_indices]
    if len(mesh.face_colors) == len(mesh.faces):
        return_mesh.face_colors = mesh.face_colors[marker_indices]

    return return_mesh


def _duplicate_elemente_indices(arr):
    _, idx, inv_idx, cnt = np.unique(
        arr, axis=0, return_inverse=True, return_index=True, return_counts=True
    )
    dups = np.where(cnt > 1)
    dups = idx[dups]
    dup_list = []
    for d in dups:
        dup_list.append(np.where(inv_idx == inv_idx[d])[0])
    return dup_list


@register_model_method
def clean(mesh: Mesh, merge_faces=True) -> Mesh:
    """
    Remove duplicate and unused vertices. Optionally merge
    duplicate faces.
    """
    return_mesh = mesh.copy()
    v = return_mesh.vertices
    f = return_mesh.faces
    dup_list = _duplicate_elemente_indices(v)
    flat_f = f.flatten()
    for dl in dup_list:
        keep = dl[0]
        for d in dl[1:]:
            flat_f[flat_f == d] = keep

    unused = set(range(len(v))) - set(flat_f)
    unused = sorted(list(unused), reverse=True)
    info(f"Removing {len(unused)} unused vertices.")
    v = np.delete(v, unused, axis=0)
    if len(mesh.vertex_colors) > 0:
        vc = np.delete(mesh.vertex_colors, unused, axis=0)
        return_mesh.vertex_colors = vc
    for u in unused:
        flat_f[flat_f >= u] -= 1
    f = flat_f.reshape((-1, 3))
    if merge_faces:
        dup_list = _duplicate_elemente_indices(f)
        duplicate_faces = []
        for dl in dup_list:
            for d in dl[1:]:
                duplicate_faces.append(d)
        if len(duplicate_faces) > 0:
            info(f"Removing {len(duplicate_faces)} duplicate faces.")
            f = np.delete(f, duplicate_faces, axis=0)
            if len(mesh.face_colors) > 0:
                fc = np.delete(mesh.face_colors, duplicate_faces, axis=0)
                return_mesh.face_colors = fc
            if len(mesh.markers) > 0:
                m = np.delete(mesh.markers, duplicate_faces, axis=0)
                return_mesh.markers = m
            if len(mesh.normals) > 0:
                n = np.delete(mesh.normals, duplicate_faces, axis=0)
                return_mesh.normals = n

    return_mesh.vertices = v
    return_mesh.faces = f

    return return_mesh
