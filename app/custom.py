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


class DeadBranchError(Exception): pass


def ourGrow(pset, max_, type_=None, prob=0.2):
    """Generate an expression tree of depth between *min* and *max*.

    :param pset: Primitive set from which primitives are selected.
    :param max_: Maximum height of the produced tree.
    :param prob: 0..1 probability of  Terminating now
    :param type_: The type that should return the tree when called.
    :returns: An expression tree with node depths between min to max
    """
    def random_terminal():
        terminals = pset.terminals[type_]
        if len(terminals) == 0:
            raise DeadBranchError("No terminal of type '%s' is available" % type_)
        else:
            term = random.choice(terminals)
            # and if it's actually a class then instantiate it
            if isclass(term):
                term = term()
            return [term]

    if type_ is None:
        type_ = pset.ret

    # we're at the maximum depth, or there are no primitives to try
    if max_ <= 1 or not len(pset.primitives[type_]):
        return random_terminal()

    # if chance dictates, return a terminal, if you can
    try:
        if prob > random.random():
            return random_terminal()
    except DeadBranchError:
        # No problem, press on, we'll try the prims.
        pass

    primitives = pset.primitives[type_].copy()
    random.shuffle(primitives)
    for prim in primitives:
        try:
            expr = [prim]
            for arg in reversed(prim.args):
                expr += ourGrow(pset, max_-1, arg, prob)
            return expr
        except DeadBranchError:
            # ok, this prim is no good, but press on and try others
            pass

    # exhausted all terminals and primitives
    raise DeadBranchError("Neither primitives nor terminals of type '%s' could be found" % type_)



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

    plt.figure(figsize=(10, individual.height + 1))
    nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="w")
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, labels)
    plt.axis("off")
    plt.show()


def toms_generate(pset, min_, max_, condition, type_=None):
    """
    as per https://gist.github.com/macrintr/9876942
    modified for python 3
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
