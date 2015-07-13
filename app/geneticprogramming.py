import random
import copy
from functools import partial
from inspect import isclass

from deap.gp import PrimitiveTree
from deap.gp import PrimitiveSet, PrimitiveSetTyped
from deap.gp import compileADF
from deap.gp import mutUniform
from deap.base import Fitness


class NoMateException(Exception):
    """Raised when two individuals cannot be mated"""
    pass


class DeadBranchError(Exception):
    """Raised when a tree could not grow further"""
    pass



class Individual(list):
    """An Individual with a number of ADF's and an RPB.

    The RPB is last in the list. The ADFs preceed it in a hierarchy such that ADF0 uses only primitives,
    ADF1 uses primitves and ADF0, ADF2 uses primitives plus ADF0 plus ADF1... the RPB uses all the ADFs.
    """
    def __init__(self, primitives, adf_range, adf_nargs, growth):
        """
        :param growth: parameters for the growth routine (percentage terminals, initial max depth, mut depth)
        :param adf_signature: a list of the number of args for each adf, other we'll work it out randomly.
            eg: [1,2,3] means 3 adfs of 1 arg, 2 args, and 3 args respectively
        """
        self.psets = []
        self.branches = []
        self.grow_pb = growth[0] / 100
        self.grow_init = growth[1]
        self.grow_mut = growth[2]
        self.primitives = primitives

        # generate an adf signature
        self.adf_signature = []
        for adf_num in range(adf_range[0], random.randint(adf_range[0], adf_range[1])):
            self.adf_signature.append(random.randint(adf_nargs[0], adf_nargs[1]))

        # A number of Automatically Defined Functions
        for adf_num, nargs in enumerate(self.adf_signature):
            adfset = self.get_pset('F%s' % adf_num, nargs)
            for subset in self.psets:
                adfset.addADF(subset)
            self.psets.append(adfset)
            self.branches.append(PrimitiveTree(genGrow(adfset, max_=self.grow_init, prob=self.grow_pb)))

        # The Result Producing Branch and pset
        rpbset = self.get_pset("MAIN", 1, "P")
        for subset in self.psets:
            rpbset.addADF(subset)
        self.psets.append(rpbset)
        self.branches.append(PrimitiveTree(genGrow(rpbset, max_=self.grow_init, prob=self.grow_pb)))

        super(Individual, self).__init__(self.branches)
        Fitness.weights = (-1.0,)  # override this if you want something else, eg maximize
        self.fitness = Fitness()

    def get_pset(self, name, arity, prefix='A'):
        """returns a new PrimitiveSet"""
        pset = PrimitiveSet(name, arity, prefix)
        for func, arity in self.primitives:
            pset.addPrimitive(func, arity)
        return pset

    def evaluate(self):
        NotImplemented

    def clone(self):
        return copy.deepcopy(self)

    def mutate(self):
        mut_expr = partial(genGrow, max_=self.grow_mut, prob=self.grow_pb)
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
            return (None, None)

        for rbranch, rnode in r_nodes:
            cbranch, cslice = get_compatible_slice(self[rbranch][rnode], self.psets[rbranch])
            if cbranch is not None:
                break

        if cbranch is None or cslice is None:
            raise NoMateException()

        pruned_slice = self[rbranch].searchSubtree(rnode)
        self[rbranch][pruned_slice] = contributor[cbranch][cslice]


class Population(list):
    """A list of individuals.

    :param ind: the class of individuals
    :param pop_size: the number of individuals
    :param adf_range: pick the number of adfs from this range
    :param adf_args: pick the number arguments in each adf from this range
    :param growth: parameters for the growth routine (percentage terminals, initial max depth, mut depth)
    """

    def __init__(self, ind, pop_size, adf_range, adf_nargs, growth):
        # generate a bunch of individuals with adfs within the specified ranges
        pop = []

        # each individual
        for idx in range(pop_size):
            # add the individual to the population
            pop.append(ind(growth))

        super(Population, self).__init__(pop)

    def select(self, n):
        return selProbablistic(self, n)


def selProbablistic(individuals, k):
    """Select *k* individuals among the input *individuals*. The
    list returned contains references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list containing k individuals.

    The individuals returned are randomly selected from individuals according
    to their fitness such that the more fit the individual the more likely
    that individual will be chosen.  Less fit individuals are less likely, but
    still possibly, selected.
    """
    # be sure to evaluate the individuals first
    for ind in individuals:
        if not getattr(ind.fitness, "values", False):
            raise Exception("Invalid fitness: you have to ensure all the individuals have fitness values "
                            "before calling this.")

    # adjusted pop is a list of tuples (adjusted fitness, individual)
    adjusted_pop = [(1.0 / (1.0 + i.fitness.values[0]), i) for i in individuals]

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


class ProgramTree(object):
    """A tree of functions"""
    adf_range = range(0, 3)
    adf_nargs = range(1, 3)

    def __init__(self, intypes, outtype, fset):
        self.fset = fset
        self.intypes = intypes
        self.outtype = outtype

        # create some ADFS
        self.ADFS = [self._add_adf() for _ in self.adf_range]

        # create the RPB
        self.RPB = Branch(intypes, outtype, fset)

    def _add_adf(self):
        # work out the signature
        outtype = type(random.choice(self.fset.random_node()))
        intypes = [type(random.choice(self.fset.random_node())) for _ in random.choice(self.adf_nargs)]
        # work out the fset - add arguments and other adfs
        adfset = copy.deepcopy(self.fset)
        for i, typ in enumerate(intypes):
            adfset.add_variable('A%d' % i, typ)
        return Branch(intypes, outtype, adfset)


class Branch(list):
    """A set of nodes that use a FunctionSet to produce a result.  A combination of deap PrimitiveSet
     and PrimitiveTree."""

    def __init__(self, intypes, outtype, fset):
        """
        :param intypes: list of types
        :param outtype: a type
        :param functionset: instance which contains all the possible functions and terminals
        """
        super(Branch, self).__init__(fset.grow(outtype))
        self.inputs = intypes
        self.output = outtype
        self.fset = fset

    def __str__(self):
        """lets see it in english"""
        return str("%s %s %s %s" % (self.inputs, self.output, self.fset, self.__repr__()))

    def grow(self):
        """ Add more primitives or terminals to the tree from the functionset """
        pass

    def size(self):
        """a measure of complexity relative to other branches"""
        pass

    def compile(self):
        """returns an expression which can be evaluated with different arguments"""
        pass

    def graft(self, twig):
        """attempt to apply another branch to part of this branch, raise exception if it's a silly attempt"""
        pass


from deap.gp import Terminal, Primitive

class Function(object):
    def __init__(self, func, intypes, outtype, symbol):
        self.func = func
        self.intypes = intypes
        self.outtype = outtype
        self.symbol = symbol

    def __repr__(self):
        return self.symbol


class DummyTerminal(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __repr__(self):
        return self.__get__(self, None)

    def __set__(self, instance, value):
        instance.value = value

    def __get__(self, instance, owner):
        if instance.value is None:
            return instance.name
        else:
            return instance.value


class FunctionSet(object):
    # a set of terminals
    terminals = set()
    # a set of primitives
    primitives = set()

    def __str__(self):
        return str(self.nodes)

    @property
    def nodes(self):
        """combined set of terminals and primitives"""
        return self.terminals | self.primitives

    def add_terminal(self, value):
        """Add a terminal to the set"""
        self.terminals.add(value)

    def add_dummy(self, name):
        """Add a dummy terminal to the set"""
        self.terminals.add(DummyTerminal(name))

    def add_primitive(self, func, intypes, outtype, symbol):
        """Add a primitive function to the set"""
        self.primitives.add(Function(func, intypes, outtype, symbol))

    def random_terminal(self, type_=None):
        """Return a terminal at random"""
        if type_ is None:
            return random.choice(list(self.terminals))
        else:
            return random.choice(list(self.terminals_of_type(type_)))

    def random_primitive(self, type_=None):
        """Return a random primitive"""
        if type_ is None:
            return random.choice(list(self.primitives))
        else:
            return random.choice(list(self.primitives_of_type(type_)))

    def terminals_of_type(self, type_):
        """return a set of terminals of type"""
        return [term for term in self.terminals if type(term) is type_]

    def primitives_of_type(self, type_):
        """return a set of primitives of type"""
        return [func for func in self.primitives if func.outtype == type_]

    def grow(self, type_, terminal_pb=0.5, max_=5):
        """return a list of nodes"""
        if max_ <= 1 or terminal_pb >= random.random() or not len(self.primitives_of_type(type_)):
            return [Terminal(self.random_terminal(type_), False, type_)]
        else:
            prim = self.random_primitive(type_)
            expr = [Primitive(prim.func.__name__, prim.intypes, prim.outtype)]
            for argtype in reversed(prim.intypes):
                expr += self.grow(argtype, terminal_pb, max_-1)
            return expr

    def to_pset(self, name, intypes_, outtype):
        pset = PrimitiveSetTyped(name, intypes_, outtype)
        for term in self.terminals:
            pset.addTerminal(term, type(term))
        for prim in self.primitives:
            pset.addPrimitive(prim.func, prim.intypes, prim.outtype, prim.func.__name__)
        return pset


# def genGrow(pset, max_, type_=None, prob=0.30):
#     """Generate an expression tree.
#     Branches can be of any height, provided they are not more than *max*.
#
#     :param pset: Primitive set from which primitives are selected.
#     :param max_: Maximum height of the produced tree.
#     :param prob: 0..1 the probability of a terminal (vs primitive) being placed at a node.
#     :param type_: The type that the tree should return when called.
#     :returns: An expression tree.
#     """
#
#     def random_terminal():
#         terminals = pset.terminals[type_]
#         if len(terminals) == 0:
#             raise DeadBranchError("No terminal of type '%s' is available" % type_)
#         else:
#             term = random.choice(terminals)
#             # and if it's actually a class then instantiate it
#             if isclass(term):
#                 term = term()
#             return [term]
#
#     if type_ is None:
#         type_ = pset.ret
#
#     # we're at the maximum depth, or there are no primitives to try
#     if max_ <= 1 or not len(pset.primitives[type_]):
#         return random_terminal()
#
#     # if chance dictates, return a terminal, if you can
#     try:
#         if random.random() < prob:
#             return random_terminal()
#     except DeadBranchError:
#         # No problem, press on, we'll try the prims.
#         pass
#
#     primitives = pset.primitives[type_].copy()
#     random.shuffle(primitives)
#     for prim in primitives:
#         try:
#             expr = [prim]
#             for arg in reversed(prim.args):
#                 expr += genGrow(pset, max_ - 1, arg, prob)
#             return expr
#         except DeadBranchError:
#             # ok, this prim is no good, but press on and try others
#             pass
#
#     # exhausted all terminals and primitives
#     raise DeadBranchError("Neither primitives nor terminals of type '%s' could be found" % type_)
