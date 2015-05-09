"""
Genetic Program to find the Euclidean Distance between the origin (0,0) and a point (x,y), aka Pythagoras' Theorem.
"""
import random
import numpy
import math
import operator
import matplotlib.pyplot as plt
import networkx as nx

from deap import gp
from deap import creator
from deap import base
from deap import tools
from deap import algorithms

from generate2 import generate
gp.generate = generate

# maximum bound of the x and y point
PLANE_SIZE = 8

# number of solutions to retain from each generation
POPULATION_SIZE = 10

# Number of generations to run
NUM_GENERATIONS = 2


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
        return "Point(%s, %s)" % (self.x, self.y)

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    @staticmethod
    def distance(this, that):
        """Return the distance between the point on this and the point provided"""
        return math.sqrt((this.x - that.x) ** 2 + (this.y - that.y) ** 2)


class RandomPoint(Point):
    """
    A random point on the plane
    """
    def __init__(self):
        super(RandomPoint, self).__init__(*[random.randrange(0, PLANE_SIZE) for _ in range(2)])


# a series of random points
A_RANDOMPOINTS = [RandomPoint() for _ in range(20)]

# the origin point of the plane
ORIGIN = Point(0, 0)


def draw(individual):
    """
    Draws a node tree of the individual
    """
    nodes, edges, labels = gp.graph(individual)
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    pos = nx.graphviz_layout(graph, prog="dot")

    plt.figure(figsize=(7, 7))
    nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="w")
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, labels)
    plt.axis("off")
    plt.show()

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
    # We're asking for a program that consumes a point and returns a distance (float)
    pset = gp.PrimitiveSetTyped(
        "MAIN",
        [Point],
        float
    )

    # a couple of functions that return the x, and y, values of a point
    pset.addPrimitive(Point.getx, [Point], int, name='getx')
    pset.addPrimitive(Point.gety, [Point], int, name='gety')

    # a set of primitive mathematical functions
    pset.addPrimitive(operator.add, [int, int], int, name="plus")
    pset.addPrimitive(operator.sub, [int, int], int, name="minus")

    # a set of intermediate mathematical functions
    square = lambda x: x ** 2
    sqrt = lambda x: math.sqrt(abs(x))
    pset.addPrimitive(square, [int], int, name="square")
    pset.addPrimitive(sqrt, [int], float, name="sqrt")

    # create a terminal for every int or point
    pset.addEphemeralConstant("Rint", lambda: random.randint(0, PLANE_SIZE), int)

    # the origin is a terminal
    pset.addTerminal(ORIGIN, Point, "Origin")

    # give the input args more meaningful names
    pset.renameArguments(ARG0='in_point')
    return pset


# TODO: change everything to floats or Decimal
#   which will overcome error "int too large to convert to float"

def get_toolbox(pset):
    """
    :return: a configured toolbox
    """
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genGrow, pset, min_=2, max_=5)
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
        for point_in in A_RANDOMPOINTS:
            program_distance = program(point_in)
            true_distance = math.hypot(point_in.x, point_in.y)
            score += min(10000, abs(true_distance - program_distance))
        return score,

    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selBest)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genGrow, min_=0, max_=5)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    return toolbox


def ourSimple(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population
    :returns: A class:`~deap.tools.Logbook` with the statistics of the
              evolution
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population)/3)

        # Vary the pool of individuals
        offspring = gp.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook


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
        print(int(i.fitness.values[0]), i)


if __name__ == "__main__":
    main()
