import operator
import unittest
import uuid
import numpy as np

from app.ngp import Baseset
from app.ngp import Individual


def nor(a, b):
    return (a | b) ^ 1


class NGPTestCase(unittest.TestCase):

    def test_silly_pset(self):
        # make the primitive set
        bset = Baseset()
        for prim in [
            (operator.add, [int, int], float),
            (operator.sub, [float, float], int),
            # (nor, [bool, bool], bool),
        ]:
            bset.addPrimitive(*prim)

        # declare adfs
        for n in range(5):
            tree, pset = bset.addFunction('ADF')
            print("\nADF%s: " % n, pset.ret, pset.ins)
            print(tree)

    def test_generation_of_adfs(self):
        """generate lots of adfs and count how many use all their arguments"""
        # make the primitive set
        bset = [
            (operator.add, [int, int], float),
            (operator.add, [float, float], int),
            (operator.sub, [int, int], float),
            (operator.sub, [float, float], int),
            (operator.mul, [float, float], float),
            (operator.mul, [int, int], int),
        ]
        # declare adfs
        num = 1000
        for n in range(num):
            baseset = Baseset()
            for prim in bset:
                baseset.addPrimitive(*prim)
            tree, pset = baseset.addFunction('TST%s' % n)
            print(len(pset.ins), pset.ins, '->', pset.ret)
            print(tree)

    def test_specific_inout(self):
        bset = [
            (operator.add, [int, int], int),
            (operator.sub, [int, int], int),
            (operator.mul, [float, float], float),
            (operator.truediv, [int, int], float),
        ]
        baseset = Baseset()
        for prim in bset:
            baseset.addPrimitive(*prim)
        for idx in range(5):
            tree, pset = baseset.addFunction('TST%s' % idx, [int, int], float, prefix='IN')
            print(tree, pset.mapping.keys())


import types
import random
from functools import partial


class ProgramTestCase(unittest.TestCase):
    def test_program(self):
        # make the primitive set
        bset = Baseset()
        for prim in [
            (operator.add, [int, int], float),
            (operator.add, [float, float], int),
            (operator.sub, [int, int], float),
            (operator.sub, [float, float], int),
            (operator.mul, [float, float], float),
            (operator.mul, [int, int], int),
        ]:
            bset.addPrimitive(*prim)
        intypes = [int, float]
        outtype = float
        prog = Individual(bset, intypes, outtype)
        for tree, pset in prog.routines:
            print(pset.name, ":", pset.ins, '->', pset.ret)
            print("       ", tree)
        print(prog.evaluate(1, 1.0))

    def test_grow_predicate_routines(self):
        """try some tricky primitives like forloops and if-then-else"""

        def part(func, arg1, arg2):
            return partial(func, arg1, arg2)

        def ifthenelse(cond, part1, part2):
            if cond:
                return part1()
            else:
                return part2()

        bset = Baseset()
        bset.addEphemeralConstant(str(uuid.uuid4()), lambda: random.randint(0, 10), int)
        bset.addPrimitive(operator.gt, [int, int], bool)
        bset.addPrimitive(operator.add, [int, int], int)
        bset.addPrimitive(ifthenelse, [bool, types.FunctionType, types.FunctionType], object)
        # bset.addPrimitive(part, [types.FunctionType, object, object], types.FunctionType)

        prog = Individual(bset, [int, int], int)
        for tree, pset in prog.routines:
            print(pset.name, ":")
            print(pset.ins, '->', pset.ret)
            print(tree)
            print()

        print(prog.evaluate(-10, 5))
        print(prog.evaluate(1, 2))
        print(prog.evaluate(3, 4))

    def test_integers(self):
        """play with matrixes"""
        bset = Baseset()
        bset.addEphemeralConstant(str(uuid.uuid4()), lambda: np.random.rand(1, 3), np.ndarray)
        bset.addPrimitive(operator.add, [int, int], int)

        ind = Individual(bset, [int], int)

        for tree, pset in ind.routines:
            print(pset.name, ":")
            print(pset.ins, '->', pset.ret)
            print(tree)
            print()

        m = np.random.rand(1, 3)
        print("M:", m)
        print("R:", ind.evaluate(m))

    def test_more_integers(self):
        """Does it respect the types we're telling it to use?"""
        primset = [
            (operator.add, [int, int], int),
            # (operator.sub, [int, float], int),
            # (operator.mul, [float, float], float),
        ]
        baseset = Baseset()
        for prim in primset:
            baseset.addPrimitive(*prim)

        prog = Individual(baseset, [int, int], int)
        for tree, pset in prog.routines:
            print(pset.name, ":", pset.ins, '->', pset.ret)
            print("       ", tree)
        print('Score:', prog.evaluate(2, 1.0))
        print('-----\n\n')


class MatrixTestCase(unittest.TestCase):

    def test_matrix(self):
        """play with matrixes"""
        bset = Baseset()
        bset.addEphemeralConstant('EMatrix1', lambda: np.random.rand(2, 2), np.ndarray)
        bset.addEphemeralConstant('EMatrix2', lambda: np.random.rand(2, 2), np.ndarray)
        bset.addPrimitive(operator.add, [np.ndarray, np.ndarray], np.ndarray)
        bset.addPrimitive(operator.sub, [np.ndarray, np.ndarray], np.ndarray)

        ind = Individual(bset, [np.ndarray], np.ndarray)

        m = np.random.rand(2, 2)
        print("M:", m, '\n')

        for tree, pset in ind.routines:
            print(pset.name, ":", tree)
            # print(pset.ins, '->', pset.ret)
            # print('Terms:', [t.name for t in pset.terminals[np.ndarray]])

        result = ind.evaluate(m)
        print("\nR:", result)
