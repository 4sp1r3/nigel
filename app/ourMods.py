import random


def selProbablistic(individuals, k):
    """Select *k* individuals among the input *individuals*. The
    list returned contains references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list containing k individuals.

    The individuals returned are randomly selected from individuals according
    to their fitness such that the more fit the individual the more likely
    that individual will be chosen.  Less fit individuals are less likely, but
    still possibly, selected.
    """
    # be sure to evaluate the individuals first
    for ind in individuals:
        if not getattr(ind.fitness, "values", False):
                raise Exception("Invalid fitness: you have to ensure all the individuals have fitness values "
                                "before calling this.")

    # adjusted pop is a list of tuples (adjusted fitness, individual)
    adjusted_pop = [(1.0 / (1.0 + i.fitness.values[0]), i) for i in individuals]

    # normalised_pop is a list of tuples (float, individual) where the float indicates
    # a 'share' of 1.0 that the individual deserves based on it's fitness relative to
    # the other individuals. It is sorted so the best chances are at the front of the list.
    denom = sum([fit for fit, ind in adjusted_pop])
    normalised_pop = [(fit/denom, ind) for fit, ind in adjusted_pop]
    normalised_pop = sorted(normalised_pop, key=lambda x: x[0], reverse=True)

    # randomly select with a fitness bias
    selected = []
    for x in range(k):
        rand = random.random()
        accumulator = 0.0
        for share, ind in normalised_pop:
            accumulator += share
            if rand <= accumulator:
                selected.append(ind)
                break
    return selected
