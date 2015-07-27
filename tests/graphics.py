import unittest
from app.graphics import Vertex, Edge, Face


class DataImportTestCase(unittest.TestCase):

    def test_stuff(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges)

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
        for edge in sorted(someedges):
            print(edge)


    def test_faces(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges)

        for fid in range(5):
            print("Face ", fid, '\n', faces[fid])

    def test_blockings(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges)

        face = faces[36]
        vertex = vertices[749]
        print("Vertex")
        print(vertex)
        print("Face")
        print(face.vertices)
        print("This face is blocking this vertex?", face.is_blocking(vertex))
        self.assertTrue(face.is_blocking(vertex))

    def test_bigblockingstest(self):
        from app.graphics import Vertex, Edge, Face

        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        faces = Face.load('../headmesh/NFaceEdges.txt', edges)
        for vertex in vertices.values():
            print(vertex.id, vertex.is_blocked(faces))
