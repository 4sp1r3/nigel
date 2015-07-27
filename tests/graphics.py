import unittest
from app.graphics import Vertex, Edge, Face


class DataImportTestCase(unittest.TestCase):

    def test_data_importing(self):
        vertices = Vertex.load('../headmesh/NVertices.txt')
        edges = Edge.load('../headmesh/NEdgeVertices.txt', vertices)
        print(edges[0])

        faces = Face.load('../headmesh/NFaceEdges.txt', edges)
        print(faces[0])

        face = faces[0]
        vertex = vertices[400]
        print(face.is_blocking(vertex))

        for vertex in vertices.values():
            blocked = vertex.is_blocked(faces)
            if not blocked:
                print(vertex, blocked)
