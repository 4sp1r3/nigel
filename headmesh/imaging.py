import matplotlib.pyplot as plt


class TwoDimensionalImage(object):
    """
    Represents a two dimensional image, and operations on it.
    """
    def __init__(self, filename):
        """
        Import the image and store it as a 2D plane/matrix.
        param filename: relative path to an image file
        """
        self.A = plt.imread(filename)

    @property
    def shape(self):
        return self.A.shape
