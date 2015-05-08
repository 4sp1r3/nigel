import unittest
import imaging


class TestImaging(unittest.TestCase):
    def test_init(self):
        # load and test the dimensions of the headmash
        fname = 'HeadMash.0004.bmp'
        im = imaging.TwoDimensionalImage(fname)
        print(fname, im.shape)
        self.assertEqual(im.shape, (256, 256, 4))

        # check the dimensions of miss foo jpg
        fname = 'Miss.Foo.jpg'
        im = imaging.TwoDimensionalImage(fname)
        print(fname, im.shape)
        self.assertEqual(im.shape, (4615, 3283, 3))
