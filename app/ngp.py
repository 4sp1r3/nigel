import copy
import random
import numpy as np
from inspect import isclass
from functools import partial
import matplotlib.pyplot as plt
import networkx as nx

from deap.gp import PrimitiveSetTyped
from deap.gp import PrimitiveTree
from deap.gp import Primitive
from deap.gp import mutUniform
from deap.base import Fitness
from deap.tools import Statistics
from deap.tools import HallOfFame
from deap.tools import Logbook


class GrowException(Exception):
    """Tried a bunch of times but could not grow a suitable tree from the given primitives"""
    pass


class DeadBranchError(Exception):
    """Could not grow a tree.
    Probably because there are no nodes of the required type available"""
    pass

class NoMateException(Exception):
    """Unsuccessful in finding a compatible mate for an individual"""
    pass


class Baseset(object):
    """
    Basic list of primitive functions granted to the problem
    """
    def __init__(self):
        """
        :param primitives: a list of primitives as tuples (func, intypes, outtype)
        Eg. (operator.add, [int, int], int)
        """
        # collection of primitives
        self.primitives = []
        # collection of available ephemeral routines
        self.ephemerals = []
        # dict of instantiated ephemerals
        self.ephemeral_instances = {}
        # collection of terminals
        self.terminals = []

    def addPrimitive(self, primitive, in_types, ret_type, name=None):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.primitives.append((primitive, in_types, ret_type, name))

    def addTerminal(self, terminal, ret_type, name=None):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.terminals.append((terminal, ret_type, name))

    def addEphemeralConstant(self, name, ephemeral, ret_type):
        """
        Same as for DEAPs PrimitiveSetTyped
        """
        self.ephemerals.append((name, ephemeral, ret_type))

    def get_ephemeral_instance(self, idx):
        """creates a new ephemeral and stores it and returns it
        :param idx: the id of the ephemeral to instantiate
        """
        (name, func, ret) = self.ephemerals[idx]
        name = 'E%s' % len(self.ephemeral_instances)
        value = func()
        self.ephemeral_instances[name] = value
        return name, value


class FitnessMin(Fitness):
    weights = (-1.0,)


class Individual(object):
    """
    An (individual) program of a random number of adfs and a Result Producing Branch (RPB)
    """
    # A list of input types
    INTYPES = NotImplemented
    # The output type
    OUTTYPE = NotImplemented
    # The maximum number of ADFs to generate
    MAX_ADFS = 4
    # min, max number of input arguments to adfs
    ADF_NARGS = (1, 5)
    # Probability of terminal when growing:
    GROWTH_TERM_PB = 0.3
    # Maximum depth of initial growth
    GROWTH_MAX_INIT_DEPTH = 5
    # Maximum depth of mutation growth
    GROWTH_MAX_MUT_DEPTH = 3
    # maximum number of times to attempt to grow a complete adf before abandoning
    GROWTH_MAX_ATTEMPTS = 50
    # maximum number of signatures to try before ultimately giving up
    GROWTH_MAX_SIGNATURES = 1000

    def __init__(self, baseset):
        """
        :param baseset: a Baseset object with the primitives already loaded
        """
        # a reference to the baseset of primitives, terminals and ephemerals
        self.baseset = baseset
        # a collection of function trees
        self.trees = []
        # collection of psets; one for each tree
        self.psets = []

        # randomly decide the number of adfs
        nADFs = random.choice(list(range(self.MAX_ADFS + 1)))

        # generate the adfs
        for idx in range(nADFs):
            name = 'F%s' % idx
            self.add_function(name)

        # generate the RPB
        self.add_function("MAIN", self.INTYPES, self.OUTTYPE, prefix='IN')

        # attach a fitness
        self.fitness = FitnessMin()

    def __str__(self):
        """describe this in english"""
        return "\n".join([pset.name + ":" + str(tree) for tree, pset in self])

    def __iter__(self):
        """return pairs of tree/psets"""
        for pair in zip(self.trees, self.psets):
            yield pair

    def get_random_outtype(self):
        urn = list()
        for prim in self.baseset.primitives:
            urn.append(prim[2])
        for adf in self.psets:
            urn.append(adf.ret)
        return random.choice(urn)

    def get_random_intypes(self):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in self.baseset.primitives:
            for intype in prim[1]:
                urn.append(intype)
        for adf in self.psets:
            for intype in adf.ins:
                urn.append(intype)

        # choose the number of args
        nargcount = random.randint(self.ADF_NARGS[0], self.ADF_NARGS[1])

        # range the args from 0 to ensure they're contiguous
        return [random.choice(urn) for _ in range(nargcount)]

    def get_primitive_set(self, name, intypes, outtype, prefix):
        """
        Return a deap primitive set corresponding to the base prims and any added adfs
        """
        pset = PrimitiveSetTyped(name, intypes, outtype, prefix)
        for term in self.baseset.terminals:
            pset.addTerminal(term[0], term[1], term[2])
        for idx in range(len(self.baseset.ephemerals)):
            name, value = self.baseset.get_ephemeral_instance(idx)
            pset.addTerminal(value, type(value), name)
        for prim in self.baseset.primitives:
            pset.addPrimitive(prim[0], prim[1], prim[2], prim[3])
        for adfset in self.psets:
            pset.addADF(adfset)
        return pset

    def grow(self, pset, max_, type_=None, prob=0.30):
        """Generate an expression tree.
        Branches can be of any height, provided they are not more than *max*.

        :param pset: Primitive set from which primitives are selected.
        :param max_: Maximum height of the produced tree.
        :param prob: 0..1 the probability of a terminal (vs primitive) being placed at a node.
        :param type_: The type that the tree should return when called.
        :returns: An expression tree.
        """

        def random_terminal():
            terminals = pset.terminals[type_]
            if len(terminals) == 0:
                raise DeadBranchError("No terminal of type '%s' is available" % type_)
            else:
                term = random.choice(terminals)
                # and if it's actually a class then instantiate it
                if isclass(term):
                    term = term()
                return [term]

        if type_ is None:
            type_ = pset.ret

        # we're at the maximum depth, or there are no primitives to try
        if max_ <= 1 or not len(pset.primitives[type_]):
            return random_terminal()

        # if chance dictates, return a terminal, if you can
        try:
            if random.random() < prob:
                return random_terminal()
        except DeadBranchError:
            # No problem, press on, we'll try the prims.
            pass

        primitives = pset.primitives[type_].copy()
        random.shuffle(primitives)
        for prim in primitives:
            try:
                expr = [prim]
                for arg in prim.args:
                    expr += self.grow(pset, max_ - 1, arg, prob)
                return expr
            except DeadBranchError:
                # ok, this prim is no good, but press on and try others
                continue
        else:
            # exhausted all terminals and primitives
            raise DeadBranchError("Neither primitives nor terminals of type '%s' could be found" % type_)

    def add_function(self, name, intypes=None, outtype=None, prefix='A'):
        """
        Create and add a new function
        :param name: a unique name for the function (or non-unique if that's a deliberate intention)
        :param intypes: list of input types
        :param outtype: the output type
        :param prefix: label for the input terminals
        :return: undefined
        """
        # if we can't grow a function and types were not specified
        # then we'll change the signature, otherwise fails
        flexible_signature = outtype is None and intypes is None

        # pick an outtype
        if outtype is None:
            outtype = self.get_random_outtype()

        # pick the intypes
        if intypes is None:
            intypes = self.get_random_intypes()

        # (try to) grow a tree
        for _ in range(self.GROWTH_MAX_SIGNATURES):
            pset = self.get_primitive_set(name, intypes, outtype, prefix)
            for _ in range(self.GROWTH_MAX_ATTEMPTS):
                try:
                    tree = PrimitiveTree(self.grow(pset, self.GROWTH_MAX_INIT_DEPTH, outtype, prob=self.GROWTH_TERM_PB))
                except DeadBranchError:
                    continue
                all_args_used = all([pset.mapping[arg] in tree for arg in pset.arguments])
                if all_args_used and len(tree) > 1:
                    self.psets.append(pset)
                    self.trees.append(tree)
                    return
            else:
                if flexible_signature:
                    # try a different signature
                    outtype = self.get_random_outtype()
                    intypes = self.get_random_intypes()
                else:
                    raise GrowException("Despite trying %s times unable to grow specified signature %s -> %s ." %
                                        (self.GROWTH_MAX_ATTEMPTS, intypes, outtype))
        else:
            # we tried but no valid tree could be grown
            raise GrowException("No ADF tree could be grown after %s attempts with different ADF signatures, "
                                "where %s attempts were made to grow within each signature. Please review your "
                                "definitions of the primitives and retry" % (
                                    self.GROWTH_MAX_SIGNATURES, self.GROWTH_MAX_ATTEMPTS))

    def clone(self):
        """returns a copy of oneself"""
        return copy.deepcopy(self)

    def mutate(self):
        """pick a random node and cut/grow a new bit of tree there"""
        mut_expr = partial(self.grow, max_=self.GROWTH_MAX_MUT_DEPTH, prob=self.GROWTH_TERM_PB)
        tree = random.choice(range(len(self.trees)))
        self.trees[tree] = mutUniform(self.trees[tree], expr=mut_expr, pset=self.psets[tree])[0]

    def mate(self, contributor):
        """
        Cut a compatible branch off the contributor and stick it somewhere here
        """
        # collect all possible receiving nodes
        r_nodes = [(b, n) for b in range(len(self.trees)) for n in range(len(self.trees[b]))]
        random.shuffle(r_nodes)

        # collect all possible contributor nodes
        c_nodes = [(b, n) for b in range(len(contributor.trees)) for n in range(len(contributor.trees[b]))]
        random.shuffle(c_nodes)

        def get_compatible_slice(rnode, rpset):
            """
            returns a slice of the contributer which fits the receiving type and pset,
            or None
            """
            for cbranch, cnode in c_nodes:

                # reject swapping nodes that don't match
                if contributor.trees[cbranch][cnode] != rnode:
                    continue

                # reject if adfs in contributed nodes have a different signature
                candidate_slice = contributor.trees[cbranch].searchSubtree(cnode)
                candidate_nodes = contributor.trees[cbranch][candidate_slice]

                # all the signatures match
                # FIXME: what about the ephemerals!? So what are we checking for nowadays?!
                try:
                    if all([subnode == rpset.mapping[subnode.name] for subnode in candidate_nodes]):
                        return (cbranch, candidate_slice)
                except KeyError:
                    continue

            # the receiving node is wholly incompatible with the contributor
            return (None, None)

        for rbranch, rnode in r_nodes:
            cbranch, cslice = get_compatible_slice(self.trees[rbranch][rnode], self.psets[rbranch])
            if cbranch is not None:
                break

        if cbranch is None or cslice is None:
            raise NoMateException()

        pruned_slice = self.trees[rbranch].searchSubtree(rnode)
        self.trees[rbranch][pruned_slice] = contributor.trees[cbranch][cslice]

    def compile(self):
        # removes deap's compile and compileADF so we can see what it's doing.
        # for each routine, add previous routines to the context, codify the routine and call it,
        #  then add it to the list of routines in context. Return the evaluated solution.
        adfdict = {}
        func = None
        for subexpr, pset in self:
            pset.context.update(adfdict)
            code = str(subexpr)
            if len(pset.arguments) > 0:
                adfargs = ",".join(arg for arg in pset.arguments)
                code = "lambda {args}: {code}".format(args=adfargs, code=code)
            func = eval(code, pset.context, {})
            adfdict.update({pset.name: func})
        return func

    def evaluate(self, *args):
        raise NotImplementedError()

    def draw(self):
        """
        Draws a node tree of an adf individual
        """
        PROGN = 'PROGN'
        expr = []
        for num, branch in enumerate(self.trees[:-1]):
            expr = expr + ['F%s' % num] + branch
        expr += ['RPB'] + self.trees[-1]
        nodes = list(range(len(expr)))
        edges = list()
        labels = dict()

        stack = []
        for i, node in enumerate(expr):
            if stack:
                edges.append((stack[-1][0], i))
                stack[-1][1] -= 1

            if isinstance(node, Primitive):
                labels[i] = node.name
            elif hasattr(node, 'value'):
                labels[i] = node.value
            else:
                labels[i] = str(node)

            if hasattr(node, 'arity'):
                stack.append([i, node.arity])
            elif node == PROGN:
                stack.append([i, len(self.trees[-1])])
            else:
                stack.append([i, 1])

            while stack and stack[-1][1] == 0:
                stack.pop()

        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        pos = nx.graphviz_layout(graph, prog="dot")

        figsize = (25, max([i.height for i in self.trees]) + 2)
        fig = plt.figure(figsize=figsize)
        fig.suptitle("Score {:2.4f}".format(self.fitness.values[0]), fontsize=16, y=0.05)
        fig.text(0.0, 0.05, "\n".join(
            # ["{}".format(individual.signature)] +
            ["{} ({})".format(k, v.arity) for k, v in sorted(self.psets[-1].mapping.items())]
        ))
        nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="w")
        nx.draw_networkx_edges(graph, pos)
        nx.draw_networkx_labels(graph, pos, labels)
        plt.axis("off")
        plt.show()


class Population(list):
    """
    A collection of individuals
    """
    INDIVIDUAL_CLASS = Individual
    POPULATION_SIZE = 100
    MAX_MUTATION_DEPTH = 2
    CLONE_BEST = 5
    MAX_MATE_ATTEMPTS = 10
    MATE_MUTATE_CLONE = (80, 18, 2)

    def __init__(self, baseset):
        self.bset = baseset
        pop = [self.INDIVIDUAL_CLASS(self.bset) for _ in range(self.POPULATION_SIZE)]
        super(Population, self).__init__(pop)

        self.stats = Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

        self.logbook = Logbook()
        self.logbook.header = ['gen'] + self.stats.fields

        self.hof = HallOfFame(1)
        self.generation = 0

    def select(self, k):
        """Probablistic select *k* individuals among the input *individuals*. The
        list returned contains references to the input *individuals*.

        :param individuals: A list of individuals to select from.
        :param k: The number of individuals to select.
        :returns: A list containing k individuals.

        The individuals returned are randomly selected from individuals according
        to their fitness such that the more fit the individual the more likely
        that individual will be chosen.  Less fit individuals are less likely, but
        still possibly, selected.
        """
        # adjusted pop is a list of tuples (adjusted fitness, individual)
        adjusted_pop = [(1.0 / (1.0 + i.fitness.values[0]), i) for i in self]

        # normalised_pop is a list of tuples (float, individual) where the float indicates
        # a 'share' of 1.0 that the individual deserves based on it's fitness relative to
        # the other individuals. It is sorted so the best chances are at the front of the list.
        denom = sum([fit for fit, ind in adjusted_pop])
        normalised_pop = [(fit / denom, ind) for fit, ind in adjusted_pop]
        normalised_pop = sorted(normalised_pop, key=lambda x: x[0], reverse=True)

        # randomly select with a fitness bias
        # FIXME: surely this can be optimized?
        selected = []
        for x in range(k):
            rand = random.random()
            accumulator = 0.0
            for share, ind in normalised_pop:
                accumulator += share
                if rand <= accumulator:
                    selected.append(ind)
                    break
        if len(selected) == 1:
            return selected[0]
        else:
            return selected

    def evolve(self):
        """
        Return an evolved population
        :returns: a population
        """
        # evaluate every individual
        for ind in self:
            if not len(ind.fitness.values):
                ind.fitness.values = ind.evaluate()

        self.logbook.record(gen=self.generation, **self.stats.compile(self))
        self.hof.update(self)
        print(self.logbook.stream)

        # the best x of the population are cloned directly into the next generation
        sorted_pop = sorted(self, key=lambda i: i.fitness.values[0])
        offspring = sorted_pop[:self.CLONE_BEST]

        # rest of the population clone, mate, or mutate at random
        for idx in range(len(self) - self.CLONE_BEST):

            # decide how to alter this individual
            rand = random.random()
            if rand < self.MATE_MUTATE_CLONE[0]:  # MATE/CROSSOVER
                for _ in range(0, self.MAX_MATE_ATTEMPTS):
                    try:
                        receiver, contributor = self.select(2)
                        child = receiver.clone()
                        child.mate(contributor)
                        break
                    except NoMateException:
                        raise
                else:  # fallback to a clone if we can't successfully mate
                    child = self.select(1)
                    print("No mate after %s attempts." % self.MAX_MATE_ATTEMPTS)

            elif rand < (self.MATE_MUTATE_CLONE[0] + self.MATE_MUTATE_CLONE[1]):  # MUTATE
                ind = self.select(1)
                child = ind.clone()
                child.mutate()

            else:  # CLONE
                child = self.select(1)

            offspring.append(child)
        self[:] = offspring
        self.generation += 1
