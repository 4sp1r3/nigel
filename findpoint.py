import random
import numpy
import math

from deap import gp
from deap import creator
from deap import base
from deap import tools
from deap import algorithms

PLANE_SIZE = 8
POPULATION_SIZE = 100



class Point(object):
    """
    A point on a plane
    """
    def __init__(self, x, y):
        """
        x and y is a black point on a white photo
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return "<%s, %s>" % (self.x, self.y)

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    @staticmethod
    def distance(this, that):
        """Return the distance between the point on this and the point provided"""
        return math.sqrt((this.x - that.x) ** 2 + (this.y - that.y) ** 2)


class RandomPoint(Point):
    def __init__(self):
        super(RandomPoint, self).__init__(*[random.randrange(0, PLANE_SIZE) for _ in range(2)])


A_RANDOMPOINTS = [RandomPoint() for _ in range(10)]




def set_creator():
    """
    configure the creator module
    :return: None, it adds classes to the module directly
    """
    # A smaller score (distance) is better
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    # Every individual is a tree of operations (plus a Fitness class)
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)


def get_pset():
    """
    :return: the typed set of primitive operations
    """
    pset = gp.PrimitiveSetTyped(
        "DAIN",
        [Point],
        Point
    )

    # get coordinates of a point
    pset.addPrimitive(Point.getx, [Point], int, name='getx')
    pset.addPrimitive(Point.gety, [Point], int, name='gety')

    # create a point
    pset.addPrimitive(Point, [int, int], Point, name='new_point')

    # create a terminal for every int
    pset.addEphemeralConstant("Rint", lambda: random.randint(0, PLANE_SIZE), int)

    # give the input args more meaningful names
    pset.renameArguments(ARG0='in_point')
    return pset


def get_toolbox(pset):
    """
    :return: a configured toolbox
    """
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genGrow, pset, min_=1, max_=50)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def eval_func(individual):
        """
        Apply the program to pairs of triangles in the sample set.  Tally up the differences
        between the output and the goal.
        """
        # print(individual)
        program = toolbox.compile(expr=individual)
        score = 0
        for point_in in A_RANDOMPOINTS:
            point_out = program(point_in)
            diff = Point.distance(point_in, point_out)
            score += diff
        return score,

    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selBest)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genGrow, min_=0, max_=5)
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
    return algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 10, stats, halloffame=hof)


def main():
    set_creator()
    pop, logbook = run(get_toolbox(get_pset()))
    for i in sorted(pop, key=lambda i: i.fitness.values[0], reverse=True):
        print(int(i.fitness.values[0]), i)


if __name__ == "__main__":
    main()
