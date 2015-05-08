import operator

from deap import gp
from deap import creator
from deap import base
from deap import tools

from primitives import Head, HEAD, Photo, PHOTO


# A smaller score (distance) is better
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# Every individual in the population is a tree of operations with a Fitness class
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)


pset = gp.PrimitiveSetTyped(
    "MAIN",         # Name seems to be an arbritrary string
    [Photo, Head],  # Input types: a Photo and a Head
    Head            # Output type: a Head
)


def if_then_else(input, then_output, else_output):
    if input:
        return then_output
    else:
        return else_output

pset.addPrimitive(operator.eq, [Head, Head], bool)
pset.addPrimitive(operator.ne, [Head, Head], bool)
pset.addPrimitive(if_then_else, [bool, Head, Head], Head)

pset.addTerminal(HEAD['alfred'], Head, "ALFREDs head")
pset.addTerminal(HEAD['bob'], Head, "BOBs head")
pset.addTerminal(False, bool)


toolbox = base.Toolbox()
toolbox.register("expr", gp.genGrow, pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def eval(individual):
    func = toolbox.compile(expr=individual)
    new_head = func(PHOTO['nigel'], HEAD['alfred'])
    return new_head.distance(HEAD['alfred']),

toolbox.register("evaluate", eval)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
