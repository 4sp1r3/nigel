import unittest
import operator
import math
from deap import creator
from deap import base
from deap.gp import PrimitiveTree, PrimitiveSetTyped, Terminal


from pythagoras import Point
from custom import ourGrow, DeadBranchError


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", PrimitiveTree, fitness=creator.FitnessMin)


def get_pset():
    """
    :return: the typed set of primitive operations
    """
    # We're asking for a program that consumes a point and returns a distance (float)
    pset = PrimitiveSetTyped(
        "MAIN",
        [Point],
        float
    )

    # a couple of functions that return the x, and y, values of a point
    pset.addPrimitive(Point.getx, [Point], float, name='getx')
    pset.addPrimitive(Point.gety, [Point], float, name='gety')

    # a set of primitive mathematical functions
    pset.addPrimitive(operator.add, [float, float], float, name="plus")
    pset.addPrimitive(operator.sub, [float, float], float, name="minus")

    # a set of intermediate mathematical functions
    square = lambda x: x ** 2
    sqrt = lambda x: math.sqrt(abs(x))
    pset.addPrimitive(square, [float], float, name="square")
    pset.addPrimitive(sqrt, [float], float, name="sqrt")

    # give the input args more meaningful names
    pset.renameArguments(ARG0='P')
    return pset


class GrowTestCase(unittest.TestCase):
    def setUp(self):
        self.pset = get_pset()

    def test_terminals(self):
        self.assertRaises(DeadBranchError, ourGrow, self.pset, 1, float)
        tree = ourGrow(self.pset, 1, Point)
        self.assertIsInstance(tree[0], Terminal)
        print(PrimitiveTree(tree).height, [node.name for node in tree])

    def test_depth_2(self):
        # try a float
        tree = PrimitiveTree(ourGrow(self.pset, 2, float))
        print(tree.height, tree)
        self.assertLessEqual(tree.height, 2)
        # try a point
        tree = PrimitiveTree(ourGrow(self.pset, 2, Point))
        print(tree.height, tree)
        self.assertLessEqual(tree.height, 2)

    def test_depth_3(self):
        # try a float
        tree = PrimitiveTree(ourGrow(self.pset, 3, float))
        print("f", tree.height, tree)
        self.assertLessEqual(tree.height, 3)
        # try a point
        tree = PrimitiveTree(ourGrow(self.pset, 3, Point))
        print("p", tree.height, tree)
        self.assertLessEqual(tree.height, 3)

    def test_depth_4(self):
        # try a float
        tree = PrimitiveTree(ourGrow(self.pset, 4, float))
        print("f", tree.height, tree)
        self.assertLessEqual(tree.height, 4)
        # try a point
        tree = PrimitiveTree(ourGrow(self.pset, 4, Point, 0.0))
        print("p", tree.height, tree)
        self.assertLessEqual(tree.height, 4)

    def test_depth_20(self):
        # try a float
        tree = PrimitiveTree(ourGrow(self.pset, 20, float))
        print("f", tree.height, tree)
        self.assertLessEqual(tree.height, 20)
        # try a point
        tree = PrimitiveTree(ourGrow(self.pset, 20, Point, 0.0))
        print("p", tree.height, tree)
        self.assertLessEqual(tree.height, 20)
