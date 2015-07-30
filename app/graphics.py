import math
import numpy as np

ACCURACY = 0.04
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
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return str([self.x, self.y, self.z])

    def __eq__(self, other):
        return self.id == other.id

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    def is_blocked(self, faces):
        """True when this vertex is blocked from view by faces"""
        for face in faces.values():
            if face.is_blocking(self):
                return True
        return False

    @staticmethod
    def load(filename):
        # vertices (vid, x, y, z)
        np_vertices = np.loadtxt(
            filename, delimiter="\t", skiprows=1,
            dtype=[('id', 'i4'), ('x', 'f8'), ('y', 'f8'), ('z', 'f8')]
        )
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

    def __lt__(self, other):
        if self.v2 == other.v1:
            return True
        if self.v1 == other.v2:
            return False
        return Exception('Edges are neither less than, nor greater than')

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def sort(edges):
        """return the list of edges in tip-to-tail order, flipping an edge end-for-end
        if necessary"""
        edgestack = edges.copy()
        path = [edgestack[0]]
        edgestack.pop(0)
        while len(edgestack):
            for idx, edge in enumerate(edgestack):
                if path[-1].v2 == edge.v1:
                    path.append(edge)
                    edgestack.pop(idx)
                    break
                elif path[-1].v2 == edge.v2:
                    # flip this edge around
                    path.append(Edge('-' + str(edge.id), edge.v2, edge.v1))
                    edgestack.pop(idx)
                    break
            else:
                raise Exception("These edges do not form a path: %s" % edges)
        return path

    @staticmethod
    def load(filename, vertices):
        # edge vertices (eid, vid, vid)
        np_edges = np.loadtxt(filename, delimiter="\t", skiprows=1, dtype="i4,i4,i4")

        edges = {}
        for id, v1, v2 in np_edges:
            edges[id] = Edge(id, vertices[v1], vertices[v2])
        return edges


class Face(object):
    def __init__(self, id, edges):
        """Although they may be presented out of order, the list of edges must ultimately
         form a contiguous circular path through each vertex"""
        self.id = id
        self.edges = Edge.sort(edges)
        self.vertices = [e.v1 for e in self.edges]
        assert(Face.is_face(self.edges))

    def __str__(self):
        return "\n".join(map(str, self.vertices))

    def is_behind(self, vertex):
        """True if the vertex is behind the plane of this face
        """
        # ok to use three vertices of the plane (Nige:28/7/15)
        V = vertex.to_array()
        A, B, C = [self.vertices[i].to_array() for i in [0, 1, 2]]
        AB = B - A
        AC = C - A
        ABxAC = np.cross(AB, AC)
        result = (((A[0] - V[0]) * (ABxAC[0]) + (A[1] - V[1]) * (ABxAC[1])) / (ABxAC[2])) + (A[2] - V[2])
        return result > 0

    def is_inside(self, vertex):
        """True if the vertex is blocked by this face

        Accumulate the integral of each edge in this face with the vertex. If the total is
        zero, then the vertex is visible.
        """
        try:
            total = 0.0
            for idx in range(len(self.vertices)):
                tegral = integral(self.vertices[idx - 1], self.vertices[idx], vertex)
                total += tegral
            result = abs(total) > ACCURACY
            return result
        except ZeroDivisionError:
            return False

    def is_blocking(self, obj):
        """True when in line and is behind; whatever they mean"""
        if isinstance(obj, Vertex):
            return self.is_inside(obj) and self.is_behind(obj)
        if isinstance(obj, Edge):
            return self.is_blocking(obj.v1) or self.is_blocking(obj.v2)
        return NotImplementedError()

    @staticmethod
    def is_face(edges):
        """True if the edges describe the closed face of a contiguous path through the
        vertices"""
        start_vertex = edges[0].v1
        current_vertex = start_vertex
        for edge in edges:
            if current_vertex == edge.v1:
                current_vertex = edge.v2
            else:
                return False
        return current_vertex == start_vertex

    @staticmethod
    def load(filename, edges):
        # get the edges of the face (fid, eid, eid, eid, eid)
        # if the last edge is null indicate with a -1 edge id
        convertfunc = lambda x: -1 if x == b'NULL' else x
        np_faceedges = np.loadtxt(
            filename, delimiter="\t", skiprows=1, converters={4: convertfunc},
            dtype=[('id', 'i4'), ('edge1', 'i4'), ('edge2', 'i4'), ('edge3', 'i4'), ('edge4', 'i4')]
        )
        # for every face
        faces = {}
        # get the edges
        for id, *edgeids in np_faceedges:
            try:
                face_edges = [edges[id] for id in edgeids if id >= 0]
                faces[id] = Face(id, face_edges)
            except KeyError:
                pass
                #print("Face %s discarded because not all these edges are known (%s)." % (id, edgeids))
        return faces
