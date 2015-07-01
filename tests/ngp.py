import operator
import random
import unittest


from deap.gp import PrimitiveSetTyped as DEAPPrimitiveSetTyped
from deap.gp import PrimitiveTree as DEAPPrimitiveTree
from deap.gp import compileADF
from ourMods import genGrow, DeadBranchError


class GrowException(Exception):
    """Tried a bunch of times but could not grow a suitable tree from the given primitives"""
    pass


class Baseset(object):
    """
    Basic list of primitive functions to give to deap

    Add tuples to the list (func, intypes, outtype)
    Eg. (operator.add, [int, int], int)
    """
    # min, max number of input arguments to adfs
    nargs = (1, 5)

    def __init__(self, primitives):
        self.primitives = primitives
        self.adfsets = []

    def get_random_outtype(self):
        urn = list()
        for prim in self.primitives:
            urn.append(prim[2])
        return random.choice(urn)

    def get_random_intypes(self):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in self.primitives:
            for intype in prim[1]:
                urn.append(intype)

        # choose the number of args
        nargcount = random.randint(self.nargs[0], self.nargs[1])

        # range the args from 0 to ensure they're contiguous
        return [random.choice(urn) for _ in range(nargcount)]

    def getPrimitiveSet(self, name, intypes, outtype, prefix):
        """Return a deap primitive set corresponding to the base prims and any added adfs"""
        pset = DEAPPrimitiveSetTyped(name, intypes, outtype, prefix)
        for prim in self.primitives:
            pset.addPrimitive(prim[0], prim[1], prim[2])
        for adfset in self.adfsets:
            pset.addADF(adfset)
        return pset

    def addADF(self, pset):
        """Add a new primitive to subsequent primitivesets reflecting the meta properties of the pset.

        :param pset: needs to have 'name', 'ins', and 'ret' properties - so a PrimitiveSet will do
            but note the DEAP addADF routine doesn't use anything other than these args: it adds them as
            a primitive to the pset it is acting on, but in a slightly different way to normal prims
            (they're not added to the pset context).

            The 'name' probably should be unique, although DEAP do not assert this?
        """
        self.adfsets.append(pset)



def FunctionFactory(baseset, name, intypes=None, outtype=None, prefix='A'):
    """
    A DEAP PrimitiveTree which can construct itself randomly
    """
    # maximum size to grow the tree initially
    grow_max = 5
    # maximum number of times to attempt to grow a complete adf before abandoning
    max_grow_attempts = 50
    # terminal density during growth (1.0 = all terminals)
    grow_term_pb = 0.3

    # pick an outtype
    if outtype is None:
        outtype = baseset.get_random_outtype()

    # pick the intypes
    if intypes is None:
        intypes = baseset.get_random_intypes()

    pset = baseset.getPrimitiveSet(name, intypes, outtype, prefix)

    for _ in range(max_grow_attempts):
        try:
            tree = DEAPPrimitiveTree(genGrow(pset, grow_max, outtype, prob=grow_term_pb))
        except DeadBranchError:
            continue
        all_args_used = all([pset.mapping[arg] in tree for arg in pset.arguments])
        if all_args_used and len(tree) > 1:
            return tree, pset

    raise GrowException("Failed to grow a suitable ADF despite %s attempts." % max_grow_attempts)


class Individual(object):
    """
    An (individual) program of a random number of adfs and a Result Producing Branch (RPB)
    """
    max_adfs = 4

    def __init__(self, baseset, intypes, outtype):
        self.baseset = baseset
        self.intypes = intypes
        self.outtype = outtype

        # randomly decide the number of adfs
        nADFs = random.choice(list(range(self.max_adfs)))

        # generate the adfs
        self.ADFs = []
        for idx in range(nADFs):
            adf, pset = FunctionFactory(baseset, 'ADF%s' % idx)
            self.ADFs.append((adf, pset))
            baseset.addADF(pset)

        # generate the RPB
        tree, pset = FunctionFactory(baseset, "MAIN", self.intypes, self.outtype, prefix='IN')
        self.RPB = (tree, pset)

    @property
    def psets(self):
        return [adf[1] for adf in self.ADFs] + [self.RPB[1]]

    @property
    def trees(self):
        return [adf[0] for adf in self.ADFs] + [self.RPB[0]]

    def evaluate(self):
        func = compileADF(self.trees, self.psets)

        return 0


def nor(a, b):
    return (a | b) ^ 1


class NGPTestCase(unittest.TestCase):

    def test_silly_pset(self):
        # make the primitive set
        bset = Baseset([
            (operator.add, [int, int], int),
            (operator.sub, [int, int], int),
            #(nor, [bool, bool], bool),
        ])
        # declare adfs
        for n in range(5):
            tree, pset = FunctionFactory(bset, 'ADF')
            print("\nADF%s: " % n, pset.ret, pset.ins)
            print(tree)

    def test_generation_of_adfs(self):
        """generate lots of adfs and count how many use all their arguments"""
        # make the primitive set
        bset = Baseset([
            (operator.add, [int, int], float),
            (operator.add, [float, float], int),
            (operator.sub, [int, int], float),
            (operator.sub, [float, float], int),
            (operator.mul, [float, float], float),
            (operator.mul, [int, int], int),
        ])
        # declare adfs
        num = 1000
        for n in range(num):
            tree, pset = FunctionFactory(bset, 'TST%s' % n)
            print(len(pset.ins), pset.ins, '->', pset.ret)
            print(tree)

    def test_specific_inout(self):
        bset = Baseset([
            (operator.add, [int, int], int),
            (operator.sub, [int, int], int),
            (operator.mul, [float, float], float),
            (operator.truediv, [int, int], float),
        ])
        for _ in range(5):
            tree, pset = FunctionFactory(bset, 'TST', [int, int], float)
            print(tree)
            print(pset.mapping.keys())


class ProgramTestCase(unittest.TestCase):
    def test_program(self):
        # make the primitive set
        bset = Baseset([
            (operator.add, [int, int], float),
            (operator.add, [float, float], int),
            (operator.sub, [int, int], float),
            (operator.sub, [float, float], int),
            (operator.mul, [float, float], float),
            (operator.mul, [int, int], int),
        ])
        intypes = [int, float]
        outtype = float
        prog = Individual(bset, intypes, outtype)
        print("Program in/out:", intypes, outtype)
        print("Program prims:", prog.baseset)
        for idx, adf in enumerate(prog.ADFs):
            print("F%s:" % idx, adf[0])

        print("RPB:", prog.RPB[0])

        print(prog.evaluate())

        # print(prog.RPB[1].context.keys())
