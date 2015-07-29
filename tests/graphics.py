import unittest
import random
from app.graphics import Vertex, Edge, Face


class DataImportTestCase(unittest.TestCase):
    """
    Test the importing of head mesh data
    """
    def test_import(self):
        """just demonstrate loading of the mesh from text files"""
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges, vertices)
        self.assertTrue(len(vertices))
        self.assertTrue(len(edges))
        self.assertTrue(len(faces))

        face = faces[36]
        vertex = vertices[749]
        print("Vertex", vertex)
        print("Face:\n", face.vertices)
        print("This face is blocking this vertex?", face.is_blocking(vertex))
        for fid in range(5):
            print("Face", fid, '\n', faces[fid])

    def test_face_order_of_vertices(self):
        """ensure a face is a path of sequential edges that end back where it started"""
        A = Vertex('A', -4., 4., 0)
        B = Vertex('B', 4., 4., 0)
        C = Vertex('C', 4., -4., 0)
        D = Vertex('D', -4., -4., 0)
        e1 = Edge(1, A, B)
        e2 = Edge(2, B, C)
        e3 = Edge(3, C, D)
        e4 = Edge(4, D, A)
        valid_paths = [
            [A, B, C, D], [B, C, D, A], [C, D, A, B], [D, A, B, C],
            [A, D, C, B], [D, C, B, A], [C, B, A, D], [B, A, D, C]
        ]
        edges = [e4, e1, e3, e2]
        for _ in range(50):
            random.shuffle(edges)
            face = Face(1, edges)
            print([e.id for e in edges], "=>", [v.id for v in face.vertices])
            self.assertTrue(face.vertices in valid_paths)


class VertexBlockingTestCase(unittest.TestCase):
    """
    Tests routines involved in detection of a face blocking a vertex
    """
    def setUp(self):
        self.vertices = Vertex.load('../headmesh/NVertices.txt')
        self.edges = Edge.load('../headmesh/NEdgeVertices.txt', self.vertices)
        self.faces = Face.load('../headmesh/NFaceEdges.txt', self.edges, self.vertices)

    def test_stuff(self):
        """just play around here"""
        face = self.faces[36]
        print("Face")
        print(face.vertices)

        for i in range(740, 760):
            vertex = self.vertices[i]
            print("Vertex", vertex.id)
            print("This face is blocking this vertex?", face.is_blocking(vertex))

    def test_own_vertex_does_not_block(self):
        """asking a face if it is blocked by one of it's own vertices should return 'no'"""
        face = self.faces[36]
        v0 = face.vertices[0]
        print(face)
        print("v0", v0, face.is_blocking(v0))
        self.assertFalse(face.is_blocking(v0))

        v1 = Vertex(1, -1.701380038, -1.005879965, 12.89350033)
        print('v1', v1, face.is_blocking(v1))

    def test_is_behind(self):
        """test that a vertex behind a face, or not, can be detected"""
        face = self.faces[36]
        vertex = self.vertices[749]
        print("Face\n", face, '\n')
        self.assertTrue(face.is_behind(vertex))

        v1 = Vertex(1, -4., -4., 0)
        v2 = Vertex(2, 4., -4., 0)
        v3 = Vertex(3, -4., 4., 0)
        v4 = Vertex(4, 4., 4., 0)

        edges = [Edge(1, v1, v2), Edge(2, v2, v3), Edge(3, v3, v4), Edge(4, v4, v1)]
        face = Face(0, edges)

        v1 = Vertex(1, 0, 3.99, -0.1)
        self.assertTrue(face.is_behind(v1))
        print(v1.y, face.is_behind(v1), '\n')

        v1 = Vertex(1, 0, 4.00, -0.0)
        self.assertFalse(face.is_behind(v1))
        print(v1.y, face.is_behind(v1), '\n')

        v1 = Vertex(1, 0, 4.01, .1)
        self.assertFalse(face.is_behind(v1))
        print(v1.y, face.is_behind(v1), '\n')

        v1 = Vertex(1, 0, 4.10, -0.1)
        self.assertTrue(face.is_behind(v1))
        print(v1.y, face.is_behind(v1), '\n')

    def test_is_inside(self):
        """test detection that a vertex is inside the boundaries of a face (ignorning the z-plane)
        aka (orthagonal view)
        """
        v1 = Vertex(1, -4., -4., 0)
        v2 = Vertex(2, 4., -4., 0)
        v3 = Vertex(3, -4., 4., 0)
        v4 = Vertex(4, 4., 4., 0)

        edges = [Edge(1, v1,v2), Edge(2, v2, v3), Edge(3, v3,v4), Edge(4, v4, v1)]
        face = Face(0, edges)

        v1 = Vertex(1, 0, 3.9, -0.1)
        self.assertTrue(face.is_inside(v1))
        print(v1.y, face.is_inside(v1), '\n')

        v1 = Vertex(1, 0, 3.99, -0.1)
        self.assertTrue(face.is_inside(v1))
        print(v1.y, face.is_inside(v1), '\n')

        v1 = Vertex(1, 0, 4.00, -0.0)
        self.assertFalse(face.is_inside(v1))
        print(v1.y, face.is_inside(v1), '\n')

        v1 = Vertex(1, 0, 4.01, .1)
        self.assertTrue(face.is_inside(v1))
        print(v1.y, face.is_inside(v1), '\n')

        v1 = Vertex(1, 0, 4.10, -0.1)
        self.assertFalse(face.is_inside(v1))
        print(v1.y, face.is_inside(v1), '\n')

    def test_vertex_behind_the_plane_or_some_such(self):
        face = self.faces[36]
        vertex = self.vertices[749]
        print("Face\n", face, '\n')
        print("Vertex", vertex, face.is_blocking(vertex))
        self.assertTrue(face.is_blocking(vertex))

        for z in range(5, 15):
            vertex.z = z
            print("Vertex", vertex, face.is_blocking(vertex))

        self.assertFalse(face.is_blocking(vertex))


class EdgeOcclusionTestCase(unittest.TestCase):
    """
    * detect edges which are fully/partially hidden by faces, and
    """
    def test_edge_occlusion(self):
        """move an edge from one side of a face, behind it, and out the other side
        Should start not hidden, become hidden, then reappear
        """
        result = False
        self.assertTrue(result)

    def test_edge_non_occlusion(self):
        """move an edge from one side of a face, in front of it, and out the other side
        Should never be hidden
        """
        result = False
        self.assertTrue(result)


class FaceOcclusionTestCase(unittest.TestCase):
    """
    Detect faces which are fully/partally hidden by faces
    """
    def test_face_occlusion(self):
        """move a triangle across and behind a square"""
        result = False
        self.assertTrue(result)

    def test_face_occlusion(self):
        """move a big square across and behind a tiny triangle
        When encased, the little triangle does not hide the big square;
        leave it to other faces to hide the edges of the square: Nige 29Jul15
        """
        result = False
        self.assertTrue(result)

    def test_face_non_occlusion(self):
        """move a triangle across in front of a square"""
        result = False
        self.assertTrue(result)
