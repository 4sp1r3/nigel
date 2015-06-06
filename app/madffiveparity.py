# An attempt to do the parity problem with our modifications (Kosa).
# Modified to use an ADF.

GENERATIONS = 5
POP_SIZE = 300

import random
import copy
import numpy
from functools import partial

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

    def evaluate(self):
        func = compileADF(self, [pset, adf0pset, adf1pset])
        score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))
        nodes = len(self[0]) + len(self[1]) + len(self[2])
        score = max(0, PARITY_SIZE_M - score + nodes * 0.001)
        return score,

    def clone(self):
        return copy.deepcopy(self)

    def mutate(self):
        section = random.choice(('ADF1', 'ADF0', 'MAIN'))
        mut_expr = partial(genGrow, max_=3)
        if section == 'MAIN':
            self[0] = mutUniform(self[0], expr=mut_expr, pset=pset)[0]
        elif section == 'ADF1':
            self[1] = mutUniform(self[1], expr=mut_expr, pset=adf1pset)[0]
        else:
            self[2] = mutUniform(self[2], expr=mut_expr, pset=adf0pset)[0]

    def mate(self, contributor):
        subtree = random.choice((0, 1, 2))
        self[subtree] = PrimitiveTree(cxPTreeGraft(self[subtree], contributor[subtree]))


class Population(list):
    def __init__(self, ind, n):
        super(Population, self).__init__([ind() for _ in range(n)])

    def select(self, n):
        return selProbablistic(self, n)


"""
### Data Structures
"""
def main(pop_size=POP_SIZE, gens=GENERATIONS):
    #random.seed(21)
    pop = Population(Individual, pop_size)
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
            ind.fitness.values = ind.evaluate()
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
                ind = pop.select(1)
                child = ind.clone()

            if action == 'mate':
                receiver, contributor = pop.select(2)
                child = receiver.clone()
                child.mate(contributor)

            if action == 'mutate':
                ind = pop.select(1)
                child = ind.clone()
                child.mutate()

            offspring.append(child)
        pop[:] = offspring
    log(gen+1)

    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main()
    print(hof)
