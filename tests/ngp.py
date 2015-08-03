import operator
import unittest
import math
import uuid
import numpy as np

from geneticprogramming import Individual
from geneticprogramming import Population
from geneticprogramming import Baseset


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
            bset.add_primitive(*prim)

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
                baseset.add_primitive(*prim)
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
            baseset.add_primitive(*prim)
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
            bset.add_primitive(*prim)
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
        bset.add_ephemeral(str(uuid.uuid4()), lambda: random.randint(0, 10), int)
        bset.add_primitive(operator.gt, [int, int], bool)
        bset.add_primitive(operator.add, [int, int], int)
        bset.add_primitive(ifthenelse, [bool, types.FunctionType, types.FunctionType], object)
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
        bset.add_ephemeral(str(uuid.uuid4()), lambda: np.random.rand(1, 3), np.ndarray)
        bset.add_primitive(operator.add, [int, int], int)

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
            baseset.add_primitive(*prim)

        prog = Individual(baseset, [int, int], int)
        for tree, pset in prog.funcset:
            print(pset.name, ":", pset.ins, '->', pset.ret)
            print("       ", tree)
        print('Score:', prog.evaluate(2, 1.0))
        print('-----\n\n')


from deap.gp import Primitive, Terminal, PrimitiveSetTyped

class CrossoverTestCase(unittest.TestCase):
    def test_iscompatible_adf(self):
        """
        Ensure the routine correctly distinguishes two ADF0s which have different input arguments
        """
        # two adfs, same name, different signatures
        adf_int = PrimitiveSetTyped("ADF0", [int, float], float)
        adf_float = PrimitiveSetTyped("ADF0", [float, float], int)

        # two psets, one with the float adf, the other with the int adf
        pset_int = PrimitiveSetTyped("MAIN", [float], bool)
        pset_int.addADF(adf_int)
        pset_float = PrimitiveSetTyped("MAIN", [float], bool)
        pset_float.addADF(adf_float)

        # the int adf is compatible with the int pset
        self.assertTrue(Individual.is_compatible(pset_int.mapping["ADF0"], pset_int))
        # the float adf is not compatible with the int pset
        self.assertFalse(Individual.is_compatible(pset_float.mapping["ADF0"], pset_int))
        # the float adf is compatible with the float pset
        self.assertTrue(Individual.is_compatible(pset_float.mapping["ADF0"], pset_float))
        # the int adf is not compatible with the float pset
        self.assertFalse(Individual.is_compatible(pset_int.mapping["ADF0"], pset_float))

        # the int pset has an unnamed float terminal
        pset_int.addTerminal(0, int)
        terms = [term for type_ in pset_int.terminals for term in pset_int.terminals[type_]]
        self.assertTrue(all([Individual.is_compatible(term, pset_int) for term in terms]))


class MatrixTestCase(unittest.TestCase):

    def test_matrix(self):
        """play with matrixes"""
        bset = Baseset()
        bset.add_ephemeral('EMatrix1', lambda: np.random.rand(2, 2), np.ndarray)
        bset.add_ephemeral('EMatrix2', lambda: np.random.rand(2, 2), np.ndarray)
        bset.add_primitive(operator.add, [np.ndarray, np.ndarray], np.ndarray)
        bset.add_primitive(operator.sub, [np.ndarray, np.ndarray], np.ndarray)

        Individual.INTYPES = [np.ndarray]
        Individual.OUTTYPE = np.ndarray
        ind = Individual(bset)

        m = np.random.rand(2, 2)
        print("M:", m, '\n')

        for tree, pset in zip(ind.trees, ind.psets):
            print(pset.name, ":", tree)
            # print(pset.ins, '->', pset.ret)
            # print('Terms:', [t.name for t in pset.terminals[np.ndarray]])

        result = ind.evaluate(m)
        print("\nR:", result)

        Individual.INTYPES = [np.ndarray]
        Individual.OUTTYPE = np.ndarray
        ind2 = Individual(bset)

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
        bset.add_ephemeral('P', lambda: random.randint(0, 1), int)
        bset.add_primitive(getValue, [np.ndarray, int], float, name="get")
        bset.add_primitive(operator.add, [float, float], float, name="add")
        bset.add_primitive(operator.sub, [float, float], float, name="sub")
        bset.add_primitive(square, [float], float, name="square")
        bset.add_primitive(sqrt, [float], float, name="sqrt")

        def if_then_else(input, output1, output2):
            if input:
                return output1
            else:
                return output2

        # bset.add_primitive(operator.lt, [float, float], bool, name="lt")
        bset.add_primitive(operator.eq, [float, float], bool, name="gt")
        bset.add_primitive(if_then_else, [bool, float, float], float, name="IF")

        # bset.add_terminal(False, bool)
        # bset.add_terminal(True, bool)

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
                score = 100000
            # accumulate the number of nodes actually used during a run by calling the adfs in the rpb
            nodes = sum([len(tree) for tree in individual.trees])
            modifier = 1 + (-2 ** - (nodes / 250))
            return score + modifier,
        Individual.evaluate = evaluate


        # run the evolution
        Population.POPULATION_SIZE = 500  # Number of individuals in a generation
        Population.MATE_MUTATE_CLONE = (70, 25, 5)  # ratio of individuals to mate, mutate, or clone
        Population.CLONE_BEST = 1  # Number of best individuals to seed directly into offspring

        Individual.MAX_ADFS = 0  # The maximum number of ADFs to generate
        Individual.ADF_NARGS = (1, 5)  # min, max number of input arguments to adfs
        Individual.GROWTH_TERM_PB = 0.3  # Probability of terminal when growing:
        Individual.GROWTH_MAX_INIT_DEPTH = 12  # Maximum depth of initial growth
        Individual.GROWTH_MAX_MUT_DEPTH = 5  # Maximum depth of mutation growth

        population = Population(bset)
        while population[0].fitness.values[0] >= 1.0:
            population.evolve()

        best = population[0]
        best.draw()

    def test_pythagoras_matrix2(self):
        """copy of the copy of the notebook"""

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
        bset.add_ephemeral('EM', lambda: np.random.rand(1, 2), np.ndarray)
        bset.add_ephemeral('EF', lambda: random.random(), float)
        bset.add_ephemeral('EI', lambda: random.randint(0, 1), int)

        bset.add_primitive(getValue, [np.ndarray, int], float, name="get")
        bset.add_primitive(operator.add, [float, float], float, name="add")
        bset.add_primitive(operator.sub, [float, float], float, name="sub")
        bset.add_primitive(square, [float], float, name="square")
        bset.add_primitive(sqrt, [float], float, name="sqrt")

        def if_then_else(input, output1, output2):
            if input:
                return output1
            else:
                return output2

        bset.add_primitive(operator.lt, [float, float], bool, name="lt")
        bset.add_primitive(if_then_else, [bool, float, float], float, name="IF")

        # bset.add_terminal(False, bool)
        # bset.add_terminal(True, bool)

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
                score = 100000
            # accumulate the number of nodes actually used during a run by calling the adfs in the rpb
            nodes = sum([len(tree) for tree in individual.trees])
            modifier = 1 + (-2 ** - (nodes / 250))
            return score + modifier,

        Individual.evaluate = evaluate


        # run the evolution
        Population.POPULATION_SIZE = 50  # Number of individuals in a generation
        Population.MATE_MUTATE_CLONE = (70, 25, 5)  # ratio of individuals to mate, mutate, or clone
        Population.CLONE_BEST = 1  # Number of best individuals to seed directly into offspring

        Individual.MAX_ADFS = 0  # The maximum number of ADFs to generate
        Individual.ADF_NARGS = (1, 5)  # min, max number of input arguments to adfs
        Individual.GROWTH_TERM_PB = 0.3  # Probability of terminal when growing:
        Individual.GROWTH_MAX_INIT_DEPTH = 12  # Maximum depth of initial growth
        Individual.GROWTH_MAX_MUT_DEPTH = 5  # Maximum depth of mutation growth

        population = Population(bset)
        for gen in range(2):
            population.evolve()
            if population[0].fitness.values[0] < 1.0:
                break

        best = population[0]
        best.draw()
