import os
import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab as maymlab


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class Head(object):
    """
    3D representation of a head
    """
    def __init__(self, filename):
        """
        param filename: path to a tsv file containing an index and the x,y,z
            coords for 1024 vertices of the head
            eg: 993	2.908586979	1.991146803	10.45521641
        """
        self.filename = filename
        self.vertices = np.loadtxt(open(filename, "rb"), delimiter="\t", skiprows=1, usecols=(1, 2, 3))
        self.x, self.y, self.z = self.vertices[:, 0], self.vertices[:, 1], self.vertices[:, 2]

    def plot(self, color=(1.0, 1.0, 1.0)):
        """
        Open a window and show the head
        param color: 3 floats betwen 0 and 1 where 1,1,1 is white.
        """
        maymlab.points3d(self.x, self.y, self.z, scale_factor=0.5, color=color)

    def move(self, x, y, z):
        """
        Shift the position of the head by [x, y, z]
        """
        self.vertices = self.vertices * [x, y, z]

    def distance(self, other):
        """
        Compares this head with the other returning an accumulation of the distances between all the
        corresponding vertices.
        param other: another head instance
        return: a float
        """
        # for every vertex accumulate the distance between the corresponding points
        total = 0.0
        for p1, p2 in zip(self.vertices, other.vertices):
            total += np.linalg.norm(p1 - p2)
        return total


HEADS_DIR = 'heads'
HEAD = {
    'alfred': Head(os.path.join(BASE_PATH, HEADS_DIR, "AlfredVertices.csv")),
    'bob': Head(os.path.join(BASE_PATH, HEADS_DIR, "BobVertices.csv"))
}


class Photo(object):
    """
    2D photo of a head (hopefully:) and manipulate it as a matrix
    """
    def __init__(self, filename):
        """
        Import the image and store it as a 2D plane/matrix.
        param filename: absolute path to an image file
        """
        self.filename = filename
        self.A = plt.imread(self.filename)

    @property
    def shape(self):
        return self.A.shape

    def plot(self):
        plt.imshow(self.A)
        plt.show()


MUGS_DIR = 'mugshots'
PHOTO = {
    "nigel": Photo(os.path.join(BASE_PATH, MUGS_DIR, "nigel.bmp")),
    "mannequin": Photo(os.path.join(BASE_PATH, MUGS_DIR, "mannequin.bmp")),
    "zimmerman": Photo(os.path.join(BASE_PATH, MUGS_DIR, "zimmerman.jpg"))
}
