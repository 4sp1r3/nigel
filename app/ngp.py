import random

from deap.gp import PrimitiveSetTyped
from deap.gp import PrimitiveTree
from deap.gp import compileADF
from app.ourMods import genGrow, DeadBranchError


class GrowException(Exception):
    """Tried a bunch of times but could not grow a suitable tree from the given primitives"""
    pass


class Baseset(object):
    """
    Basic list of primitive functions to give to deap
    """
    # min, max number of input arguments to adfs
    nargs = (1, 5)

    def __init__(self, primitives):
        """
        :param primitives: a list of primitives as tuples (func, intypes, outtype)
        Eg. (operator.add, [int, int], int)
        """
        self.primitives = primitives
        # collection of psets; one for each ADF.
        self.psets = []

    def get_random_outtype(self):
        urn = list()
        for prim in self.primitives:
            urn.append(prim[2])
        for adf in self.psets:
            urn.append(adf.ret)
        return random.choice(urn)

    def get_random_intypes(self):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in self.primitives:
            for intype in prim[1]:
                urn.append(intype)
        for adf in self.psets:
            for intype in adf.ins:
                urn.append(intype)

        # choose the number of args
        nargcount = random.randint(self.nargs[0], self.nargs[1])

        # range the args from 0 to ensure they're contiguous
        return [random.choice(urn) for _ in range(nargcount)]

    def getPrimitiveSet(self, name, intypes, outtype, prefix):
        """Return a deap primitive set corresponding to the base prims and any added adfs"""
        pset = PrimitiveSetTyped(name, intypes, outtype, prefix)
        for prim in self.primitives:
            pset.addPrimitive(prim[0], prim[1], prim[2])
        for adfset in self.psets:
            pset.addADF(adfset)
        return pset

    def addFunction(self, name, intypes=None, outtype=None, prefix='A'):
        """
        Create and add a new function
        :param name: a unique name for the function (or non-unique if that's a deliberate intention)
        :param intypes: list of input types
        :param outtype: the output type
        :param prefix: label for the input terminals
        :return: a tuple of the grown tree and the pset used to produce it
        """
        # maximum size to grow the tree initially
        grow_max = 5
        # terminal density during growth (1.0 = all terminals)
        grow_term_pb = 0.3
        # maximum number of times to attempt to grow a complete adf before abandoning
        max_grow_attempts = 50
        # maximum number of signatures to try before ultimately giving up
        max_signature_attempts = 1000

        # pick an outtype
        if outtype is None:
            outtype = self.get_random_outtype()

        # pick the intypes
        if intypes is None:
            intypes = self.get_random_intypes()

        for _ in range(max_signature_attempts):
            pset = self.getPrimitiveSet(name, intypes, outtype, prefix)
            for _ in range(max_grow_attempts):
                try:
                    tree = PrimitiveTree(genGrow(pset, grow_max, outtype, prob=grow_term_pb))
                except DeadBranchError:
                    continue
                all_args_used = all([pset.mapping[arg] in tree for arg in pset.arguments])
                if all_args_used and len(tree) > 1:
                    self.psets.append(pset)
                    return tree, pset
            else:
                # try a different signature
                outtype = self.get_random_outtype()
                intypes = self.get_random_intypes()

        # we tried but no valid tree could be grown
        raise GrowException("No ADF tree could be grown after %s attempts with different ADF signatures, "
                            "where %s attempts were made to grow within each signature. Please review your "
                            "definitions of the primitives and retry" % (max_signature_attempts, max_grow_attempts))


class Individual(object):
    """
    An (individual) program of a random number of adfs and a Result Producing Branch (RPB)
    """
    max_adfs = 4

    def __init__(self, baseset, intypes, outtype):
        """
        :param baseset: a Baseset object with the primitives already loaded
        :param intypes: list of input types
        :param outtype: the output type
        """
        self.baseset = baseset
        self.intypes = intypes
        self.outtype = outtype

        # the primitive trees that make up this program
        self.routines = []

        # randomly decide the number of adfs
        nADFs = random.choice(list(range(self.max_adfs)))

        # generate the adfs
        for idx in range(nADFs):
            name = 'ADF%s' % idx
            self.routines.append(baseset.addFunction(name))

        # generate the RPB
        self.routines.append(baseset.addFunction("MAIN", self.intypes, self.outtype, prefix='IN'))

    def evaluate(self, *args):
        trees, psets = zip(*self.routines)
        func = compileADF(trees, psets)
        return func(*args)
