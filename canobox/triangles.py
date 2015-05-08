"""
Primitives for modeling triangles
"""
import copy
import random
import numpy
from matplotlib import pyplot


class Triangle(object):
    """It's a triangle (2D)"""
    def __init__(self, x1, y1, x2, y2, x3, y3):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3

    @property
    def photo(self):
        """return a numpy array corresponding to a 2d photo of this triangle"""
        x_coords = [self.x1, self.x2, self.x3]
        y_coords = [self.y1, self.y2, self.y3]
        # draw the triangle
        fig = pyplot.figure()
        fig.add_subplot(111)
        pyplot.fill(x_coords, y_coords, 'black')
        fig.canvas.draw()
        # convert it to a numpy array
        w, h = fig.canvas.get_width_height()
        buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
        buf.shape = (w, h, 4)
        # roll it from ARBG to RGBA
        buf = numpy.roll(buf, 3, axis=2)
        return buf

    @property
    def model(self):
        """returns the coordinates of the points in the triangle as a numpy array"""
        return numpy.array([
            [self.x1, self.y1],
            [self.x2, self.y2],
            [self.x3, self.x3]
        ])

    def clone(self):
        """return a copy of this"""
        return copy.deepcopy(self)


class RandomTriangle(Triangle):
    """A randomly generated triangle"""
    def __init__(self):
        super(RandomTriangle, self).__init__(
            [random.randrange(50, 200) for x in range(6)]
        )


class Photo(object):
    """does stuff to a photo"""
    def __init__(self, arr):
        self.arr = arr

    def pixel_at(self, x, y):
        """Returns a boolean - False if white, True if black"""
        return self.arr[x, y, 1] == 255

    def width(self):
        return self.arr.shape[0]

    def height(self):
        return self.arr.shape[1]
