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


class ADF(object):
    """
    A subroutine within a program
    """
    # range of input arguments
    nargs = (1,5)

    def __init__(self, pset):
        # a collection of primitive functions (just a list of Primitive types)
        self.pset = pset
        self.outtype = ADF.get_random_outtype(self.pset)
        self.intypes = ADF.get_random_intypes(self.pset, self.nargs)

    def get_primitivesettyped(self, name='ADF'):
        deap_pset = DEAPPrimitiveSetTyped(name, self.intypes, self.outtype)
        for prim in self.pset:
            deap_pset.addPrimitive(prim.func, prim.intypes, prim.outtype)
        return deap_pset

    @staticmethod
    def get_random_outtype(pset):
        urn = list()
        for prim in pset:
            urn.append(prim.outtype)
        return random.choice(urn)

    @staticmethod
    def get_random_intypes(pset, nargs):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in pset:
            for intype in prim.intypes:
                urn.append(intype)

        # choose the number of args
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
        success = 0
        num = 1000
        for n in range(num):
            adf = ADF(pset)
            print("ADF%s: " % n, len(adf.intypes), adf.intypes, '->', adf.outtype)
            deap_pset = adf.get_primitivesettyped()
            try:
                tree = DEAPPrimitiveTree(genGrow(deap_pset, 5, adf.outtype))
            except DeadBranchError as ex:
                print("ERROR:", ex)
                continue

            # for arg in deap_pset.arguments:
            #     term = deap_pset.mapping[arg]
            #     print(arg, term in tree)

            ok = all([deap_pset.mapping[arg] in tree for arg in deap_pset.arguments])
            if ok:
                success += 1

            print(ok, "->", tree)

        print("Success: %s of %s" % (success, num))
