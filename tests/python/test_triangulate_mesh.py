import unittest
import dtcc_wrangler
from dtcc_model import Mesh
import numpy as np
from numpy.testing import assert_array_equal


class TestTriangulate(unittest.TestCase):
    def test_no_triangles(self):
        # Test case where the mesh is already triangulated
        mesh = Mesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]),
            faces=np.array([[0, 1, 2], [0, 2, 3]]),
        )
        triangulated_mesh = mesh.triangulate()
        assert_array_equal(triangulated_mesh.vertices, mesh.vertices)
        assert_array_equal(triangulated_mesh.faces, mesh.faces)

    def test_triangles(self):
        # Test case where the mesh needs to be triangulated
        mesh = Mesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]),
            faces=np.array([[0, 1, 2, 3]]),
        )
        triangulated_mesh = mesh.triangulate()
        assert_array_equal(triangulated_mesh.vertices, mesh.vertices)
        assert_array_equal(triangulated_mesh.faces, np.array([[0, 1, 2], [0, 2, 3]]))

    def test_empty_mesh(self):
        # Test case where the mesh is empty
        mesh = Mesh(vertices=np.array([]), faces=np.array([]))
        triangulated_mesh = mesh.triangulate()
        assert_array_equal(triangulated_mesh.vertices, [])
        assert_array_equal(triangulated_mesh.faces, [])


if __name__ == "__main__":
    unittest.main()
