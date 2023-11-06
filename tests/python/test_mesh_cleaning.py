import unittest
import numpy as np
from dtcc_model.geometry.mesh import Mesh
import dtcc_wrangler


class TestClean(unittest.TestCase):
    def test_clean_no_duplicates(self):
        # Create a test mesh with duplicate vertices
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        faces = np.array([[0, 1, 2], [0, 2, 3]])

        mesh = Mesh(vertices=vertices, faces=faces)
        clean_mesh = mesh.clean()
        self.assertEqual(len(clean_mesh.vertices), len(mesh.vertices))
        self.assertEqual(len(clean_mesh.faces), len(mesh.faces))
        self.assertTrue(np.all(clean_mesh.vertices == mesh.vertices))
        self.assertTrue(np.all(clean_mesh.faces == mesh.faces))

    def test_clean_with_duplicates(self):
        # Create a test mesh with duplicate vertices
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 0]])
        faces = np.array([[0, 1, 2], [3, 2, 4]])
        mesh = Mesh(vertices=vertices, faces=faces)
        clean_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        clean_faces = np.array([[0, 1, 2], [0, 2, 3]])
        mesh = Mesh(vertices=vertices, faces=faces)
        clean_mesh = mesh.clean()
        print(clean_mesh.vertices)
        self.assertEqual(len(clean_mesh.vertices), len(mesh.vertices) - 1)
        self.assertEqual(len(clean_mesh.faces), len(mesh.faces))
        self.assertTrue(np.all(mesh.vertices == vertices))
        self.assertTrue(np.all(clean_mesh.vertices == clean_vertices))
        self.assertTrue(np.all(clean_mesh.faces == clean_faces))

    def test_clean_with_duplicate_faces(self):
        # Create a test mesh with duplicate vertices
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 0]])
        faces = np.array([[0, 1, 2], [3, 2, 4], [0, 1, 2]])
        mesh = Mesh(vertices=vertices, faces=faces)
        mesh.markers = np.array([1, 2, 1])
        mesh.normals = np.array([[0, 0, 1], [0, 0, 1], [0, 0, -1]])
        clean_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        clean_faces = np.array([[0, 1, 2], [0, 2, 3]])
        clean_markers = np.array([1, 2])
        clean_normals = np.array([[0, 0, 1], [0, 0, 1]])

        clean_mesh = mesh.clean()
        self.assertTrue(np.all(clean_mesh.faces == clean_faces))
        self.assertTrue(np.all(clean_mesh.markers == clean_markers))
        self.assertTrue(np.all(clean_mesh.normals == clean_normals))


if __name__ == "__main__":
    unittest.main()
