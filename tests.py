import unittest
from deap import creator
from pythagoras import *
from custom import TerminalsError
from deap.gp import PrimitiveTree

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)


class GrowTestCase(unittest.TestCase):
    def setUp(self):
        self.pset = get_pset()

    def test_terminals(self):
        try:
            tree = ourGrow(self.pset, 1, float)
            print([node.name for node in tree])
        except TerminalsError:
            print("TerminalsError")

    def test_depth_2(self):
        tree = ourGrow(self.pset, 2, float)
        print([node.name for node in tree])

    def test_depth_3(self):
        tree = ourGrow(self.pset, 3, float)
        print([node.name for node in tree])

    def test_depth_4(self):
        tree = ourGrow(self.pset, 4, float)
        print([node.name for node in tree])

    def test_depth_20(self):
        tree = PrimitiveTree(ourGrow(self.pset, 20, float, jiggle=1))
        print(tree.height, [node.name for node in tree])

    def test_individual(self):
        toolbox = base.Toolbox()
        toolbox.register("expr", ourGrow, self.pset, 5)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)

        ind = toolbox.individual()
        print(str(ind))
