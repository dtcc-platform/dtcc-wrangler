from shapely.geometry import Polygon
from typing import List, Tuple

from dtcc_model import Building, City
import shapely
from shapely.geometry import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    MultiLineString,
    JOIN_STYLE,
)
import math
import shapely.ops
import shapely.affinity
from shapely.validation import make_valid
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import connected_components
from collections import defaultdict
from itertools import combinations, groupby

from dtcc_wrangler.logging import debug, info, warning, error, critical


def merge_polygons_convexhull(p1, p2):
    mp = MultiPolygon([p1, p2])
    return mp.convex_hull


def merge_polygon_hulls(p1, p2):
    p1_hull = p1.convex_hull
    p2_hull = p2.convex_hull
    mp = p1.union(p2)
    mp = make_valid(mp)
    if mp.geom_type == "Polygon":
        return mp
    else:
        return None


def merge_polygons_buffering(p1, p2, tol):
    b1 = p1.buffer(tol, 1, join_style=JOIN_STYLE.mitre)
    b2 = p2.buffer(tol, 1, join_style=JOIN_STYLE.mitre)
    m = b1.union(b2)
    m = m.buffer(-tol, 1, join_style=JOIN_STYLE.mitre)
    m = shapely.make_valid(m)
    if m.geom_type == "Polygon":
        return m
    else:
        return None


def merge_polygons_snapping(p1, p2, tol):
    coords = p2.exterior.coords[:]
    for idx, vertex in enumerate(coords):
        p = Point(vertex)
        nearest_point, _ = shapely.ops.nearest_points(p1.exterior, p)
        dist = p.distance(nearest_point)
        if dist > 0 and dist < tol:
            coords[idx] = nearest_point.coords[0]
    p2 = Polygon(coords)
    coords = p1.exterior.coords[:]
    for idx, vertex in enumerate(coords):
        p = Point(vertex)
        nearest_point, _ = shapely.ops.nearest_points(p2.exterior, p)
        dist = p.distance(nearest_point)
        if dist > 0 and dist < tol:
            coords[idx] = nearest_point.coords[0]
    p1 = Polygon(coords)

    m = p1.union(p2)
    m = make_valid(m)
    if m.geom_type == "Polygon":
        return m
    else:
        return None


def merge_polygons(p1, p2, tol):
    mp = p1.union(p2)
    # if mp.geom_type != "Polygon":
    #     info("Failed to merge polygons. Trying snapping")
    #     mp = merge_polygons_snapping(p1, p2, tol)
    if mp.geom_type != "Polygon":
        # info("Failed to merge polygons. Trying buffering")
        mp = merge_polygons_buffering(p1, p2, tol)
        if mp is None:
            mp = merge_polygon_hulls(p1, p2)
            if mp is None:
                info("Failed to merge polygons. Falling back to merging convex hull")
                mp = merge_polygons_convexhull(p1, p2)
    return mp


def simplify_polygon(p: Polygon, tol):
    sp = p.simplify(tol)
    if not sp.is_valid or sp.geom_type != "Polygon":
        sp = p.simplify(tol, preserve_topology=True)
    if sp.geom_type != "Polygon":
        sp = p
    return sp


def remove_slivers(p: Polygon, tol):
    # info("Removing slivers")
    b_p = p.buffer(tol, 1, join_style=JOIN_STYLE.mitre).buffer(
        -tol, 1, join_style=JOIN_STYLE.mitre
    )
    b_p = shapely.make_valid(b_p)
    if b_p.geom_type == "Polygon":
        return b_p
    else:
        b_p = merge_multipolygon(b_p, tol)
    return b_p


def remove_holes(p: Polygon):
    return Polygon(p.exterior)


def merge_multipolygon(multipolygon, tol=0.1):
    polygons = list(multipolygon.geoms)
    merged = []
    # orig_polygons = polygons.copy()
    if len(polygons) == 1:
        m = polygons[0]
    elif len(polygons) == 2:
        m = merge_polygons(polygons[0], polygons[1], tol)
    else:
        while len(polygons) > 0:
            p = polygons.pop()
            for i, p2 in enumerate(polygons):
                if p.intersects(p2.buffer(tol)):
                    p = merge_polygons(p, p2, tol)
                    polygons.pop(i)
                    polygons.append(p)
        merged.append(p)
        m = shapely.ops.unary_union(merged)
    m = make_valid(m)
    return m


def find_merge_candidates(polygons: List[Polygon], tol: float) -> List[List[int]]:
    """Find all polygons closer than _tolerance_ in a list of polygons and return a list of indices of polygons to be merged."""
    rtree = shapely.strtree.STRtree(polygons)
    merge_idxs = rtree.query(polygons, predicate="dwithin", distance=tol)
    merge_idxs = merge_idxs.T
    # keep = [m[0] != m[1] for m in merge_idxs]
    # merge_idxs = merge_idxs[keep]
    adj_matrix = lil_matrix(np.zeros((len(polygons), len(polygons))))
    for i, j in merge_idxs:
        adj_matrix[i, j] = 1
        adj_matrix[j, i] = 1
    # Find connected components using scipy.sparse.csgraph.connected_components
    _, labels = connected_components(adj_matrix, directed=False)
    polygon_indices = defaultdict(list)
    for idx, label in enumerate(labels):
        polygon_indices[label].append(idx)

    polygon_indices = [r for r in polygon_indices.values()]
    return polygon_indices


def merge_list_of_polygons(mcp: List[Polygon], tolerance=1e-2) -> Polygon:
    if len(mcp) == 1:
        return mcp[0]
    else:
        m = shapely.ops.unary_union(mcp)
        m = shapely.make_valid(m)
        if m.geom_type == "Polygon":
            return m
        else:
            m = merge_multipolygon(m, tolerance)
            if m.geom_type != "Polygon":
                warning("Failed to merge polygon list. Falling back to convex hull")
                m = m.convex_hull
            return m


def polygon_merger(
    polygons: List[Polygon], tolerance: float = 1e-2
) -> Tuple[List[Polygon], List[List[int]]]:
    """Merge all polygons closer than _tolerance_ in a list of polygons into a list of polygons and a list of indices of merged polygons."""
    merge_candidates = find_merge_candidates(polygons, tolerance)
    if len(merge_candidates) == len(polygons):
        # No polygons withon tolerance of each other
        return polygons, merge_candidates
    merge_candidate_polygons = []
    for mc in merge_candidates:
        merge_candidate_polygons.append([polygons[idx] for idx in mc])

    merged_polygons = []
    for mcp in merge_candidate_polygons:
        m = merge_list_of_polygons(mcp, tolerance)
        merged_polygons.append(m)

    return merged_polygons, merge_candidates


def widen_gaps(fp: Polygon, tol: float) -> Polygon:
    if shapely.minimum_clearance(fp) > tol:
        return fp
    edges = [
        LineString([fp.exterior.coords[i], fp.exterior.coords[i + 1]])
        for i in range(len(fp.exterior.coords) - 1)
    ]

    for idx1, idx2 in combinations(range(len(edges)), 2):
        if idx1 == idx2:
            continue
        edge1 = edges[idx1]
        edge2 = edges[idx2]
        distance = edge1.distance(edge2)
        if distance > 0 and distance < tol:
            nps = shapely.ops.nearest_points(edge1, edge2)
            midpoint = LineString([nps[0], nps[1]]).centroid
            mid_buffer = midpoint.buffer(tol)
            mid_buffer_intersects = MultiLineString(edges).intersection(mid_buffer)
            interesct_ch = mid_buffer_intersects.convex_hull
            fp = fp.union(interesct_ch)
            fp = fp.simplify(1e-3, True)
    return fp


def lengthen_edges(fp: Polygon, tol: float) -> Polygon:
    extr_verts = list(fp.exterior.coords)
    vertex_count = len(extr_verts) - 1
    edges = [
        LineString([extr_verts[i], extr_verts[i + 1]])
        for i in range(len(extr_verts) - 1)
    ]

    updated_verts = []
    for idx1, idx2 in combinations(range(len(edges)), 2):
        if idx1 == idx2:
            continue
        edge1 = edges[idx1]
        edge2 = edges[idx2]
        distance = edge1.distance(edge2)
        if distance > 0 and distance < tol:
            delta = (tol - distance) / 2
            nps = shapely.ops.nearest_points(edge1, edge2)
            centroid1 = nps[0]
            centroid2 = nps[1]
            dx = centroid2.x - centroid1.x
            dy = centroid2.y - centroid1.y
            length = (dx**2 + dy**2) ** 0.5
            unit_dx = dx / length
            unit_dy = dy / length
            t_edge1 = shapely.affinity.translate(
                edge1, -unit_dx * distance, -unit_dy * delta
            )
            t_edge2 = shapely.affinity.translate(
                edge2, unit_dx * distance, unit_dy * delta
            )
            updated_verts.append((idx1, t_edge1.coords[0]))
            updated_verts.append(((idx1 + 1) % vertex_count, t_edge1.coords[1]))
            updated_verts.append((idx2, t_edge2.coords[0]))
            updated_verts.append(((idx2 + 1) % vertex_count, t_edge2.coords[1]))

    # print(f"len(extr_verts) post: {len(extr_verts)}")
    updated_verts.sort(key=lambda x: x[0])
    # updated_verts = groupby(updated_verts, key=lambda x: x[0])
    # print(updated_verts)
    for idx, uv in groupby(updated_verts, key=lambda x: x[0]):
        min_dist = 1e6
        base_pt = extr_verts[idx]
        for _, pt in uv:
            dist = (pt[0] - base_pt[0]) ** 2 + (pt[1] - base_pt[1]) ** 2
            if dist < min_dist:
                min_dist = dist
                extr_verts[idx] = pt
    extr_verts[-1] = extr_verts[0]
    return Polygon(extr_verts, holes=fp.interiors)


def flatten_sharp_angles(fp: Polygon, min_angle: float, tol: float) -> Polygon:
    exterior_ring = list(fp.exterior.coords)
    updated = False
    inserted_verts = []
    for i in range(len(exterior_ring) - 1):
        p1 = exterior_ring[i]
        p2 = exterior_ring[i + 1]
        p3 = exterior_ring[(i + 2) % (len(exterior_ring) - 1)]
        angle = math.degrees(
            math.atan2(p3[1] - p2[1], p3[0] - p2[0])
            - math.atan2(p1[1] - p2[1], p1[0] - p2[0])
        )

        if abs(angle) < min_angle:
            updated = True
            normal = (-p2[1] + p1[1], p2[0] - p1[0])
            normal_mag = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            flip = -1 if angle > 0 else 1

            normal = (flip * normal[0] / normal_mag, flip * normal[1] / normal_mag)
            new_pt = (p2[0] + (normal[0] * tol), p2[1] + (normal[1] * tol))
            inserted_verts.append(((i + 1) % (len(exterior_ring) - 1), new_pt))

    if updated:
        for ins_idx, pt in inserted_verts:
            exterior_ring.insert(ins_idx + 1, pt)
        return Polygon(exterior_ring, holes=fp.interiors)
    else:
        return fp
