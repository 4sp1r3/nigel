__author__ = 'johnmee'


class BirthError(Exception):
    """Unsuccessful in finding a compatible mate for, or mutating, an individual"""
    pass


from geneticprogramming.BaseSet import Baseset
from geneticprogramming.Individual import Individual
from geneticprogramming.Population import Population
