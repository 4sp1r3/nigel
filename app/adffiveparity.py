# An attempt to do the parity problem with our modifications (Kosa).
# Modified to use an ADF.

GENERATIONS = 5
POP_SIZE = 300

import random
import operator

import numpy

from deap import base
from deap import creator
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

# the adf takes two inputs and has just the one primitive
adfpset = PrimitiveSet("ADF0", 2, "ARG")
adfpset.addPrimitive(nor, 2)

# the main pset is the same, plus the adf
pset = PrimitiveSet("MAIN", PARITY_FANIN_M, "IN")
pset.addPrimitive(nor, 2)
pset.addADF(adfpset)


"""
### Data Structures
"""
# An Individual comprises two trees: the ADF and the Main program and seeks the lowest fitness score
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
creator.create("ADF", PrimitiveTree, pset=adfpset)
creator.create("MAIN", PrimitiveTree, pset=pset)
toolbox = base.Toolbox()

# The ADF is grown up to 5 levels deep
toolbox.register("adf_expr", genGrow, pset=adfpset, max_=5)
toolbox.register("ADF", tools.initIterate, creator.ADF, toolbox.adf_expr)

# the program is also grown up to 5 levels deep
toolbox.register("main_expr", genGrow, pset=pset, max_=5)
toolbox.register("MAIN", tools.initIterate, creator.MAIN, toolbox.main_expr)
toolbox.register("individual", tools.initCycle, creator.Individual, [toolbox.MAIN, toolbox.ADF])

# the population is a list of individuals and (hopefully) the default compile routine knows what to do
# with the adfs
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", compileADF, psets=[pset, adfpset])

def evalParity(individual):
    func = toolbox.compile(expr=individual)
    score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))
    nodes = len(individual[0]) + len(individual[1])
    score = max(0, PARITY_SIZE_M - score + nodes * 0.001)
    return score,

toolbox.register("evaluate", evalParity)

# TODO: and so how does it crossbreed?!
toolbox.register("select", selProbablistic)
toolbox.register("mate", cxPTreeGraft)
toolbox.register("expr_mut", genGrow, max_=3)
toolbox.register("mutate", mutUniform, expr=toolbox.expr_mut, pset=pset)


def main(pop_size=POP_SIZE, gens=GENERATIONS):
    #random.seed(21)
    pop = toolbox.population(n=pop_size)
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
                subtree = random.choice((0, 1))
                if subtree == 0:
                    creator.MAIN(toolbox.mate(receiver[subtree], contributor[subtree]))
                else:
                    creator.ADF(toolbox.mate(receiver[subtree], contributor[subtree]))

            if action == 'mutate':
                ind = toolbox.select(pop, 1)
                child = toolbox.clone(ind)
                section = random.choice(('ADF', 'MAIN'))
                if section == 'MAIN':
                    child[0] = toolbox.mutate(ind[0], pset=pset)[0]
                else:
                    child[1] = toolbox.mutate(ind[1], pset=adfpset)[0]
            offspring.append(child)
        pop[:] = offspring
    log(gen+1)

    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main()
    print(hof)
