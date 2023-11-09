import dtcc_builder
import dtcc_io
import dtcc_model
import dtcc_wrangler
import dtcc_viewer
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from shapely.affinity import translate

from itertools import groupby
from shapely.ops import nearest_points
from itertools import combinations
import alphashape

from shapely import is_ccw
import numpy as np
import math
import sys

city = dtcc_io.load_city("testcase1.shp")

city = city.merge_buildings(1, simplify=False)
city.view()

for idx, b in enumerate(city.buildings):
    fp = b.footprint
    edges = [
        LineString([fp.exterior.coords[i], fp.exterior.coords[i + 1]])
        for i in range(len(fp.exterior.coords) - 1)
    ]

    edge_edge_distances = []
    for idx1, idx2 in combinations(range(len(edges)), 2):
        if idx1 == idx2:
            continue
        edge1 = edges[idx1]
        edge2 = edges[idx2]
        distance = edge1.distance(edge2)
        if distance > 0 and distance < 1:
            print(distance, idx1, idx2)
            nps = nearest_points(edge1, edge2)
            midpoint = LineString([nps[0], nps[1]]).centroid
            mid_buffer = midpoint.buffer(1)
            mid_buffer_intersects = MultiLineString(edges).intersection(mid_buffer)
            interesct_ch = mid_buffer_intersects.convex_hull
            fp = fp.union(interesct_ch)
            fp = fp.simplify(1e-3)
    city.buildings[idx].footprint = fp
city = city.simplify_buildings(1e-3)
city.view()
for idx, b in enumerate(city.buildings):
    fp = b.footprint
    extr_verts = list(fp.exterior.coords)
    print(f"len(extr_verts) pre: {len(extr_verts)}")
    edges = [
        LineString([extr_verts[i], extr_verts[i + 1]])
        for i in range(len(extr_verts) - 1)
    ]

    edge_edge_distances = []
    updated_verts = []
    for idx1, idx2 in combinations(range(len(edges)), 2):
        if idx1 == idx2:
            continue
        edge1 = edges[idx1]
        edge2 = edges[idx2]
        distance = edge1.distance(edge2)
        if distance > 0 and distance < 1:
            print("final pass", distance, idx1, idx2)
            delta = (1 - distance) / 2
            centroid1 = edge1.centroid
            centroid2 = edge2.centroid
            dx = centroid2.x - centroid1.x
            dy = centroid2.y - centroid1.y
            length = (dx**2 + dy**2) ** 0.5
            unit_dx = dx / length
            unit_dy = dy / length
            t_edge1 = translate(edge1, -unit_dx * distance, -unit_dy * distance)
            t_edge2 = translate(edge2, unit_dx * distance, unit_dy * distance)
            updated_verts.append((idx1, t_edge1.coords[0]))
            updated_verts.append((idx1 + 1, t_edge1.coords[1]))
            updated_verts.append((idx2, t_edge2.coords[0]))
            updated_verts.append((idx2 + 1, t_edge2.coords[1]))

    # print(f"len(extr_verts) post: {len(extr_verts)}")
    updated_verts.sort(key=lambda x: x[0])
    updated_verts = groupby(updated_verts, key=lambda x: x[0])
    for idx, uv in updated_verts:
        print(idx)
        min_dist = 1e6
        base_pt = extr_verts[idx]
        for _, pt in uv:
            dist = (pt[0] - base_pt[0]) ** 2 + (pt[1] - base_pt[1]) ** 2
            if dist < min_dist:
                min_dist = dist
                extr_verts[idx] = pt
    b.footprint = Polygon(extr_verts)
city.view()
footprints = [b.footprint for b in city.buildings]
for idx, f in enumerate(footprints):
    # Get the exterior ring of the polygon
    exterior_ring = list(f.exterior.coords)

    # Iterate over the coordinates of the exterior ring
    updated = False
    inserted_verts = []
    for i in range(len(exterior_ring) - 2):
        p1, p2, p3 = exterior_ring[i : i + 3]
        angle = abs(
            math.degrees(
                math.atan2(p3[1] - p2[1], p3[0] - p2[0])
                - math.atan2(p1[1] - p2[1], p1[0] - p2[0])
            )
        )
        if angle < 10:
            updated = True
            normal = (-p2[1] + p1[1], p2[0] - p1[0])
            normal_mag = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            normal = (normal[0] / normal_mag, normal[1] / normal_mag)
            if len(p2) == 2:
                new_pt = (p2[0] + (normal[0] * 1), p2[1] + (normal[1] * 1))
            else:
                new_pt = (p2[0] + (normal[0] * 1), p2[1] + (normal[1] * 1), 0)
            inserted_verts.append((i + 1, new_pt))
        # elif abs(angle - 180) < 3:
        #     exterior_ring.pop(i + 1)
        #     updated = True

    if updated:
        for ins_idx, pt in inserted_verts:
            exterior_ring.insert(ins_idx, pt)
        city.buildings[idx].footprint = Polygon(exterior_ring, f.interiors)
city.view()
sys.exit()
print(f"min clearance: {fp.minimum_clearance}")
# Assuming you have a list of vertices in the variable 'vertices'
vertices_array = np.array(fp.exterior.coords.xy).T

# Calculate the distance between each vertex to every other vertex
distances = np.sqrt(
    np.sum((vertices_array[:, np.newaxis] - vertices_array) ** 2, axis=-1)
)
indices = np.where((distances > 0) & (distances < 1))
indices = {tuple(sorted(idx.tolist())) for idx in indices}
print(indices)
for pt_pairs in indices:
    p1 = vertices_array[pt_pairs[0]]
    l1_1 = p1 - vertices_array[pt_pairs[0] - 1]
    l1_2 = p1 - vertices_array[pt_pairs[0] + 1]
    l1_1_normal = np.array([-l1_1[1], l1_1[0]])
    l1_1_normal /= np.linalg.norm(l1_1_normal)
    l1_2_normal = np.array([l1_2[1], -l1_2[0]])
    l1_2_normal /= np.linalg.norm(l1_2_normal)
    vertex1_normal = (l1_1_normal + l1_2_normal) / 2
    # print(l1_1_normal, l1_2_normal)
    print(vertex1_normal)
    p2 = vertices_array[pt_pairs[1]]
    l2_1 = p2 - vertices_array[pt_pairs[1] - 1]
    l2_2 = p2 - vertices_array[pt_pairs[1] + 1]
    l2_1_normal = np.array([-l2_1[1], l2_1[0]])
    l2_1_normal /= np.linalg.norm(l2_1_normal)
    l2_2_normal = np.array([l2_2[1], -l2_2[0]])
    l2_2_normal /= np.linalg.norm(l2_2_normal)
    vertex2_normal = (l2_1_normal + l2_2_normal) / 2
    print(vertex2_normal)
    new_vertex1 = p1 + (vertex1_normal * 1)
    vertices_array[pt_pairs[0]] = new_vertex1
    new_vertex2 = p2 + (vertex2_normal * 1)
    vertices_array[pt_pairs[1]] = new_vertex2
    new_fp = Polygon(vertices_array)
    city.buildings[0].footprint = new_fp

city.view()
