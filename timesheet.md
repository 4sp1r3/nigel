# Timesheet

12 Mar 15 - 
# Create environment, install notebook, DEAP, document it

See the README.md

# Run the "onemax" problem and work out what it does, and how.

https://github.com/DEAP/deap/blob/daf8c1c8776f57be448865ac8ace56bdb05d8324/examples/ga/onemax.py
http://deap.readthedocs.org/en/master/api/tools.html#deap.tools.initRepeat

- it generates a "population" of 300 lists of 100 booleans (:29,:45 tools.initRepeat)
- it counts the number of trues/falses in each list (:33 def evalOneMax)
- it runs a "tournament" selection process??
   ?? WTF is a tournament:
   - Is a tournament just a random selection? I don't see any evaluation inputs so how can it be doing a non-random selection?
   - playing with the code the output is a list of the same length as the input (300) and whilst they're not identical it's
       hard to determine what their differences are (if any, just in a different sort order?)
   - given the name my expectation is that it is a qualitative selection process but I'm just not seeing how
   - it must do something because if I do a straight copy the evolution doesn't work! The generations just don't improve
   - ok: maybe it is random!? the docs state "This function uses the choice() function from the python base random module."
   - NOPE: looking at the DEAP code "fitness" is an assumed attibute of Individual objects, 
     - so yep it can be a non-random selection because fitness is a basic property
     https://github.com/DEAP/deap/blob/master/deap/tools/selection.py#L34
- it pairs and "mates" the population using 'cxTwoPoint' by picking a random point in the list and swapping the contents
    before that point. eg: [0,1,2,3,4][5,6,7,8,9] might become [5,6,2,3,4][0,1,7,8,9]
- in itself there is also a randomization coefficient applied to whether or not the mating occurs
- it selects 1 in 5 Individuals in the population to "mutate" by randomly flipping the booleans (5% chance for every bit in the Individual)
- fitness of each individual is re-evaluated and assigned
- prints out some stats
- loops over that 40 times
- spits out the results

Seems like a very obtuse way to get a sequence of 100 "true"s but there it is ;-)

# Run the 'onemax_short' problem

http://deap.readthedocs.org/en/master/api/algo.html#deap.algorithms.eaSimple

- turns out there is an "algorithm" routine available in DEAP to do something like the above (crossover and mutate randomly)
 just by 'registering' into the 'toolbox' module all the necessary routines and probability constants.

# Take the time to write everything up and commit it and email Nigel.
