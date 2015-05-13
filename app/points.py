import random
import operator
import numpy

from functools import partial
from deap import gp
from deap import creator
from deap import base
from deap import tools
from deap import algorithms


POPULATION_SIZE = 100



class PhotoOfAPoint(object):
    def __init__(self, x, y):
        """
        x and y is a black point on a white photo
        """
        self.x = x
        self.y = y

    @staticmethod
    def get_x(self):
        return self.x

    @staticmethod
    def get_y(self):
        return self.y

    def __repr__(self):
        return "<%s %s>" % (self.x, self.y)


def read_x(photo):
    return partial(PhotoOfAPoint.get_x, photo)


def read_y(photo):
    return partial(PhotoOfAPoint.get_y, photo)


class RandomPhotoAPoint(PhotoOfAPoint):
    def __init__(self):
        super(RandomPhotoAPoint, self).__init__(*[random.randrange(0, 8) for _ in range(2)])


A_RANDOMPHOTOS = [RandomPhotoAPoint() for _ in range(10)]
B_RANDOMPHOTOS = [RandomPhotoAPoint() for _ in range(10)]

class Vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '<%s, %s>' % (self.x, self.y)


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
        [PhotoOfAPoint, PhotoOfAPoint],
        Vector
    )

    # randoms
    pset.addEphemeralConstant("Rint", lambda: random.randint(0, 10), int)


    # Integer Mathematics
    def i_safe_div(left, right):
        try:
            return left // right
        except ZeroDivisionError:
            return 0

    pset.addPrimitive(operator.add, [int, int], int, name="iadd")
    pset.addPrimitive(operator.sub, [int, int], int, name="isub")
    pset.addPrimitive(operator.mul, [int, int], int, name="imul")
    pset.addPrimitive(i_safe_div, [int, int], int, name="idiv")

    # functions
    def a_not_negative(a, b):
        if a < 0:
            return a
        else:
            return b

    def negate(a):
        return -a


    pset.addPrimitive(a_not_negative, [int, int], int, name="the_greater_of")
    pset.addPrimitive(negate, [int], int, name="negate")

    # get coordinates
    pset.addPrimitive(read_x, [PhotoOfAPoint], int, name='getx')
    pset.addPrimitive(read_y, [PhotoOfAPoint], int, name='gety')
    #pset.addTerminal(photo_1, PhotoOfAPoint)
    #pset.addEphemeralConstant("randomphoto", lambda: RandomPhotoAPoint, RandomPhotoAPoint)
    #pset.addPrimitive(RandomPhotoAPoint.__init__, [], PhotoOfAPoint, name='randphoto')

    # create vector
    pset.addPrimitive(Vector.__init__, [int, int], Vector, name='make_vector')

    # give the input args more meaningful names
    pset.renameArguments(ARG0='photo_current')
    pset.renameArguments(ARG1='photo_target')
    return pset


def true_vector(a, b):
    return Vector(a.x - b.x, a.y - b.y)


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
        for x in range(len(A_RANDOMPHOTOS)):
            vector_out  = program(A_RANDOMPHOTOS[x], B_RANDOMPHOTOS[x])
            correct_vector = true_vector(A_RANDOMPHOTOS[x], B_RANDOMPHOTOS[x])
            score += abs(correct_vector.x - vector_out.x) + abs(correct_vector.y - correct_vector.x)
        return (1 / (1 - score),)


    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selBest, k=POPULATION_SIZE/10)
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
