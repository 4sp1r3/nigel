__author__ = 'johnmee'


class NoMateException(Exception):
    """Unsuccessful in finding a compatible mate for an individual"""
    pass


from geneticprogramming.BaseSet import Baseset
from geneticprogramming.Individual import Individual
from geneticprogramming.Population import Population
