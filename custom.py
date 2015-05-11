import sys
import random
from inspect import isclass
# from operator import attrgetter
# from deap.gp import __type__

import matplotlib.pyplot as plt
import networkx as nx

from deap import tools
from deap.gp import graph as gph
from deap.algorithms import varAnd
from deap.gp import PrimitiveTree


class TerminalsError(Exception): pass
class PrimitivesError(Exception): pass


def ourGrow(pset, depth, type_=None, max_fails=5, jiggle=2):
    """Generate an expression tree of depth between *min* and *max*.

    :param pset: Primitive set from which primitives are selected.
    :param depth: Height of the produced tree.
    :param type_: The type that should return the tree when called.
    :returns: An expression tree with node depths between min to max
    """
    assert depth != 0
    if type_ is None:
        type_ = pset.ret

    # a tree of depth 1 is just a terminal
    if depth == 1:
        # if we have some terminals to choose from
        if pset.terminals[type_]:
            # return a Terminal
            term = random.choice(pset.terminals[type_])
            # and if it's actually a class then instantiate it
            if isclass(term):
                term = term()
            return [term]
        else:
            # No terminals of that type available
            raise TerminalsError("No terminals of type '%s' available" % type_)

    # if there are no primitives of this type try returning a terminal instead
    # if that doesn't work then raise an error
    if not pset.primitives[type_]:
        try:
            return ourGrow(pset, 1, type_)
        except TerminalsError:
            # things are pretty bad if neither terminals nor primitives of that type
            raise PrimitivesError("No terminals or primitives available of type '%s'" % type_)

    # pick a primitive and grow a tree under each argument
    primitives = pset.primitives[type_].copy()
    random.shuffle(primitives)
    for prim in primitives:
        fails = 0
        while fails < max_fails:
            fails += 1
            try:
                expr = [prim]
                for arg in reversed(prim.args):
                    expr += ourGrow(pset, depth - 1, arg)
                tree = PrimitiveTree(expr)
                if abs(tree.height - depth) <= jiggle:
                    return expr
            except TerminalsError:
                # never mind we'll try again, up to max_fails attempts
                pass
    # ran out of primitives
    raise PrimitivesError("None of the primitives grew into a valid tree (type '%s')" % type_)


def toms_generate(pset, min_, max_, condition, type_=None):
    """
    as per https://gist.github.com/macrintr/9876942
    :param pset:
    :param min_:
    :param max_:
    :param condition:
    :param type_:
    :return:
    """
    if type_ is None:
        type_ = pset.ret
    expr = []
    height = random.randint(min_, max_)
    # stack is the nodes we need to fill (depth, result type)
    # push the root node
    stack = [(0, type_)]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        # At the bottom of the tree
        if condition(height, depth):
            # Try finding a terminal
            try:
                term = random.choice(pset.terminals[type_])
                # if it's a class instansiate it
                if isclass(term):
                    term = term()
                expr.append(term)
            # No terminals available,
            # so pull the depth back one layer, and append a primitive and
            # push it's args onto the stack
            except IndexError:
                try:
                    depth -= 1
                    prim = random.choice(pset.primitives[type_])
                    expr.append(prim)
                    for arg in reversed(prim.args):
                        stack.append((depth + 1, arg))

                # No primitives fit either, so raise an error
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




# def condition(height, depth):
    #     """Expression generation stops when the depth is equal to height
    #     or when it is randomly determined that a a node should be a terminal.
    #     """
    #     return depth >= height or \
    #            (depth >= min_ and random.random() < pset.terminalRatio)
    #
    # return generate(pset, min_, max_, condition, type_)


#def generate(pset, min_, max_, condition, type_=__type__):
    # """Generate a Tree as a list of list. The tree is build
    # from the root to the leaves, and it stop growing when the
    # condition is fulfilled.
    #
    # :param pset: A primitive set from wich to select primitives of the trees.
    # :param min_: Minimum height of the produced trees.
    # :param max_: Maximum Height of the produced trees.
    # :param condition: The condition is a function that takes two arguments,
    #                   the height of the tree to build and the current
    #                   depth in the tree.
    # :param type_: The type that should return the tree when called, when
    #               :obj:`None` (default) no return type is enforced.
    # :returns: A grown tree with leaves at possibly different depths
    #           dependending on the condition function.
    # """


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


# something that given a population normalizes the fitness scores 0..1
# class NormalisedPopulationWeightedFitness(Fitness):
# pass
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
