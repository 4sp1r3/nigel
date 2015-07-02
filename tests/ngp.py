import operator
import unittest

from app.ngp import Baseset
from app.ngp import Individual


def nor(a, b):
    return (a | b) ^ 1


class NGPTestCase(unittest.TestCase):

    def test_silly_pset(self):
        # make the primitive set
        bset = Baseset([
            (operator.add, [int, int], float),
            (operator.sub, [float, float], int),
            #(nor, [bool, bool], bool),
        ])
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
            baseset = Baseset(bset)
            tree, pset = baseset.addFunction('TST%s' % n)
            print(len(pset.ins), pset.ins, '->', pset.ret)
            print(tree)

    def test_specific_inout(self):
        bset = Baseset([
            (operator.add, [int, int], int),
            (operator.sub, [int, int], int),
            (operator.mul, [float, float], float),
            (operator.truediv, [int, int], float),
        ])
        for idx in range(5):
            tree, pset = bset.addFunction('TST%s' % idx, [int, int], float, prefix='IN')
            print(tree, pset.mapping.keys())


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
        for tree, pset in prog.routines:
            print(pset.name, ":", pset.ins, '->', pset.ret)
            print("       ", tree)
        print(prog.evaluate(1, 1.0))
