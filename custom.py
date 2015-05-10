import sys
import random
from inspect import isclass
from operator import attrgetter
import matplotlib.pyplot as plt
import networkx as nx

from deap import tools
from deap.gp import graph as gph
from deap.gp import __type__
from deap.algorithms import varAnd


# something that given a population normalizes the fitness scores 0..1
# class NormalisedPopulationWeightedFitness(Fitness):
#     pass
#
#
# def selWeighted(individuals, k):
#     """Select *k* individuals among the input *individuals*. The
#     list returned contains references to the input *individuals*.
#
#     :param individuals: A list of individuals to select from.
#     :param k: The number of individuals to select.
#     :returns: A list containing k individuals.
#
#     The individuals returned are randomly selected from individuals according
#     to their fitness such that the more fit the individual the more likely
#     that individual will be chosen.  Less fit individuals are less likely, but
#     still possibly, selected.
#     """
#     # Evaluate the individuals with an invalid fitness
#     # for ind in individuals:
#     #     if not getattr(ind.fitness, "values", False):
#     #         raise Exception("Invalid fitness: you have to ensure all the individuals have fitness values "
#     #                         "before calling this.")
#     # pop_fitness = sum([i.fitness.values[0] for i in individuals])
#     # denom = 1 +
#     #
#     return sorted(individuals, key=attrgetter("fitness"), reverse=True)[:k]


def generate(pset, min_, max_, condition, type_=__type__):
    """Generate a Tree as a list of list. The tree is build
    from the root to the leaves, and it stop growing when the
    condition is fulfilled.

    :param pset: A primitive set from wich to select primitives of the trees.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param condition: The condition is a function that takes two arguments,
                      the height of the tree to build and the current
                      depth in the tree.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) no return type is enforced.
    :returns: A grown tree with leaves at possibly different depths
              dependending on the condition function.


    DUMMY NODE ISSUES

    DEAP will only place terminals if we're at the bottom of a branch.
    This creates two issues:
    1. A primitive that takes other primitives as inputs could be placed at the
        second to last layer.
        SOLUTION: You need to allow the tree to end whenever the height condition is met,
                    so create "dummy" terminals for every type possible in the tree.
    2. A primitive that takes terminals as inputs could be placed above the second to
        last layer.
        SOLUTION: You need to allow the tree to continue extending the branch until the
                    height condition is met, so create "dummy" primitives that just pass
                    through the terminal types.

    These "dummy" terminals and "dummy" primitives introduce unnecessary and sometimes
    nonsensical solutions into populations. These "dummy" nodes can be eliminated
    if the height requirement is relaxed.


    HOW TO PREVENT DUMMY NODE ISSUES

    Relaxing the height requirement:
    When at the bottom of the branch, check for terminals first, then primitives.
        When checking for primitives, skirt the height requirement by adjusting
        the branch depth to be the second to last layer of the tree.
        If neither a terminal or primitive fits this node, then throw an error.
    When not at the bottom of the branch, check for primitives first, then terminals.

    Issue with relaxing the height requirement:
    1. Endless loops are possible when primitive sets have any type loops.
        A primitive with an output of one type may not take an input type of
        itself or a parent type.
        SOLUTION: A primitive set must be well-designed to prevent those type loops.

    """
    expr = []
    height = random.randint(min_, max_)
    stack = [(0, type_)]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        # At the bottom of the tree
        if condition(height, depth):
            # Try finding a terminal
            try:
                term = random.choice(pset.terminals[type_])

                if isclass(term):
                    term = term()
                expr.append(term)
                # No terminal fits
            except:
                # So pull the depth back one layer, and start looking for primitives
                try:
                    depth -= 1
                    prim = random.choice(pset.primitives[type_])

                    expr.append(prim)
                    for arg in reversed(prim.args):
                        stack.append((depth + 1, arg))

                        # No primitive fits, either - that's an error
                except IndexError:
                    e = IndexError("The gp.generate function tried to add "
                                   "a primitive of type '%s', but there is "
                                   "none available." % (type_,))
                    _, _, e.__traceback__ = sys.exc_info()
                    raise e

        # Not at the bottom of the tree
        else:
            # Check for primitives
            try:
                # JM: Type is None means we can use any primitive, right?
                if type_ is None:
                    all_prims = list()
                    for typ in pset.primitives.keys():
                        for prm in pset.primitives[typ]:
                            all_prims.append(prm)
                    prim = random.choice(all_prims)
                else:
                    prim = random.choice(pset.primitives[type_])

                expr.append(prim)
                for arg in reversed(prim.args):
                    stack.append((depth + 1, arg))
                    # No primitive fits
            except:
                # So check for terminals
                try:
                    # JM: Type is None means we can use any terminal, right?
                    if type_ is None:
                        all_terms = list()
                        for typ in pset.terminals.keys():
                            for ter in pset.terminals[typ]:
                                all_terms.append(ter)
                        print("all terms: ", all_terms)
                        term = random.choice(all_terms)
                    else:
                        term = random.choice(pset.terminals[type_])

                # No terminal fits, either - that's an error
                except IndexError:
                    _, _, traceback = sys.exc_info()
                    e = IndexError("The gp.generate function tried to add "
                                   "a terminal of type '%s', but there is "
                                   "none available." % (type_,))
                    e.__traceback__ = traceback
                    raise e

                if isclass(term):
                    term = term()
                expr.append(term)

    return expr


def ourSimple(population, toolbox, cxpb, mutpb, ngen, stats=None,
              halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population
    :returns: A class:`~deap.tools.Logbook` with the statistics of the
              evolution
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) / 3)

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook


def draw(individual):
    """
    Draws a node tree of the individual
    """
    nodes, edges, labels = gph(individual)
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    pos = nx.graphviz_layout(graph, prog="dot")

    plt.figure(figsize=(7, 7))
    nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="w")
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, labels)
    plt.axis("off")
    plt.show()
