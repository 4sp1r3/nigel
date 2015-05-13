"""
Primitives for modeling triangles
"""
import copy
import random
import numpy
from io import BytesIO
import matplotlib.pyplot as plt


# maximum boundary of the plane
MAXPOINT = 480


class Photo(object):
    """A 2D image
    """
    def __init__(self, file):
        """
        :param file: file like object to read from (BytesIO or an open filehandle)
        """
        # a numpy matrix [X, Y, 4] where X and Y are the width and height of the 'file'
        self.data = plt.imread(file)

    @property
    def shape(self):
        return self.data.shape

    @property
    def width(self):
        return self.data.shape[0]

    @property
    def height(self):
        return self.data.shape[1]

    def get_color(self, x, y):
        """Returns the 4 color values (RGBA) at position x,y"""
        return self.data[x, y]

    def is_white(self, x, y):
        """Returns a boolean - True if not perfectly white"""
        r, g, b, a = self.get_color(x, y)
        return r + g + b == 3.0

    def is_black(self, x, y):
        """Returns a boolean - True if not perfectly black"""
        r, g, b, a = self.get_color(x, y)
        return r + g + b == 0.0

    def save(self, filename):
        """Save to file
        :param filename: the filename to use. It will detect type from the filename extension
        """
        plt.imsave(filename, self.data)


class Point(object):
    """A point in 2D space"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "<Point [%s, %s]>" % (self.x, self.y)

    def add(self, x, y):
        self.x += x
        self.y += y


class Triangle(object):
    """
    Model of a 2D triangle
    """
    def __init__(self, p1, p2, p3):
        self.v1, self.v2, self.v3 = p1, p2, p3

    def __repr__(self):
        return "<Triangle %s %s %s>" % (self.v1, self.v2, self.v3)

    def photo(self, close=True):
        """return a Photo object of this triangle"""

        # plot an image
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.fill([self.v1.x, self.v2.x, self.v3.x], [self.v1.y, self.v2.y, self.v3.y], "black")

        # save it to a memory file and create a Photo from that
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        photo = Photo(buf)

        # if you want to plot it in notebook you have to leave it open (and consume memory)
        if close:
            buf.close()
            plt.close()
        return photo

    @staticmethod
    def move(triangle, vertex, x, y):
        """move vertex v by x, y units
        :param v: string of the vertex of the triangle (v1, v2, v3
        :param x: int to add to the x coordinate
        :param y: int to add to the y coordinate
        """
        #TODO: add a "protection" if vertex not in 1-3 then set to something inside 1-3
        #TODO: add protection to keep it inside some boundaries (eg 640 x 640)
        point = getattr(triangle, vertex)
        point.add(x, y)
        return triangle

    @staticmethod
    def random_vertex():
        """
        pick a vertex at random
        :return: string
        """
        return "v%s" % random.randint(1, 3)

    @staticmethod
    def getx(triangle, vertex):
        """return the value of x of the given vertex"""
        vert = getattr(triangle, "v%s" % vertex)
        return vert.x

    @staticmethod
    def gety(triangle, vertex):
        """return the value of x of the given vertex"""
        vert = getattr(triangle, "v%s" % vertex)
        return vert.y

        # @property
    # def model(self):
    #     """returns the coordinates of the points in the triangle as a numpy array"""
    #     return numpy.array([
    #         [self.x1, self.y1],
    #         [self.x2, self.y2],
    #         [self.x3, self.x3]
    #     ])
    #
    # def clone(self):
    #     """return a copy of this"""
    #     return copy.deepcopy(self)
    #
    # @staticmethod
    # def distance(triA, triB):
    #     """Return the distance between the two triangles"""
    #     # for every vertex accumulate the distance between the corresponding points
    #     total = 0.0
    #     for p1, p2 in zip(triA.model, triB.model):
    #         total += numpy.linalg.norm(p1 - p2)
    #     return total


# a known triangle
REF_TRIANGLE = Triangle(Point(0, 0), Point(100, 0), Point(100, 0))


class RandomPoint(Point):
    """A randomly generated point in space"""
    def __init__(self):
        super(RandomPoint, self).__init__(*[random.randrange(0, MAXPOINT) for _ in range(2)])


class RandomTriangle(Triangle):
    """A randomly generated triangle"""
    def __init__(self):
        super(RandomTriangle, self).__init__(RandomPoint(), RandomPoint(), RandomPoint())
