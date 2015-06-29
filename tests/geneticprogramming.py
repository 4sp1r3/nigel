import unittest
import operator
from app.ourMods import adfdraw

from app.geneticprogramming import Individual
from app.geneticprogramming import FunctionSet
from app.geneticprogramming import Branch


def nor(a, b):
    return (a | b) ^ 1


class FunctionSetTestCase(unittest.TestCase):

    def test_functionset(self):
        fset = FunctionSet()
        fset.add_primitive(nor, [bool, bool], bool, '^')
        fset.add_primitive(operator.add, [int, int], int, '+')
        fset.add_terminal(False)
        fset.add_terminal(True)
        fset.add_terminal(12)

        print("Terms:", fset.terminals)
        print("Funcs:", fset.primitives)
        print("All:  ", fset.nodes, fset)
        print("Random:  ", fset.random_terminal(), fset.random_primitive())
        print("RType: ", fset.random_terminal(bool), fset.random_primitive(int))

        print("Types: ", fset.terminals_of_type(bool), fset.terminals_of_type(int))
        print("Types: ", fset.primitives_of_type(bool), fset.primitives_of_type(int))

        twig = fset.grow(int)
        print(twig)


class BranchTestCase(unittest.TestCase):
    def setUp(self):
        fset = FunctionSet()
        fset.add_primitive(nor, [bool, bool], bool, '^')
        fset.add_terminal(False)
        fset.add_terminal(True)
        self.fset = fset

    def test_branch(self):
        branch = Branch([bool, bool], bool, self.fset)
        print(branch)


class IndividualTestCase(unittest.TestCase):

    def test_creation(self):
        primitives = [(nor, 2)]
        growth = (30, 5, 3)
        adf_range = (1, 5)
        adf_nargs = (0, 2)
        Ind_cls = Individual(primitives, adf_range, adf_nargs, growth)
        ind = Ind_cls()
        print(str(ind))


class PopulationTestCase(unittest.TestCase):
    def test_create(self): pass
    def test_sort(self): pass
    def test_select(self): pass
    def test_best(self): pass
    def test_generation(self): pass




class SomeTestCase(unittest.TestCase):
    """
    Run the adf version of five parity
    """
    def test_one(self):
        from app.madffiveparity import main
        pop, stats, hof = main(gens=20, pop_size=300)
        adfdraw(hof[0])


# from app.geneticprogramming import FunctionSet
# class FunctionSetTestCase(unittest.TestCase):
#     """
#
#     """
#     def test_terminals(self):
#         fset = FunctionSet()
#         fset.add_terminal(8)
#         fset.add_terminal(8)
#         self.assertIn(8, fset.terminals)
#         self.assertEqual(1, len(fset.terminals))
#
#         print(fset.terminals)
#         print(fset.random_terminal())
#
#     def test_primitives(self):
#         fset = FunctionSet()
#         fset.add_primitive(operator.add, [float, float], float, '+')
#         p = fset.random_primitive()
#         print(p)
#
#     def test_growth(self):
#         fset = FunctionSet()
#         fset.add_terminal(8)
#         print(fset.grow())
#
#     def test_something(self):
#         import math, operator
#
#         square = lambda x: x ** 2
#         sqrt = lambda x: math.sqrt(abs(x))
#         to_float = lambda i: float(i)
#
#         primitives = [
#             (operator.add, [float, float], float, '+'),
#             (operator.sub, [float, float], float, '-'),
#             (square, [float], float, '\u00B2'),
#             (sqrt, [float], [float], "\u221A"),
#             (to_float, [int], [float], "\u211C")
#         ]
#
#         terminals = [
#             ('A0', int),
#             ('A1', float)
#         ]
#
#         from app.geneticprogramming import FunctionSet
#         fset = FunctionSet(primitives)
#         fset.add(primitives)
