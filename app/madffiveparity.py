# An attempt to do the parity problem with our modifications (Kosa).
# Modified to use an ADF.

# percentage of pop to clone. Mut vs mate is an input
PB_CLONE = 2

MAX_MATE_ATTEMPTS = 10

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


def get_pset(primitives, name, arity, prefix='A'):
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
    class NoMateException(Exception): pass

    def __init__(self, adf_signature):
        """
        :param adf_signature: a list of the number of args for each adf
        eg: [1,2,3] means 3 adfs of 1 arg, 2 args, and 3 args respectively
        :return:
        """
        self.psets = []
        self.branches = []
        self.signature = adf_signature

        # A number of Automatically Defined Functions
        for adf_num, nargs in enumerate(adf_signature):
            adfset = get_pset(primitives, 'F%s' % adf_num, nargs)
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
        func = compileADF(self, self.psets)
        score = 0
        try:
            for in_, out in zip(inputs, outputs):
                if func(*in_) == out:
                    score += 1
#            score = sum(func(*in_) == out for in_, out in zip(inputs, outputs))
        except Exception as ex:
            print(ex)
            adfdraw(self)
            raise ex
        score = max(0, PARITY_SIZE_M - score)

        # accumulate the number of nodes actually used during a run by calling the adfs in the rpb
        nodes = 0
        for node in self[-1]:
            if node.name[:1] != 'F':
                nodes += 1
            else:
                nodes += len(self[int(node.name[1])])

        modifier = 1 + (-2 ** - (nodes / 250))
        return score + modifier,

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

        def get_compatible_slice(rnode, rpset):
            """
            returns a slice of the contributer which fits the receiving type and pset,
            or None
            """
            for cbranch, cnode in c_nodes:

                # reject swapping nodes that don't match
                if contributor[cbranch][cnode] != rnode:
                    continue

                # reject if adfs in contributed nodes have a different signature
                candidate_slice = contributor.branches[cbranch].searchSubtree(cnode)
                candidate_nodes = contributor.branches[cbranch][candidate_slice]

                # all the signatures match
                try:
                    if all([subnode == rpset.mapping[subnode.name] for subnode in candidate_nodes]):
                        return (cbranch, candidate_slice)
                except KeyError:
                    continue

            # the receiving node is wholly incompatible with the contributor
            return (None,None)

        for rbranch, rnode in r_nodes:
            cbranch, cslice = get_compatible_slice(self[rbranch][rnode], self.psets[rbranch])
            if cbranch is not None:
                break

        if cbranch is None or cslice is None:
            raise self.NoMateException()

        pruned_slice = self[rbranch].searchSubtree(rnode)
        self[rbranch][pruned_slice] = contributor[cbranch][cslice]


class Population(list):
    def __init__(self, ind, pop_size, adf_range, adf_nargs):
        # generate a bunch of individuals with adfs within the specified ranges
        pop = []
        for idx in range(pop_size):
            adfs = []
            for adf_num in range(adf_range[0], random.randint(adf_range[0], adf_range[1])):
                adfs.append(random.randint(adf_nargs[0], adf_nargs[1]))
            pop.append(ind(adfs))

        super(Population, self).__init__(pop)

    def select(self, n):
        return selProbablistic(self, n)


"""
### Data Structures
"""
def main(pop_size=100, gens=100, adf_range=(0,4), adf_nargs=(1,5), pb_mate=80, best_of_class=5):

    pop = Population(Individual, pop_size, adf_range, adf_nargs)
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

        if hof[0].fitness.values[0] < 0.25:     # end early if correct and less than x nodes visited
            break

        # the best x of the population are cloned directly into the next generation
        sorted_pop = sorted(pop, key=lambda x: x.fitness.values[0])
        offspring = sorted_pop[:best_of_class]

        # rest of the population clone, mate, or mutate at random
        for idx in range(len(pop) - best_of_class):

            # decide how to alter this individual
            rand = random.randint(0, 100)
            if rand in range(0, PB_CLONE):
                action = 'clone'
            elif rand in range(0, pb_mate):
                action = 'mate'
            else:
                action = 'mutate'

            if action == 'clone':
                ind = pop.select(1)
                child = ind.clone()

            if action == 'mate':
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
