import unittest
from app.graphics import Vertex, Edge, Face


class FaceBlockingTestCase(unittest.TestCase):
    def setUp(self):
        self.vertices = Vertex.load('../headmesh/NVertices.txt')
        self.edges = Edge.load('../headmesh/NEdgeVertices.txt', self.vertices)
        self.faces = Face.load('../headmesh/NFaceEdges.txt', self.edges, self.vertices)

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
        face = self.faces[36]
        vertex = self.vertices[749]
        print("Face\n", face, '\n')
        #print("Vertex", vertex, "is behind:", face.is_behind(vertex))
        self.assertTrue(face.is_behind(vertex))

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


class DataImportTestCase(unittest.TestCase):
    def test_stuff(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges, vertices)

        face = faces[36]
        vertex = vertices[749]
        print("Vertex")
        print(vertex)
        print("Face")
        print(face.vertices)
        print("This face is blocking this vertex?")
        print(face.is_blocking(vertex))

    def test_edges(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        someedges = list(edges.values())[:5]
        for edge in someedges:
            print(edge)

    def test_faces(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges, vertices)

        for fid in range(5):
            print("Face", fid, '\n', faces[fid])

    def test_blockings(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges, vertices)

        face = faces[36]
        vertex = vertices[749]
        print("Vertex")
        print(vertex)
        print("Face")
        print(face.vertices)
        print("This face is blocking this vertex?", face.is_blocking(vertex))
        self.assertTrue(face.is_blocking(vertex))
