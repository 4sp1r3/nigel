import copy
import random
from inspect import isclass
import matplotlib.pyplot as plt
import networkx as nx

from deap.gp import PrimitiveSetTyped
from deap.gp import PrimitiveTree
from deap.gp import Primitive
from deap.gp import Terminal
from deap.base import Fitness

from geneticprogramming import NoMateException


class GrowException(Exception):
    """Tried a bunch of times but could not grow a suitable tree from the given primitives"""
    pass


class NoTerminalError(Exception):
    """Could not grow a tree due to a lack of suitable terminal"""
    pass


class NoPrimitiveError(Exception):
    """Could not grow a tree due to a lack of suitable primitives"""
    pass


class FitnessMin(Fitness):
    weights = (-1.0,)


class Individual(object):
    """
    An (individual) program of a random number of adfs and a Result Producing Branch (RPB)
    """
    # A list of input types
    INTYPES = NotImplemented
    # The output type
    OUTTYPE = NotImplemented
    # The maximum number of ADFs to generate
    MAX_ADFS = 4
    # min, max number of input arguments to adfs
    ADF_NARGS = (1, 5)
    # Probability of terminal when growing:
    GROWTH_TERM_PB = 0.3
    # Maximum depth of initial growth
    GROWTH_MAX_INIT_DEPTH = 5
    # Maximum depth of mutation growth
    GROWTH_MAX_MUT_DEPTH = 3
    # maximum number of times to attempt to grow a complete adf before abandoning
    GROWTH_MAX_ATTEMPTS = 500
    # maximum number of signatures to try before ultimately giving up
    GROWTH_MAX_SIGNATURES = 100
    # All ephemerals must start with this
    EPHEMERAL_PREFIX = 'E'

    def __init__(self, baseset):
        """
        :param baseset: a Baseset object with the primitives already loaded
        """
        # a reference to the baseset of primitives, terminals and ephemerals
        self.baseset = baseset
        # a collection of function trees
        self.trees = []
        # collection of psets; one for each tree
        self.psets = []

        # randomly decide the number of adfs
        nadfs = random.choice(list(range(self.MAX_ADFS + 1)))

        # generate the adfs
        for idx in range(nadfs):
            name = 'F%s' % idx
            self.add_function(name)

        # generate the RPB
        self.add_function("MAIN", self.INTYPES, self.OUTTYPE, prefix='IN')

        # attach a fitness
        self.fitness = FitnessMin()

    def __str__(self):
        """describe this in english"""
        return "\n".join([pset.name + ":" + str(tree) for tree, pset in self])

    def __iter__(self):
        """return pairs of tree/psets"""
        for pair in zip(self.trees, self.psets):
            yield pair

    def get_random_outtype(self):
        urn = list()
        for prim in self.baseset.primitives:
            urn.append(prim[2])
        for adf in self.psets:
            urn.append(adf.ret)
        return random.choice(urn)

    def get_random_intypes(self):
        """Return a list of input types of random type and number"""
        # put all the input types in all the primitives into an urn
        urn = list()
        for prim in self.baseset.primitives:
            for intype in prim[1]:
                urn.append(intype)
        for adf in self.psets:
            for intype in adf.ins:
                urn.append(intype)

        # choose the number of args
        nargcount = random.randint(self.ADF_NARGS[0], self.ADF_NARGS[1])

        # range the args from 0 to ensure they're contiguous
        return [random.choice(urn) for _ in range(nargcount)]

    def get_primitive_set(self, name, intypes, outtype, prefix):
        """
        Return a deap primitive set corresponding to the base prims and any added adfs
        """
        pset = PrimitiveSetTyped(name, intypes, outtype, prefix)
        for term in self.baseset.terminals:
            pset.addTerminal(term[0], term[1], term[2])
        for idx in range(len(self.baseset.ephemerals)):
            name, value = self.baseset.get_ephemeral_instance(idx)
            pset.addTerminal(value, type(value), name)
        for prim in self.baseset.primitives:
            pset.addPrimitive(prim[0], prim[1], prim[2], prim[3])
        for adfset in self.psets:
            pset.addADF(adfset)
        return pset

    @staticmethod
    def get_random_terminal(pset, type_):
        """Return one of the terminals of type from the pset"""
        terminals = pset.terminals[type_]
        if len(terminals):
            term = random.choice(terminals)
            # and if it's actually a class then instantiate it
            if isclass(term):
                term = term()
            return term
        else:
            raise NoTerminalError("No terminal of type '%s' is available" % type_)

    @staticmethod
    def gen_random_primitives(pset, type_):
        """Return one of the primitives of type from the pset"""
        primitives = pset.primitives[type_]
        if len(primitives):
            random.shuffle(primitives)
            # yield primitives until you get one that works
            for prim in primitives:
                yield prim
        else:
            raise NoPrimitiveError("No primitive of type '%s' is available" % type_)

    @staticmethod
    def all_args_used(pset, tree):
        """True if all the input arguments in pset are used by tree"""
        return all([pset.mapping[arg] in tree for arg in pset.arguments])

    @staticmethod
    def grow(pset, max_, type_=None, prob=None):
        """Generate an expression tree.
        Branches can be of any height, provided they are not more than *max*.

        :param pset: Primitive set from which primitives are selected.
        :param max_: Maximum height of the produced tree.
        :param prob: 0..1 the probability of a terminal (vs primitive) being placed at a node.
        :param type_: The type that the tree should return when called.
        :returns: An expression tree.
        """
        if prob is None:
            prob = Individual.GROWTH_TERM_PB

        if type_ is None:
            type_ = pset.ret

        # if maximum depth or no primitives or chance
        if max_ <= 1 or random.random() < prob or not len(pset.primitives[type_]):
            # return a random terminal
            return [Individual.get_random_terminal(pset, type_)]

        # return a primitive and tree
        for prim in Individual.gen_random_primitives(pset, type_):
            try:
                expr = [prim]
                for arg in prim.args:
                    expr += Individual.grow(pset, max_ - 1, arg, prob)
                return expr
            except (NoTerminalError, NoPrimitiveError):
                # that prim didn't work, so try the next one.
                continue
        else:
            raise NoPrimitiveError("No primitive is available. I tried them all.")

    def add_function(self, name, intypes=None, outtype=None, prefix='A'):
        """
        Create and add a new function
        :param name: a unique name for the function (or non-unique if that's a deliberate intention)
        :param intypes: list of input types
        :param outtype: the output type
        :param prefix: label for the input terminals
        :return: undefined
        """
        # if we can't grow a function and types were not specified
        # then we'll change the signature, otherwise fails
        flexible_signature = outtype is None and intypes is None

        # pick an outtype
        if outtype is None:
            outtype = self.get_random_outtype()

        # pick the intypes
        if intypes is None:
            intypes = self.get_random_intypes()

        # (try to) grow a tree
        for signature in range(Individual.GROWTH_MAX_SIGNATURES):
            pset = self.get_primitive_set(name, intypes, outtype, prefix)
            # keep trying till we get a valid function tree
            for attempt in range(self.GROWTH_MAX_ATTEMPTS):
                try:
                    # grow a tree
                    tree = PrimitiveTree(Individual.grow(pset, self.GROWTH_MAX_INIT_DEPTH, outtype, prob=self.GROWTH_TERM_PB))
                    all_args_used = all([pset.mapping[arg] in tree for arg in pset.arguments])
                    # if all the arguments are used
                    if all_args_used and len(tree) > 1:
                        # use it
                        self.psets.append(pset)
                        self.trees.append(tree)
                        return
                except (NoTerminalError, NoPrimitiveError):
                    # a valid tree did not eventuate
                    continue
            else:
                # if we couldn't grow a tree, but we are free to alter the inputs and output types
                if flexible_signature:
                    # try a different signature
                    outtype = self.get_random_outtype()
                    intypes = self.get_random_intypes()
                else:
                    # otherwise abort
                    raise GrowException("Despite trying %s times unable to grow specified signature %s -> %s ." %
                                        (self.GROWTH_MAX_ATTEMPTS, intypes, outtype))
        else:
            # we tried but no valid tree could be grown
            raise GrowException("No ADF tree could be grown after %s attempts with different ADF signatures, "
                                "where %s attempts were made to grow within each signature. Please review your "
                                "definitions of the primitives and retry" % (
                                    self.GROWTH_MAX_SIGNATURES, self.GROWTH_MAX_ATTEMPTS))

    def clone(self):
        """returns a copy of oneself"""
        return copy.deepcopy(self)

    def mutate(self):
        """
        Change a random node by growing a new bit of tree there
        Yes, it could replace the root node of a subtree.
        Yes, it will happily replace a slice with an identical slice. Especially terminals.
        """
        # pick a subtree to mutate
        idx = random.choice(range(len(self.trees)))
        subtree, subpset = self.trees[idx], self.psets[idx]

        # pick a node to mutate
        index = random.randrange(len(subtree))
        slice_ = subtree.searchSubtree(index)
        type_ = subtree[index].ret

        # grow from that node
        for _ in range(Individual.GROWTH_MAX_ATTEMPTS):
            try:
                mutation = Individual.grow(subpset, self.GROWTH_MAX_MUT_DEPTH, type_=type_, prob=self.GROWTH_TERM_PB)
                if Individual.all_args_used(subpset, mutation):
                    break
                else:
                    continue
            except (GrowException, NoPrimitiveError, NoTerminalError):
                continue
        # print(slice_, [n.name for n in subtree[slice_]], [n.name for n in mutation])
        subtree[slice_] = mutation
        del self.fitness.values

    @staticmethod
    def is_compatible(node, pset):
        """
        True if the node will make sense within the pset's context
        :param node: a node
        :param pset: a deap PrimitiveSetTyped
        :return: true/false
        """
        # ephemeral
        if isinstance(node, Terminal) and node.name[:1] == Individual.EPHEMERAL_PREFIX:
            return True

        # same name and type then no problem
        try:
            pnode = pset.mapping[node.name]
            if isinstance(pnode, Primitive) and isinstance(node, Primitive):
                return node.ret == pnode.ret and node.args == pnode.args
            else:
                return node.ret == pnode.ret and node.arity == pnode.arity
        except KeyError:
            pass

        return False

    def find_slice(self, nodetype, pset):
        """
        Returns a slice compatible with nodetype and pset, or error
        :param nodetype: the type that the slice needs to return
        :param pset: the set of nodes the receiver knows of; don't use anything not in here
          Excepting Ephemerals—using unknown emphemerals is permitted.
        """
        # collect all possible contributor nodes
        # TODO: perhaps create an iterator/enumerator for this operation
        branch_nodes = [(b, n) for b in range(len(self.trees)) for n in range(len(self.trees[b]))]
        random.shuffle(branch_nodes)

        # try every node for a valid contribution
        for ibranch, inode in branch_nodes:

            # if root node has wrong return type
            if self.trees[ibranch][inode].ret != nodetype:
                continue

            # resolve to candidate slice
            candidate_slice = self.trees[ibranch].searchSubtree(inode)
            candidate_nodes = self.trees[ibranch][candidate_slice]

            if all([Individual.is_compatible(node, pset) for node in candidate_nodes]):
                return candidate_nodes

        # the receiving node is wholly incompatible with the contributor
        return None

    def mate(self, other):
        """
        Cut a compatible branch off the contributor and stick it somewhere here
        Yes, they'll happily exchange identical slices.
        """
        # collect all possible receiving nodes
        branch_nodes = [(b, n) for b in range(len(self.trees)) for n in range(len(self.trees[b]))]
        random.shuffle(branch_nodes)

        for ibranch, inode in branch_nodes:
            nodetype = self.trees[ibranch][inode].ret
            contribution = other.find_slice(nodetype, self.psets[ibranch])
            if contribution is not None:
                pruned_slice = self.trees[ibranch].searchSubtree(inode)
                self.trees[ibranch][pruned_slice] = contribution
                del self.fitness.values
                return
        else:
            raise NoMateException("Exhausted all possible nodes on both individuals without finding a mate.")

    def compile(self):
        # removes deap's compile and compileADF so we can see what it's doing.
        # for each routine, add previous routines to the context, codify the routine and call it,
        #  then add it to the list of routines in context. Return the evaluated solution.
        adfdict = {}
        func = None
        for subexpr, pset in self:
            pset.context.update(adfdict)
            code = str(subexpr)
            if len(pset.arguments) > 0:
                adfargs = ",".join(arg for arg in pset.arguments)
                code = "lambda {args}: {code}".format(args=adfargs, code=code)
            context = pset.context
            context.update(self.baseset.ephemeral_instances)
            func = eval(code, pset.context, {})
            adfdict.update({pset.name: func})
        return func

    def evaluate(self, *args):
        raise NotImplementedError()

    @property
    def ephemerals_used(self):
        """A dictionary of the ephemerals actually in use"""
        used = dict()
        for tree in self.trees:
            for node in tree:
                if node.name in self.baseset.ephemeral_instances:
                    used[node.name] = self.baseset.ephemeral_instances[node.name]
        return used

    def draw(self):
        """
        Draws a node tree of an adf individual
        """
        progn = 'PROGN'
        expr = []
        for num, branch in enumerate(self.trees[:-1]):
            expr = expr + ['F%s' % num] + branch
        expr += ['RPB'] + self.trees[-1]
        nodes = list(range(len(expr)))
        edges = list()
        labels = dict()

        stack = []
        for i, node in enumerate(expr):
            if stack:
                edges.append((stack[-1][0], i))
                stack[-1][1] -= 1

            if isinstance(node, Primitive):
                labels[i] = node.name
            elif hasattr(node, 'value'):
                if node.value in self.ephemerals_used:
                    if isinstance(self.ephemerals_used[node.value], float):
                        labels[i] = "%.2f" % self.ephemerals_used[node.value]
                    elif isinstance(self.ephemerals_used[node.value], int):
                        labels[i] = "%s" % self.ephemerals_used[node.value]
                    else:
                        labels[i] = node.value
                else:
                    labels[i] = node.value
            else:
                labels[i] = str(node)

            if hasattr(node, 'arity'):
                stack.append([i, node.arity])
            elif node == progn:
                stack.append([i, len(self.trees[-1])])
            else:
                stack.append([i, 1])

            while stack and stack[-1][1] == 0:
                stack.pop()

        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        pos = nx.graphviz_layout(graph, prog="dot")

        figsize = (25, max([i.height for i in self.trees]) + 2)
        fig = plt.figure(figsize=figsize)
        fig.suptitle("Score {:2.4f}".format(self.fitness.values[0]), fontsize=16, y=0.05)

        # list the signatures fof the primitives
        text = "\n".join(
            ["{} ({})".format(k, v.arity) for k, v in sorted(self.psets[-1].mapping.items()) if isinstance(v, Primitive)]
        )

        # list the values of the ephemerals that get used
        for k, v in self.ephemerals_used.items():
            text += "\n{}: {}".format(k, v)

        fig.text(0.0, 0.05, text)
        nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="w")
        nx.draw_networkx_edges(graph, pos)
        nx.draw_networkx_labels(graph, pos, labels)
        plt.axis("off")
        plt.show()
