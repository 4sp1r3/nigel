import unittest
import random
import operator
from deap import creator
from deap import base
from deap import tools
from deap import gp
from app.ourMods import genGrow, cxPTreeGraft


class cxGraftTestCase(unittest.TestCase):
    """
    Test the grafting crossover
    """
    def setUp(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

        # a primitve set with two types: int and float
        pset = gp.PrimitiveSetTyped(
            "MAIN",
            [int],
            float
        )
        pset.addPrimitive(operator.add, [float, float], float, name="fplus")
        pset.addPrimitive(operator.sub, [int, int], int, name="iminus")
        pset.addPrimitive(float, [int], float, name="float")
        pset.addPrimitive(int, [float], int, name="int")
        pset.addEphemeralConstant("RFloat", lambda: random.uniform(0, 10), float)
        pset.addEphemeralConstant("RInt", lambda: random.randint(0, 10), int)
        self.pset = pset

        # the toolbox
        toolbox = base.Toolbox()
        toolbox.register("expr", genGrow, pset, max_=10, prob=0.4)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        self.toolbox = toolbox

    def test_graft(self):
        # create two individuals
        receiver = self.toolbox.individual()
        contributor = self.toolbox.individual()
        print(receiver)
        print(contributor)

        # often raises an error because the two individuals don't have a node of the same type
        child = creator.Individual(cxPTreeGraft(receiver, contributor))
        print(child)
