import operator
import random
import unittest


from deap.gp import PrimitiveSetTyped as DEAPPrimitiveSetTyped
from deap.gp import PrimitiveTree as DEAPPrimitiveTree
from ourMods import genGrow, DeadBranchError


class Primitive(object):
    def __init__(self, func, intypes, outtype, label):
        self.func = func
        self.intypes = intypes
        self.outtype = outtype
        self.label = label

    def __repr__(self):
        return self.label


class GrowException(Exception): pass


class Program(object):
    """
    An (individual) program of a random number of adfs and a Result Producing Branch (RPB)
    """
    max_adfs = 4

    def __init__(self, pset, intypes, outtype):
        self.pset = pset
        self.intypes = intypes
        self.outtype = outtype

        # generate a random suite of ADFs
        self.ADFs = []
        for idx in range(random.choice(list(range(self.max_adfs)))):
            name = "F%s" % idx
            adf = ADF(self.pset)
            self.ADFs.append(adf)
            self.pset.append(Primitive(name, adf.intypes, adf.outtype, name))

        self.RPB = ADF(self.pset, self.intypes, self.outtype)


class ADF(object):
    """
    A subroutine within a program
    """
    # range of input arguments
    nargs = (1,5)
    # maximum size to grow the tree initially
    grow_max = 5
    # maximum number of times to attempt to grow a complete adf before abandoning
    max_grow_attempts = 50
    # terminal density during growth (1.0 = all terminals)
    grow_term_pb = 0.3

    def __init__(self, pset, intypes=None, outtype=None):
        # a collection of primitive functions (just a list of Primitive types)
        self.pset = pset

        if outtype is None:
            self.outtype = ADF.get_random_outtype(self.pset)
        else:
            self.outtype = outtype
        if intypes is None:
            self.intypes = ADF.get_random_intypes(self.pset, self.nargs)
        else:
            self.intypes = intypes

        self.tree = self.get_random_tree()

    def __repr__(self):
        return str(self.tree)

    def get_primitivesettyped(self, name='ADF'):
        deap_pset = DEAPPrimitiveSetTyped(name, self.intypes, self.outtype, 'A')
        for prim in self.pset:
            deap_pset.addPrimitive(prim.func, prim.intypes, prim.outtype, prim.label)
        return deap_pset

    def get_random_tree(self):
        """Return a deap primitive tree grown from the pset
        * one that uses all the dummy terminals
        * raise error if no acceptable tree after max_grow_attempts
        """
        deap_pset = self.get_primitivesettyped()
        for _ in range(ADF.max_grow_attempts):
            try:
                tree = DEAPPrimitiveTree(genGrow(deap_pset, ADF.grow_max, self.outtype, prob=ADF.grow_term_pb))
            except DeadBranchError:
                continue
            all_args_used = all([deap_pset.mapping[arg] in tree for arg in deap_pset.arguments])
            if all_args_used and len(tree) > 1:
                return tree
        raise GrowException("Failed to grow a suitable ADF despite %s attempts." % ADF.max_grow_attempts)

    @staticmethod
    def get_random_outtype(pset):
        urn = list()
        for prim in pset:
            urn.append(prim.outtype)
        return random.choice(urn)

    @staticmethod
    def get_random_intypes(pset, nargs=None):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in pset:
            for intype in prim.intypes:
                urn.append(intype)

        # choose the number of args
        if nargs is None or isinstance(nargs, tuple):
            nargs = random.randint(nargs[0], nargs[1])
        return [random.choice(urn) for _ in range(nargs)]



def nor(a, b):
    return (a | b) ^ 1


class NGPTestCase(unittest.TestCase):

    def test_silly_pset(self):
        # make the primitive set
        pset = [
            Primitive(operator.add, [int, int], int, '+i'),
            Primitive(operator.sub, [float, float], float, '+f'),
            Primitive(nor, [bool, bool], bool, '^'),
        ]
        # declare adfs
        for n in range(5):
            adf = ADF(pset)
            print("\nADF%s: " % n, adf.outtype, adf.intypes)
            deap_pset = adf.get_primitivesettyped()
            try:
                print(DEAPPrimitiveTree(genGrow(deap_pset, 5, adf.outtype)))
            except DeadBranchError as ex:
                print("ERROR:", ex)

    def test_success_rate_generating_full_adfs(self):
        """generate lots of adfs and count how many use all their arguments"""
        # make the primitive set
        pset = [
            Primitive(operator.add, [int, int], float, '+i'),
            Primitive(operator.add, [float, float], int, '+i'),
            Primitive(operator.sub, [int, int], float, '-f'),
            Primitive(operator.sub, [float, float], int, '-i'),
            Primitive(operator.mul, [float, float], float, '*f'),
            Primitive(operator.mul, [int, int], int, '*i'),
        ]
        # declare adfs
        num = 1000
        for n in range(num):
            adf = ADF(pset)
            print("ADF%s: " % n, len(adf.intypes), adf.intypes, '->', adf.outtype)
            print(adf.tree)

    def test_specific_inout(self):
        pset = [
            Primitive(operator.add, [int, int], int, '+'),
            Primitive(operator.sub, [int, int], int, '-'),
            Primitive(operator.mul, [float, float], float, '*'),
            Primitive(operator.truediv, [int, int], float, '/'),
        ]
        intypes = ADF.get_random_intypes(pset, 2)
        outtype = ADF.get_random_outtype(pset)
        adf = ADF(pset, intypes, outtype)
        print(intypes, outtype)
        print(adf)



class ProgramTestCase(unittest.TestCase):
    def test_program(self):
        # make the primitive set
        pset = [
            Primitive(operator.add, [int, int], float, '+i'),
            Primitive(operator.add, [float, float], int, '+i'),
            Primitive(operator.sub, [int, int], float, '-f'),
            Primitive(operator.sub, [float, float], int, '-i'),
            Primitive(operator.mul, [float, float], float, '*f'),
            Primitive(operator.mul, [int, int], int, '*i'),
        ]
        intypes = ADF.get_random_intypes(pset, 2)
        outtype = ADF.get_random_outtype(pset)
        prog = Program(pset, intypes, outtype)
        print("Program in/out:", intypes, outtype)
        print("Program prims:", prog.pset)
        for idx, adf in enumerate(prog.ADFs):
            print("F%s:" % idx, len(adf.intypes), adf)
        print("RPB:", prog.RPB)
