# An attempt to do the parity problem with our modifications (Kosa).
# Modified to use an ADF.

GENERATIONS = 5
POP_SIZE = 300
ADF_RANGE = range(0, 5)

import random
import copy
import numpy
from functools import partial

from deap import base
from deap import tools
from deap.gp import PrimitiveTree, compileADF, mutUniform, PrimitiveSet
from app.ourMods import genGrow, selProbablistic, adfdraw

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


class FitnessMin(base.Fitness):
    weights = (-1.0,)


class Individual(list):
    """
    An Individual with a number of ADF's and an RPB.
    The RPB is last in the list. The ADFs preceed it in a hierarchy such that ADF0 uses only primitives,
    ADF1 uses primitves and ADF0, ADF2 uses primitives plus ADF0 plus ADF1... the RPB uses all the ADFs.
    """
    def __init__(self):
        self.psets = []
        self.branches = []

        # A number of Automatically Defined Functions
        adf_count = random.choice(ADF_RANGE)
        for adf_num in range(adf_count):
            adfset = get_pset(primitives, 'ADF%s' % adf_num, 2)     # todo: dynamic number of arguments
            for subset in self.psets:
                adfset.addADF(subset)
            self.psets.append(adfset)
            self.branches.append(PrimitiveTree(genGrow(adfset, 5)))

        # The Result Producing Branch and pset
        rpbset = get_pset(primitives, "MAIN", PARITY_FANIN_M, "IN")
        for subset in self.psets:
            rpbset.addADF(subset)
        self.psets.append(rpbset)
        self.branches.append(PrimitiveTree(genGrow(rpbset, 5)))

        super(Individual, self).__init__(self.branches)
        self.fitness = FitnessMin()

    def evaluate(self):
        # todo: adfs that call each other
        func = compileADF(self, self.psets)
        score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))

        # accumulate the number of nodes actually used during a run by calling the adfs in the rpb
        nodes = 0
        for node in self[-1]:
            if node.name[:3] != 'ADF':
                nodes += 1
            else:
                nodes += len(self[int(node.name[3])])

        score = max(0, PARITY_SIZE_M - score)
        score = score + 1 + (-2 ** - (nodes / 250))
        return score,

    def clone(self):
        return copy.deepcopy(self)

    def mutate(self):
        mut_expr = partial(genGrow, max_=3)
        branch = random.choice(range(len(self)))
        self[branch] = mutUniform(self[branch], expr=mut_expr, pset=self.psets[branch])[0]

    def mate(self, contributor):
        """
        Cut a compatible branch off the contributor and stick it somewhere here
        """
        # collect all possible receiving nodes
        r_nodes = [(b, n) for b in range(len(self.branches)) for n in range(len(self.branches[b]))]
        random.shuffle(r_nodes)

        # collect all possible contributor nodes
        c_nodes = [(b, n) for b in range(len(contributor.branches)) for n in range(len(contributor.branches[b]))]
        random.shuffle(c_nodes)

        def get_compatible_slice(nodetype, rpset):
            """
            returns a slice of the contributer which fits the receiving type and pset,
            or None
            """
            for cbranch, cnode in c_nodes:

                # reject types that don't match
                if contributor[cbranch][cnode].ret != nodetype:
                    continue

                candidate_slice = contributor.branches[cbranch].searchSubtree(cnode)

                # reject if the primitives in the contributing node are not known to the receiving branch
                nodeset = set([n.name for n in contributor.branches[cbranch][candidate_slice]])
                if not nodeset.issubset(set(rpset.mapping.keys())):
                    continue

                return (cbranch, candidate_slice)

            # the receiving node is wholly incompatible with the contributor
            return (None,None)

        for rbranch, rnode in r_nodes:
            cbranch, cslice = get_compatible_slice(self[rbranch][rnode].ret, self.psets[rbranch])
            if cbranch is not None:
                break

        pruned_slice = self[rbranch].searchSubtree(rnode)
        self[rbranch][pruned_slice] = contributor[cbranch][cslice]


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
        if hof[0].fitness.values[0] < 0.24:     # correct and less than 100 nodes visited
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
