import unittest
import random
import operator
from deap import creator
from deap import base
from deap import tools
from deap import gp
from app.custom import ourGrow
from app.ourMods import selProbablistic


class ProbablisticSelectionTestCase(unittest.TestCase):
    """
    Test the Probablistic selection routine. (well no, but it c/should)
    """
    def setUp(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

        # the primitive set
        pset = gp.PrimitiveSetTyped(
            "MAIN",
            [float],
            float
        )
        pset.addPrimitive(operator.add, [float, float], float, name="plus")
        pset.addPrimitive(operator.sub, [float, float], float, name="minus")
        pset.addEphemeralConstant("Rfloat", lambda: random.uniform(0, 10), float)
        self.pset = pset

        # the toolbox
        toolbox = base.Toolbox()
        toolbox.register("expr", ourGrow, pset, max_=2, prob=0.0)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        self.toolbox = toolbox

    def test_selection(self):
        # create population
        pop = self.toolbox.population(n=100)

        # give them fitnesses 0, 10, 20, 30...
        for fit, ind in enumerate(pop):
            ind.fitness.values = (fit,)

        # select twenty and sort by fitness
        for ind in sorted(selProbablistic(pop, 30), key=lambda i:i.fitness.values[0]):
            print(int(ind.fitness.values[0]), '\t', str(ind))

        # the frequency of individuals should deteriorate as you go down the list
