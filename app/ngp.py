import random

from deap.gp import PrimitiveSetTyped
from deap.gp import PrimitiveTree
from app.ourMods import DeadBranchError
from app.ourMods import genGrow


class GrowException(Exception):
    """Tried a bunch of times but could not grow a suitable tree from the given primitives"""
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


class FunctionSet(object):
    """
    The set of functions of an individual
    """
    # min, max number of input arguments to adfs
    nargs = (1, 5)

    def __init__(self, baseset):
        # a reference to the baseset of primitives, terminals and ephemerals
        self.baseset = baseset
        # a collection of function trees
        self.trees = []
        # collection of psets; one for each ADF.
        self.psets = []

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
        nargcount = random.randint(self.nargs[0], self.nargs[1])

        # range the args from 0 to ensure they're contiguous
        return [random.choice(urn) for _ in range(nargcount)]

    def get_primitive_set(self, name, intypes, outtype, prefix):
        """Return a deap primitive set corresponding to the base prims and any added adfs"""
        pset = PrimitiveSetTyped(name, intypes, outtype, prefix)
        for term in self.baseset.terminals:
            pset.addTerminal(term[0], term[1], term[2])
        for idx in range(len(self.baseset.ephemerals)):
            name, value = self.baseset.get_ephemeral_instance(idx)
            pset.addTerminal(value, type(value), name)
        for prim in self.baseset.primitives:
            pset.addPrimitive(prim[0], prim[1], prim[2])
        for adfset in self.psets:
            pset.addADF(adfset)
        return pset

    def add_function(self, name, intypes=None, outtype=None, prefix='A'):
        """
        Create and add a new function
        :param name: a unique name for the function (or non-unique if that's a deliberate intention)
        :param intypes: list of input types
        :param outtype: the output type
        :param prefix: label for the input terminals
        :return: undefined
        """
        # maximum size to grow the tree initially
        grow_max = 5
        # terminal density during growth (1.0 = all terminals)
        grow_term_pb = 0.3
        # maximum number of times to attempt to grow a complete adf before abandoning
        max_grow_attempts = 50
        # maximum number of signatures to try before ultimately giving up
        max_signature_attempts = 1000

        flexible_signature = (outtype is None and intypes is None)

        # pick an outtype
        if outtype is None:
            outtype = self.get_random_outtype()

        # pick the intypes
        if intypes is None:
            intypes = self.get_random_intypes()

        for _ in range(max_signature_attempts):
            pset = self.get_primitive_set(name, intypes, outtype, prefix)
            for _ in range(max_grow_attempts):
                try:
                    tree = PrimitiveTree(genGrow(pset, grow_max, outtype, prob=grow_term_pb))
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
                                        (max_grow_attempts, intypes, outtype))
        else:
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
        self.intypes = intypes
        self.outtype = outtype

        # the primitive trees that make up this program
        self.funcset = FunctionSet(baseset)

        # randomly decide the number of adfs
        nADFs = random.choice(list(range(self.max_adfs)))

        # generate the adfs
        for idx in range(nADFs):
            name = 'ADF%s' % idx
            self.funcset.add_function(name)

        # generate the RPB
        self.funcset.add_function("MAIN", self.intypes, self.outtype, prefix='IN')

    def evaluate(self, *args):
        # removes deap's compile and compileADF so we can see what it's doing.
        # for each routine, add previous routines to the context, codify the routine and call it,
        #  then add it to the list of routines in context. Return the evaluated solution.
        adfdict = {}
        func = None
        for subexpr, pset in self.funcset:
            pset.context.update(adfdict)
            code = str(subexpr)
            if len(pset.arguments) > 0:
                adfargs = ",".join(arg for arg in pset.arguments)
                code = "lambda {args}: {code}".format(args=adfargs, code=code)
            func = eval(code, pset.context, {})
            adfdict.update({pset.name: func})

        return func(*args)
