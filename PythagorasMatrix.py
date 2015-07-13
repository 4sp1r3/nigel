import math
import random
import operator
import warnings
import numpy as np

from app.ngp import Baseset
from app.ngp import Individual
from app.ngp import Population

warnings.filterwarnings("error")

"""
Pythagoras via Matrix
"""

"""
create sample data as random points within a boundary on a plane
"""
PLANE_SIZE = 20.0
SAMPLE_SIZE = 50
RANDOMPOINTS = [PLANE_SIZE * np.random.random_sample((1, 2)) for _ in range(SAMPLE_SIZE)]


"""
create a baseset of primitives
"""
def getValue(ndarray, idx):
    """Return the indexed value from the 1x2 numpy array"""
    return ndarray[0][idx]

square = lambda x: x ** 2
sqrt = lambda x: math.sqrt(abs(x))

bset = Baseset()
bset.addEphemeralConstant('P', lambda: random.randint(0, 1), int)
bset.addPrimitive(getValue, [np.ndarray, int], float, name="get")
bset.addPrimitive(operator.add, [float, float], float, name="add")
bset.addPrimitive(operator.sub, [float, float], float, name="sub")
bset.addPrimitive(square, [float], float, name="square")
bset.addPrimitive(sqrt, [float], float, name="sqrt")

"""
Define the individuals
"""
Individual.INTYPES = [np.ndarray]
Individual.OUTTYPE = float


def evaluate(individual):
    """sum of application of all the random points"""
    program = individual.compile()
    score = 0
    try:
        for point in RANDOMPOINTS:
            program_distance = program(point)
            true_distance = math.hypot(point[0][0], point[0][1])
            score += abs(true_distance - program_distance)
    except (OverflowError, RuntimeWarning):
        score = 100000
    return score,
Individual.evaluate = evaluate

"""
Create a population and evolve it
"""
population = Population(bset)
for generation in range(200):
    population.evolve()

best = population.hof[0]
print(best)
print(best.fitness.values[0])
