import operator
import unittest
import math
import uuid
import numpy as np

from app.ngp import Baseset
from app.ngp import Individual
from app.ngp import Population


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
        for tree, pset in prog.funcset:
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
        prog2 = Individual(bset, [int, int], int)
        for tree, pset in prog.funcset:
            print(pset.name, ":")
            print(pset.ins, '->', pset.ret)
            print(tree)
            print()
        for tree, pset in prog2.funcset:
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

        for tree, pset in ind.funcset:
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
        for tree, pset in prog.funcset:
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

        for tree, pset in ind.funcset:
            print(pset.name, ":", tree)
            # print(pset.ins, '->', pset.ret)
            # print('Terms:', [t.name for t in pset.terminals[np.ndarray]])

        result = ind.evaluate(m)
        print("\nR:", result)

        ind2 = Individual(bset, [np.ndarray], np.ndarray)

        for tree, pset in ind2.funcset:
            print(pset.name, ":", tree)
        result2 = ind2.evaluate(m)
        print("\nR:", result2)

    def test_pythagoras_matrix(self):
        """copy of the notebook (originally)"""

        # setup the training data
        SAMPLE_SIZE = 50
        PLANE_SIZE = 20.0
        RANDOMPOINTS = [PLANE_SIZE * np.random.random_sample((1, 2)) for _ in range(SAMPLE_SIZE)]

        # setup the baseset
        def getValue(ndarray, idx):
            """Return the indexed value from the 1x2 numpy array"""
            return ndarray[0][idx]


        square = lambda x: x ** 2
        sqrt = lambda x: math.sqrt(abs(x))

        bset = Baseset()
        bset.addEphemeralConstant('P', lambda: random.randint(0, 1), int)
        bset.addPrimitive(getValue, [np.ndarray, int], float, name="get")
        bset.addPrimitive(operator.add, [float, float], float, name="add")
        bset.addPrimitive(operator.sub, [float, float], float, name="sub")
        bset.addPrimitive(square, [float], float, name="square")
        bset.addPrimitive(sqrt, [float], float, name="sqrt")


        # setup the individuals
        Individual.INTYPES = [np.ndarray]
        Individual.OUTTYPE = float


        def evaluate(individual):
            """sum of application of all the random points"""
            program = individual.compile()
            score = 0
            try:
                for point in RANDOMPOINTS:
                    program_distance = program(point)
                    true_distance = math.hypot(point[0][0], point[0][1])
                    score += abs(true_distance - program_distance)
            except (OverflowError, RuntimeWarning):
                pass
            if math.isnan(score) or score == 0:
                score = float('inf')
            return score,
        Individual.evaluate = evaluate

        # run the evolution
        NUM_GENERATIONS = 5

        population = Population(bset)
        for generation in range(NUM_GENERATIONS):
            population.evolve()

        best = population[0]
        best.draw()
