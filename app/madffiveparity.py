# An attempt to do the parity problem with our modifications (Kosa).
# Modified to use an ADF.

GENERATIONS = 5
POP_SIZE = 300

import random
import numpy

from deap import base
from deap import tools
from deap.gp import PrimitiveTree, compileADF, mutUniform, PrimitiveSet
from app.ourMods import genGrow, cxPTreeGraft, selProbablistic

"""
### Training data: inputs and outputs
"""
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

"""
### Primitive Sets for ADF and Main program
"""
# you can build anything you need from this one primitive
def nor(a,b):
    return not(a or b)
primitives = [(nor, 2)]

def get_pset(primitives, name, arity, prefix='ARG'):
    """returns a new PrimitiveSet"""
    pset = PrimitiveSet(name, arity, prefix)
    for func, arity in primitives:
        pset.addPrimitive(func, arity)
    return pset


adf0pset = get_pset(primitives, 'ADF0', 2)
adf1pset = get_pset(primitives, 'ADF1', 2)
pset = get_pset(primitives, "MAIN", PARITY_FANIN_M, "IN")
pset.addADF(adf0pset)
pset.addADF(adf1pset)


class FitnessMin(base.Fitness):
    weights = (-1.0,)


class Individual(list):
    """
    An Individual with a number of ADF's and an RPB
    """
    def __init__(self, *args, **kwargs):
        branches = [
            PrimitiveTree(genGrow(pset, 5)),
            PrimitiveTree(genGrow(adf1pset, 5)),
            PrimitiveTree(genGrow(adf0pset, 5))
        ]
        super(Individual, self).__init__(branches)
        self.fitness = FitnessMin()


def tool_compile(expr):
    return compileADF(expr, [pset, adf0pset, adf1pset])

def population(n):
    return [Individual() for _ in range(n)]


"""
### Data Structures
"""

def evalParity(individual):
    func = tool_compile(expr=individual)
    score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))
    nodes = len(individual[0]) + len(individual[1])
    score = max(0, PARITY_SIZE_M - score + nodes * 0.001)
    return score,

toolbox = base.Toolbox()
toolbox.register("evaluate", evalParity)
toolbox.register("select", selProbablistic)
toolbox.register("mate", cxPTreeGraft)
toolbox.register("expr_mut", genGrow, max_=3)
toolbox.register("mutate", mutUniform, expr=toolbox.expr_mut, pset=pset)


def main(pop_size=POP_SIZE, gens=GENERATIONS):
    #random.seed(21)
    pop = population(n=pop_size)
    hof = tools.HallOfFame(2)

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
            ind.fitness.values = toolbox.evaluate(ind)
        logbook.record(gen=gen, **stats.compile(pop))
        hof.update(pop)

        print(logbook.stream)
        gen += 1

    # Generational loop
    for gen in range(gens):
        log(gen)
        if hof[0].fitness.values[0] < 0.030:
            break
        offspring = []
        for idx in range(len(pop)):
            action = random.choice(('clone', 'mate', 'mutate'))

            if action == 'clone':
                ind = toolbox.select(pop, 1)
                child = toolbox.clone(ind)

            if action == 'mate':
                receiver, contributor = toolbox.select(pop, 2)
                child = toolbox.clone(receiver)
                subtree = random.choice((0, 1, 2))
                child[subtree] = PrimitiveTree(toolbox.mate(receiver[subtree], contributor[subtree]))

            if action == 'mutate':
                ind = toolbox.select(pop, 1)
                child = toolbox.clone(ind)
                section = random.choice(('ADF1', 'ADF0', 'MAIN'))
                if section == 'MAIN':
                    child[0] = toolbox.mutate(ind[0], pset=pset)[0]
                elif section == 'ADF1':
                    child[1] = toolbox.mutate(ind[1], pset=adf1pset)[0]
                else:
                    child[2] = toolbox.mutate(ind[2], pset=adf0pset)[0]

            offspring.append(child)
        pop[:] = offspring
    log(gen+1)

    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main()
    print(hof)
