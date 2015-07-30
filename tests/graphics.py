import unittest
import random
import collections
from app.graphics import Vertex, Edge, Face, ACCURACY


A = Vertex('A', -4., 4., 0)
B = Vertex('B', 4., 4., 0)
C = Vertex('C', 4., -4., 0)
D = Vertex('D', -4., -4., 0)
AB = Edge('AB', A, B)
BC = Edge('BC', B, C)
CD = Edge('CD', C, D)
DA = Edge('DA', D, A)
AC = Edge('AC', A, C)
CA = Edge('CA', C, A)
CB = Edge('CB', C, B)


class DataImportTestCase(unittest.TestCase):
    """
    Test the importing of head mesh data
    """
    def test_import(self):
        """just demonstrate loading of the mesh from text files"""
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges)
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

    def test_edges_sort(self):
        """ensure that the sorting of edges results in tail-tip-tail-tip path"""
        # this is not a valid path
        circle_path = [AB, BC, DA, CD]
        self.assertFalse(Face.is_face(circle_path))

        # but after sorting it is a valid path
        sorted_path = Edge.sort(circle_path)
        print([e.id for e in circle_path], [e.id for e in sorted_path])
        self.assertTrue(Face.is_face(sorted_path))

        # this is not a valid path and one of the edges is backward
        triangle_path = [AB, CA, CB]
        self.assertFalse(Face.is_face(triangle_path))

        # but after sorting it is a valid path
        sorted_path = Edge.sort(triangle_path)
        print([e.id for e in triangle_path], [e.id for e in sorted_path])
        self.assertTrue(Face.is_face(sorted_path))

    def test_face_order_of_vertices(self):
        """ensure a face is a path of sequential edges that end back where it started"""
        valid_paths = [
            [A, B, C, D], [B, C, D, A], [C, D, A, B], [D, A, B, C],
            [A, D, C, B], [D, C, B, A], [C, B, A, D], [B, A, D, C]
        ]
        edges = [AB, BC, CD, DA]
        for _ in range(50):
            random.shuffle(edges)
            face = Face(1, edges)
            print([e.id for e in edges], "=>", [v.id for v in face.vertices])
            self.assertTrue(face.vertices in valid_paths)


class EdgeAndFaceTestCase(unittest.TestCase):
    """Test the minor edges and faces routines"""
    def test_is_face(self):
        """ensure these paths are, and are not, paths no matter what point in the sequence
        they are presented"""
        square = collections.deque([AB, BC, CD, DA])
        for _ in range(len(square)):
            self.assertTrue(Face.is_face(square))
            square.rotate(1)
        square = collections.deque([AB, AC, CD, DA])
        for _ in range(len(square)):
            self.assertFalse(Face.is_face(square))
            square.rotate(1)

        triangle = collections.deque([AB, CA, BC])
        for _ in range(len(triangle)):
            self.assertFalse(Face.is_face(triangle))
            square.rotate(1)
        triangle = collections.deque([BC, CA, AB])
        for _ in range(len(triangle)):
            self.assertTrue(Face.is_face(triangle))
            square.rotate(1)


class VertexBlockingTestCase(unittest.TestCase):
    """
    Tests routines involved in detection of a face blocking a vertex
    """
    def setUp(self):
        self.vertices = Vertex.load('../headmesh/NVertices.txt')
        self.edges = Edge.load('../headmesh/NEdgeVertices.txt', self.vertices)
        self.faces = Face.load('../headmesh/NFaceEdges.txt', self.edges)

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
        print("Vertex %s %s blocking is %s" % (vertex.id, vertex, face.is_blocking(vertex)))

        # Nige says never mind, it was just one combo he knew about 30/6/15
        #self.assertTrue(face.is_blocking(vertex))

        for z in range(5, 15):
            vertex.z = z
            print("Vertex", vertex, face.is_blocking(vertex))



class EdgeOcclusionTestCase(unittest.TestCase):
    """
    * detect edges which are fully/partially hidden by faces, and
    """
    def test_edge_occlusion(self):
        """move an overlapping edge from one side of a face, behind it, and out the other side
        Should start not hidden, become hidden, then reappear
        """
        # make a face and an edge
        face = Face('square', [AB, BC, CD, DA])
        print(face)
        for x in range(-10, 10):
            J, K = Vertex('J', x, 0, -10), Vertex('K', x, 8, -10)
            JK = Edge('JK', J, K)
            print(JK, face.is_blocking(JK))
            if x in range(-3, 4):
                self.assertTrue(face.is_blocking(JK))
            else:
                self.assertFalse(face.is_blocking(JK))

    def test_edge_non_occlusion(self):
        """move an overlapping edge from one side of a face, in front of it, and out the other side
        Should never be hidden
        """
        # make a face and an edge
        face = Face('square', [AB, BC, CD, DA])
        print(face)
        for x in range(-10, 10):
            J, K = Vertex('J', x, 0, 10), Vertex('K', x, 8, 10)
            JK = Edge('JK', J, K)
            print(JK, face.is_blocking(JK))
            self.assertFalse(face.is_blocking(JK))

    def test_edge_momentary_occlusion(self):
        """move a small edge from one side of a face, totally behind it, and out the other side
        Should be not hidden, hidden, not hidden
        """
        # make a face and an edge
        face = Face('square', [AB, BC, CD, DA])
        print(face)
        for x in range(-8, 9):
            J, K = Vertex('J', x, 2, -10), Vertex('K', x, -2, -10)
            JK = Edge('JK', J, K)
            print(JK, face.is_inside(J), face.is_inside(K))
            if abs(x) - abs(A.x) > ACCURACY:
                if abs(x) < abs(A.x):
                    self.assertTrue(face.is_blocking(JK))
                else:
                    self.assertFalse(face.is_blocking(JK))
        print()
        for y in range(-8, 9):
            y += 0.5
            J, K = Vertex('J', -1, y, -10), Vertex('K', -1, y, -10)
            JK = Edge('JK', J, K)
            print(JK, face.is_inside(J), face.is_inside(K))
            if abs(y) < abs(A.y):
                self.assertTrue(face.is_blocking(JK))
            else:
                self.assertFalse(face.is_blocking(JK))

    def test_edge_occlusion_precision(self):
        """move a small edge from one side of a face, behind the face, focusing on
        the exact moment when it becomes hidden, and how precise that needs to be.
        """
        # make a face and an edge
        face = Face('square', [AB, BC, CD, DA])
        print(face)
        for d in range(20):
            x = 3.9 + d/100.
            J, K = Vertex('J', x, 0.5, -10), Vertex('K', x, 0.5, -10)
            JK = Edge('JK', J, K)
            print(J, K, face.is_inside(J), face.is_inside(K))
            if abs(x) - abs(A.x) > ACCURACY:
                if abs(x) < abs(A.x):
                    self.assertTrue(face.is_blocking(JK))
                else:
                    self.assertFalse(face.is_blocking(JK))


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
