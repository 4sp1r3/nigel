# An attempt to do the pythagoras problem with our modifications (Kosa).
# Modified to use typed ADF with matrices.

# maximum bounds of the x and y points
PLANE_SIZE = 20

import random
import math
import operator
import numpy

from deap import tools
from deap.gp import PrimitiveTree, compileADF, mutUniform, PrimitiveSetTyped

"""
### Training data: inputs and outputs
"""
class Point(object):
    """A point on a plane"""
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

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
    """A random point on the plane"""
    def __init__(self):
        super(RandomPoint, self).__init__(*[random.randrange(0, PLANE_SIZE) for _ in range(2)])


# a series of random points
INPUTS = [RandomPoint() for _ in range(50)]

# the distances between each point and the origin
OUTPUTS = [math.hypot(point.x, point.y) for point in INPUTS]


"""
### Primitive Sets for ADF and Main program
"""
square = lambda x: x ** 2
sqrt = lambda x: math.sqrt(abs(x))
to_float = lambda i: float(i)

primitives = [
    (Point.getx, [Point], int, 'x'),
    (Point.gety, [Point], int, 'y'),
    (operator.add, [float, float], float, '+'),
    (operator.sub, [float, float], float, '-'),
    (square, [float], float, '\u00B2'),
    (sqrt, [float], [float], "\u221A"),
    (to_float, [int], [float], "\u211C")
]



class FunctionTreeTyped(object):
    """A FunctionSet arranged into a tree.

    The tree is called with a list of typed inputs and returns a typed output.
    """
    def __init__(self, function_set=None, return_type=None, input_types=None):
        # None values meaning we haven't decided yet.
        # a list of (name, [in_types], ret_type, label) tuples
        self.function_set = function_set
        # the type this function returns; None means we don't know/care
        self.return_type = return_type
        # a list of input types
        self.input_types = input_types


def get_pset(primitives, name, arity, prefix='A'):
    """
    Returns a new PrimitiveSet
    """
    pset = PrimitiveSetTyped(name, [int, float, Point], ret_type, prefix)
    for func, arity in primitives:
        pset.addPrimitive(func, arity)
    return pset




from geneticprogramming import Individual
from geneticprogramming import Population


def evaluate(self):
    # run the function with the inputs and outputs and sum the outputs for a score out of 32
    pythagoras = compileADF(self, self.psets)
    score = sum([abs(distance - pythagoras(point)) for point, distance in zip(INPUTS, OUTPUTS)])
    score = min(100000, score)

    # accumulate the number of nodes actually used during a run by calling the adfs in the rpb
    nodes = 0
    for node in self[-1]:
        if node.name[:1] != 'F':
            nodes += 1
        else:
            nodes += len(self[int(node.name[1])])
    modifier = 1 + (-2 ** - (nodes / 250))

    return score + modifier,
# do something like
# Individual.evaluate = evaluate


"""
### Data Structures
"""
def main(pop_size=100, gens=100, adf_range=(0,4), adf_nargs=(1,5), mmc=(80,18,2), best_of_class=5, growth=(30,5,3)):

    mmc = (mmc[0]/sum(mmc), mmc[1]/sum(mmc), mmc[2]/sum(mmc))
    print("Running %s generations of %s individuals with %s ADFs of %s arguments.\n"
          "The best %s are cloned, thence %s%% mate, %s%% mutate, and %s%% clone.\n"
          "Tree growth has a %s%% probabilty being a terminal of up to %s deep on init, then %s deep on mutate.\n" % (
            gens, pop_size, adf_range, adf_nargs, best_of_class, int(100*mmc[0]), int(100*mmc[1]), int(100*mmc[2]),
            growth[0], growth[1], growth[2]))

    pop = Population(Individual, pop_size, adf_range, adf_nargs, growth)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    logbook = tools.Logbook()
    logbook.header = ['gen'] + stats.fields

    def log(gen):
        # write a generation to the log
        for ind in pop:
            ind.fitness.values = ind.evaluate()
        logbook.record(gen=gen, **stats.compile(pop))
        hof.update(pop)

        print(logbook.stream)
        gen += 1

    # Generational loop
    for gen in range(gens):
        log(gen)

        if hof[0].fitness.values[0] < 0.15:     # end early if correct and less than x nodes visited
            break

        # the best x of the population are cloned directly into the next generation
        sorted_pop = sorted(pop, key=lambda x: x.fitness.values[0])
        offspring = sorted_pop[:best_of_class]

        # rest of the population clone, mate, or mutate at random
        for idx in range(len(pop) - best_of_class):

            # decide how to alter this individual
            rand = random.random()

            # MATE/CROSSOVER
            if rand < mmc[0]:
                for _ in range(0, MAX_MATE_ATTEMPTS):
                    try:
                        receiver, contributor = pop.select(2)
                        child = receiver.clone()
                        child.mate(contributor)
                        break
                    except Individual.NoMateException:
                        pass
                else:
                    child = pop.select(1)  # fallback to a clone if we can't successfully mate
                    print("No mate after %s attempts." % MAX_MATE_ATTEMPTS)

            # MUTATE
            elif rand < (mmc[0] + mmc[1]):
                ind = pop.select(1)
                child = ind.clone()
                child.mutate()

            # CLONE
            else:
                child = pop.select(1)

            offspring.append(child)
        pop[:] = offspring
    log(gen+1)

    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main()
    print(hof)
