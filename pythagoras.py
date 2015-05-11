"""
Genetic Program to find the Euclidean Distance between the origin (0,0) and a point (x,y), aka Pythagoras' Theorem.
"""
import random
import numpy
import math
import operator

from deap import gp
from deap import creator
from deap import base
from deap import tools
from deap import algorithms

from custom import ourGrow

#from custom import selWeighted

# maximum bound of the x and y point
PLANE_SIZE = 20

# number of solutions to retain from each generation
POPULATION_SIZE = 100

# Number of generations to run
NUM_GENERATIONS = 200



class Point(object):
    """
    A point on a plane
    """
    def __init__(self, x, y):
        """
        x and y is a black point on a white photo
        """
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point(%s, %s)" % (self.x, self.y)

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    @staticmethod
    def distance(this, that):
        """Return the distance between the point on this and the point provided"""
        return math.sqrt((this.x - that.x) ** 2.0 + (this.y - that.y) ** 2.0)


class RandomPoint(Point):
    """
    A random point on the plane
    """
    def __init__(self):
        super(RandomPoint, self).__init__(*[random.randrange(0, PLANE_SIZE) for _ in range(2)])


# a series of random points
A_RANDOMPOINTS = [RandomPoint() for _ in range(50)]

# the origin point of the plane
ORIGIN = Point(0, 0)


def set_creator():
    """
    configure the creator module
    :return: None, it adds classes to the module directly
    """
    # A smaller score (distance) is better
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))

    # Every individual is a tree of operations (plus a Fitness class)
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)


def get_pset():
    """
    :return: the typed set of primitive operations
    """
    # We're asking for a program that consumes a point and returns a distance (float)
    pset = gp.PrimitiveSetTyped(
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

    # create a terminal for every int
    #pset.addEphemeralConstant("Rint", lambda: random.randint(0, PLANE_SIZE), int)

    # the origin is a terminal
    #pset.addTerminal(ORIGIN, Point, "O")
    pset.addTerminal(0.0, float, "0")

    # give the input args more meaningful names
    pset.renameArguments(ARG0='P')
    return pset


def get_toolbox(pset):
    """
    :return: a configured toolbox
    """
    toolbox = base.Toolbox()
    toolbox.register("expr", ourGrow, pset, depth=5)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def eval_func(individual):
        """
        Apply the program to every point in the sample set.  Tally up the differences
        between the output and the actual distance.
        """
        #print(individual)
        program = toolbox.compile(expr=individual)
        score = 0
        try:
            for point_in in A_RANDOMPOINTS:
                program_distance = program(point_in)
                true_distance = math.hypot(point_in.x, point_in.y)
                score += min(100000, abs(true_distance - program_distance))
        except OverflowError:
            # just leave score at whatever before the maximum
            pass
        tree = gp.PrimitiveTree(individual)
        return score, tree.height

    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selBest)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", ourGrow, depth=5)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    return toolbox


def run(toolbox):
    pop = toolbox.population(n=POPULATION_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("max", numpy.max)
    stats.register("min", numpy.min)
    return algorithms.eaSimple(pop, toolbox, 0.90, 0.10, NUM_GENERATIONS, stats, halloffame=hof)


def main():
    set_creator()
    pop, logbook = run(get_toolbox(get_pset()))
    for i in sorted(pop, key=lambda i: i.fitness.values[0], reverse=True):
        print(int(i.fitness.values[0]), i.fitness.values[1], i)

if __name__ == "__main__":
    main()
