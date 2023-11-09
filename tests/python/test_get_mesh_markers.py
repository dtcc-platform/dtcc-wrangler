import unittest
from dtcc_model.geometry.mesh import Mesh
import dtcc_wrangler


# class TestGetMarkers(unittest.TestCase):
#     def setUp(self):
#         # Create a test mesh
#         vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
#         faces = [[0, 1, 2], [0, 2, 3]]
#         markers = [0, 1]
#         self.mesh1 = Mesh(vertices=vertices, faces=faces, markers=markers)

#     def test_get_markers(self):
#         # Test filtering by markers
#         filtered_mesh = self.mesh1.get_markers(markers=[0])
#         self.assertEqual(len(filtered_mesh.faces), 1)
#         self.assertEqual(filtered_mesh.markers[0], 0)

#         # Test inverting the filter
#         filtered_mesh = self.mesh1.get_markers(
#             self.mesh, markers=[0], invert_filter=True
#         )
#         self.assertEqual(len(filtered_mesh.faces), 1)
#         self.assertEqual(filtered_mesh.markers[0], 1)

#         # Test filtering by threshold
#         filtered_mesh = self.mesh1.get_markers(self.mesh, threshold=0)
#         self.assertEqual(len(filtered_mesh.faces), 2)
#         self.assertEqual(filtered_mesh.markers[0], 1)
#         self.assertEqual(filtered_mesh.markers[1], 0)

#         # Test inverting the filter by threshold
#         filtered_mesh = self.mesh1.get_markers(self.mesh, threshold=1)
#         self.assertEqual(len(filtered_mesh.faces), 1)
#         self.assertEqual(filtered_mesh.markers[0], 1)
