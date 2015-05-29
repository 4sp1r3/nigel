# An attempt to do the parity problem with our modifications (Kosa).
# Runs, but is nonsense because the selection routine considers lower scores as better,
# whereas this problem seeks to maximize the eval score.

import random
import operator

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap.gp import PrimitiveTree, compile, mutUniform, PrimitiveSet
from app.ourMods import genGrow, cxPTreeGraft, selProbablistic, eaNigel, procreate

# Initialize Parity problem input and output matrices
PARITY_FANIN_M = 5
PARITY_SIZE_M = 2 ** PARITY_FANIN_M

inputs = [None] * PARITY_SIZE_M
outputs = [None] * PARITY_SIZE_M

for i in range(PARITY_SIZE_M):
    inputs[i] = [None] * PARITY_FANIN_M
    value = i
    dividor = PARITY_SIZE_M
    parity = 1
    for j in range(PARITY_FANIN_M):
        dividor /= 2
        if value >= dividor:
            inputs[i][j] = 1
            parity = int(not parity)
            value -= dividor
        else:
            inputs[i][j] = 0
    outputs[i] = parity

pset = PrimitiveSet("MAIN", PARITY_FANIN_M, "IN")
pset.addPrimitive(operator.and_, 2)
pset.addPrimitive(operator.or_, 2)
pset.addPrimitive(operator.xor, 2)
pset.addPrimitive(operator.not_, 1)
#pset.addTerminal(1)
#pset.addTerminal(0)

creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", genGrow, pset=pset, max_=5)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", compile, pset=pset)


def evalParity(individual):
    func = toolbox.compile(expr=individual)
    score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))
    score = max(0, PARITY_SIZE_M - score)
    return score,


toolbox.register("evaluate", evalParity)
toolbox.register("select", selProbablistic)
toolbox.register("mate", cxPTreeGraft, Individual=creator.Individual)
toolbox.register("expr_mut", genGrow, max_=3)
toolbox.register("mutate", mutUniform, expr=toolbox.expr_mut, pset=pset)
toolbox.register("procreate", procreate, toolbox=toolbox)


def main():
    #random.seed(21)
    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(2)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    eaNigel(pop, toolbox, 150, stats=stats, halloffame=hof)

    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main()
    print(hof)
