import random
import numpy as np

from geneticprogramming import Individual
from geneticprogramming import NoMateException

from deap.tools import Statistics
from deap.tools import HallOfFame
from deap.tools import Logbook


class Population(list):
    """
    A collection of individuals
    """
    INDIVIDUAL_CLASS = Individual
    POPULATION_SIZE = 100
    CLONE_BEST = 5
    MAX_MATE_ATTEMPTS = 10
    MATE_MUTATE_CLONE = (80, 18, 2)

    def __init__(self, bset):
        self.bset = bset
        pop = [Population.INDIVIDUAL_CLASS(self.bset) for _ in range(self.POPULATION_SIZE)]
        super(Population, self).__init__(pop)

        self.stats = Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

        self.logbook = Logbook()
        self.logbook.header = ['gen'] + self.stats.fields

        self.hof = HallOfFame(1)
        self.generation = 0

        # do an initial evaluation
        for ind in self:
            ind.fitness.values = ind.evaluate()

    def select(self, k):
        """Probablistic select *k* individuals among the input *individuals*. The
        list returned contains references to the input *individuals*.

        :param k: The number of individuals to select.
        :returns: A list containing k individuals.

        The individuals returned are randomly selected from individuals according
        to their fitness such that the more fit the individual the more likely
        that individual will be chosen.  Less fit individuals are less likely, but
        still possibly, selected.
        """
        # adjusted pop is a list of tuples (adjusted fitness, individual)
        adjusted_pop = [(1.0 / (1.0 + i.fitness.values[0]), i) for i in self]

        # normalised_pop is a list of tuples (float, individual) where the float indicates
        # a 'share' of 1.0 that the individual deserves based on it's fitness relative to
        # the other individuals. It is sorted so the best chances are at the front of the list.
        denom = sum([fit for fit, ind in adjusted_pop])
        normalised_pop = [(fit / denom, ind) for fit, ind in adjusted_pop]
        normalised_pop = sorted(normalised_pop, key=lambda i: i[0], reverse=True)

        # randomly select with a fitness bias
        # FIXME: surely this can be optimized?
        selected = []
        for x in range(k):
            rand = random.random()
            accumulator = 0.0
            for share, ind in normalised_pop:
                accumulator += share
                if rand <= accumulator:
                    selected.append(ind)
                    break
        if len(selected) == 1:
            return selected[0]
        else:
            return selected

    def evolve(self):
        """
        Evolve this population by one generation
        """
        self.logbook.record(gen=self.generation, **self.stats.compile(self))
        self.hof.update(self)
        print(self.logbook.stream)

        # the best x of the population are cloned directly into the next generation
        sorted_pop = sorted(self, key=lambda i: i.fitness.values[0])
        offspring = sorted_pop[:self.CLONE_BEST]

        # rest of the population clone, mate, or mutate at random
        for idx in range(len(self) - self.CLONE_BEST):

            # decide how to alter this individual
            rand = random.random()

            if rand < self.MATE_MUTATE_CLONE[0]:  # MATE/CROSSOVER
                for _ in range(0, self.MAX_MATE_ATTEMPTS):
                    try:
                        receiver, contributor = self.select(2)
                        child = receiver.clone()
                        child.mate(contributor)
                        break
                    except NoMateException as ex:
                        raise ex
                else:  # fallback to a clone if we can't successfully mate
                    child = self.select(1)
                    print("No mate after %s attempts." % self.MAX_MATE_ATTEMPTS)

            elif rand < (self.MATE_MUTATE_CLONE[0] + self.MATE_MUTATE_CLONE[1]):  # MUTATE
                ind = self.select(1)
                child = ind.clone()
                child.mutate()

            else:  # CLONE
                child = self.select(1).clone()

            offspring.append(child)
        self[:] = offspring
        self.generation += 1

        # evaluate every individual
        for ind in self:
            if not len(ind.fitness.values):
                ind.fitness.values = ind.evaluate()
