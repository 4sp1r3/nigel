import math
import warnings
import numpy as np


NUMBER_OF_RECTANGLES = 100


def f(A, B, V, t):
    PQx = V.x - (A.x + ((B.x - A.x) * t))
    PQy = V.y - (A.y + ((B.y - A.y) * t))
    PQz = 0
    PQ = [PQx, PQy, PQz]
    AB = [
        B.x - A.x,
        B.y - A.y,
        B.z - A.z
    ]
    magnitudePQ = math.sqrt(PQx ** 2.0 + PQy ** 2.0 + PQz ** 2.0)
    forceMagnitude = 1 / magnitudePQ
    forceDirection = np.cross(PQ, [0, 0, 1]) / magnitudePQ
    forceVector = forceMagnitude * forceDirection
    return np.dot(forceVector, AB)


def integral(A, B, V):
    """Do the line integral"""
    numberofRectangles = NUMBER_OF_RECTANGLES
    startingt = 0.0
    endingt = 1.0
    width = (endingt - startingt) / numberofRectangles
    runningSum = 0.0
    for i in range(numberofRectangles):
        height = f(A, B, V, startingt + i * width)
        area = height * width
        runningSum += area
    return runningSum


class Vertex(object):
    """The three dimensional coordinates of a vertex"""
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str([self.x, self.y, self.z])

    def __eq__(self, other):
        return self.id == other.id

    def is_blocked(self, faces):
        """True when this vertex is blocked from view by faces"""
        for face in faces.values():
            if face.is_blocking(self):
                return True
        return False

    @staticmethod
    def load(filename):
        # vertices (vid, x, y, z)
        np_vertices = np.loadtxt(filename, delimiter="\t", skiprows=1,
                                 dtype=[('id', 'i4'), ('x', 'f8'), ('y', 'f8'), ('z', 'f8')])
        vertices = {}
        for id, x, y, z in np_vertices:
            vertices[id] = Vertex(id, x, y, z)
        return vertices


class Edge(object):
    """The vertex ID's of two vertices"""
    def __init__(self, id, v1, v2):
        self.id = id
        self.v1 = v1
        self.v2 = v2

    def __repr__(self):
        return str([self.v1, self.v2])

    def __iter__(self):
        return iter([self.v1, self.v2])

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def load(filename, vertices):
        # edge vertices (eid, vid, vid)
        np_edges = np.loadtxt(filename, delimiter="\t", skiprows=1, dtype="i4,i4,i4")

        edges = {}
        for id, v1, v2 in np_edges:
            edges[id] = Edge(id, vertices[v1], vertices[v2])
        return edges


class Face(object):
    def __init__(self, id, vertices):
        """The vertices must be provided in the order of the path they follow;
                like tracing each edge of the face"""
        self.id = id
        self.vertices = vertices

    def __str__(self):
        return "\n".join(map(str, self.vertices))

    def is_blocking(self, vertex):
        """True if the vertex is blocked by this face

        Accumulate the integral of each edge in this face with the vertex. If the total is
        zero, then the vertex is visible.
        """
        try:
            sum = 0.0
            for idx in range(len(self.vertices)):
                sum += integral(self.vertices[idx], self.vertices[idx-1], vertex)
            # if greater than the margin of error
            return abs(sum) > 1 / NUMBER_OF_RECTANGLES
        except ZeroDivisionError:
            return False

    @staticmethod
    def load(filename, edges, vertices):

        # get the edges of the face (fid, eid, eid, eid, eid)
        # if the last edge is null indicate with a -1 edge id
        convertfunc = lambda x: -1 if x == b'NULL' else x
        np_faceedges = np.loadtxt(filename, delimiter="\t", skiprows=1,
                                  converters={4: convertfunc},
                                  dtype=[('id', 'i4'), ('edge1', 'i4'), ('edge2', 'i4'), ('edge3', 'i4'), ('edge4', 'i4')])

        # for every face
        faces = {}
        # get the edges
        for id, *edgeids in np_faceedges:
            # assemble the vertices as a path around the edges of the face
            # by putting all the edges in a list and picking a start vertex
            # then find a cojoining edge, append the opposite vertex, and removing the edge,
            # until all the edges have been used.
            try:
                face_edges = [edges[id] for id in edgeids if id >= 0]
                face_path = [face_edges[0].v1]
                face_edges.pop(0)
                while len(face_edges):
                    for idx, edge in enumerate(face_edges):
                        if edge.v1 == face_path[-1]:
                            face_path.append(edge.v2)
                            face_edges.pop(idx)
                            break
                        elif edge.v2 == face_path[-1]:
                            face_path.append(edge.v1)
                            face_edges.pop(idx)
                            break
                faces[id] = Face(id, face_path)
            except KeyError:
                # warnings.warn("Face %s discarded because not all these edges are known (%s, %s, %s, %s)." % (id, eid1, eid2, eid3, eid4))
                pass
        return faces
