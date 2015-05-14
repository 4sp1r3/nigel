import random
from inspect import isclass

import matplotlib.pyplot as plt
import networkx as nx

from deap.gp import graph as gph
from deap.gp import PrimitiveTree


def cxPTreeGraft(receiver, contributor):
    """Grafts a branch from the contributor onto the receiver.

    :param receiver: A PrimitiveTree which will receive a branch; the root is not changed
    :param contributor: An PrimitiveTree from which a branch will be copied
    :returns: A PrimitiveTree with a branch of the contributor on the receiver, or an exception.
    """
    class GraftingError(Exception):
        """A graft from the contributor to the receiver was not possible"""
        pass

    # find and randomly choose the type of node to graft at
    types1 = set([node.ret for node in receiver[1:]])
    types2 = set([node.ret for node in contributor[1:]])
    common_types = types1.intersection(types2)
    try:
        graft_type = random.choice(list(common_types))
    except IndexError:
        raise GraftingError("The two individuals do not have any nodes of the same type.")

    # pick the grafting nodes
    receiving_node = random.choice([(i, node) for i, node in enumerate(receiver) if node.ret is graft_type])
    contributed_node = random.choice([(i, node) for i, node in enumerate(contributor) if node.ret is graft_type])

    # graft the contributed slice onto a copy of the receiver
    child = receiver.copy()
    prune_slice = receiver.searchSubtree(receiving_node[0])
    contributed_slice = contributor.searchSubtree(contributed_node[0])
    child[prune_slice] = contributor[contributed_slice]

    return PrimitiveTree(child)


def genGrow(pset, max_, type_=None, prob=0.2):
    """Generate an expression tree.
    Branches can be of any height, provided they are not more than *max*.

    :param pset: Primitive set from which primitives are selected.
    :param max_: Maximum height of the produced tree.
    :param prob: 0..1 the probability of a terminal (vs primitive) being placed at a node.
    :param type_: The type that the tree should return when called.
    :returns: An expression tree.
    """
    class DeadBranchError(Exception): pass


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
                expr += genGrow(pset, max_ - 1, arg, prob)
            return expr
        except DeadBranchError:
            # ok, this prim is no good, but press on and try others
            pass

    # exhausted all terminals and primitives
    raise DeadBranchError("Neither primitives nor terminals of type '%s' could be found" % type_)


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
    #FIXME: surely this can be optimized?
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
