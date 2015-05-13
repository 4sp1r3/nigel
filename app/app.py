import random
import operator
import numpy

from deap import gp
from deap import creator
from deap import base
from deap import tools
from deap import algorithms

from triangles import Photo, Triangle, RandomTriangle, Point


# Random triangles to use as training data
TRIANGLES = [RandomTriangle() for _ in range(10)]


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
        "MAIN",             # Name seems to be an arbritrary string
        [Photo, Triangle],  # Input types: a Photo and a Triangle
        Triangle            # Output type: a triangle
    )

    # Terminals
    pset.addTerminal(False, bool)
    pset.addTerminal(True, bool)

    # randoms
    pset.addEphemeralConstant("rand_x", lambda: random.randint(-50, 50), int)
    pset.addEphemeralConstant("rand_y", lambda: random.randint(-50, 50), int)

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
    pset.addPrimitive(operator.abs, [int], int, name="abs")

    # Boolean Mathematics
    pset.addPrimitive(operator.not_, [bool], bool, name="not")
    pset.addPrimitive(operator.lt, [int, int], bool, name="lt")
    pset.addPrimitive(operator.le, [int, int], bool, name="le")
    pset.addPrimitive(operator.eq, [int, int], bool, name="eq")
    pset.addPrimitive(operator.ne, [int, int], bool, name="ne")
    pset.addPrimitive(operator.ge, [int, int], bool, name="ge")
    pset.addPrimitive(operator.gt, [int, int], bool, name="gt")

    def if_then_else(input, output1, output2):
        if input:
            return output1
        else:
            return output2

    pset.addPrimitive(if_then_else, [bool, int, int], int, name="if_then_else")

    # loops? funcs? adf?

    # Photos
    pset.addTerminal(Photo.width, int, name='width')
    pset.addTerminal(Photo.height, int, name='height')
    pset.addPrimitive(Photo.is_white, [Photo, int, int], bool, name='is_white')
    pset.addPrimitive(Photo.is_black, [Photo, int, int], bool, name='is_black')

    # Triangles
    pset.addEphemeralConstant("rand_v", Triangle.random_vertex, Point)

    # get vertex cooredinates
    pset.addPrimitive(Triangle.getx, [Triangle, int], int, name='getx')
    pset.addPrimitive(Triangle.gety, [Triangle, int], int, name='gety')

    # move one vertex of the triangle by x/y
    pset.addPrimitive(Triangle.move, [Triangle, int, int, int], Triangle, name='move')

    # give the input args more meaningful names
    pset.renameArguments(ARG0='photo_in')
    pset.renameArguments(ARG1='triangle_in')
    return pset


def get_toolbox(pset):
    """
    :return: a configured toolbox
    """
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genGrow, pset, min_=5, max_=50)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def eval_func(individual):
        """
        Apply the program to pairs of triangles in the sample set.  Tally up the differences
        between the output and the goal.
        """
        #print(individual)
        program = toolbox.compile(expr=individual)
        total = 0.0
        input_triangle = TRIANGLES[0]
        for goal_triangle in TRIANGLES[1:]:
            output_triangle = program(goal_triangle.photo(), input_triangle)
            total += Triangle.distance(goal_triangle, output_triangle)
            print(input_triangle, output_triangle, goal_triangle)
            input_triangle = goal_triangle
        return total,

    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=5)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    return toolbox

def run(toolbox):
    pop = toolbox.population(n=5)
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
