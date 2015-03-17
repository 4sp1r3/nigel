# Timesheet

## 18 Mar 2015

# **still working through pete's script, transposing into a workbook**


## 17 Mar 2015

# **watched the second video on genetic programming**
# **scoured the internets for similar work/training samples**
# **walkthrough the 'Artificial Ant Problem'**
# **working through Pete's script**


## 16 Mar 2015

# **watch the video - pretty cool!**
# **sift through the incoming code dump from pete**
	- tried running it but the virtualenv is incomplete
	- shouldn't be too hard to rebuild as there's enough clues nonetheless
# **long chat with Pete going through where he got to in detail**
# **rereading the 'Job Requirements' document again**
    - this time with a better understanding for it's language
* **long chat with nigel via facetime**


## 13 Mar 2015

* **Review implementation of the "knapsack" problem**

http://deap.readthedocs.org/en/master/examples/ga_knapsack.html
https://github.com/DEAP/deap/blob/master/examples/ga/knapsack.py

- it randomly generates the set of 20 different items available to go into the bag
- it creates fit test which has two goals! minimize one value (1-10 in weight) and maximize the other (0-100 in dollars)
   - the evaluation routine returns [a weight/value tuple to match](https://github.com/DEAP/deap/blob/master/examples/ga/knapsack.py#L62)
- it defines the Individual as a `set` of items
- ok, not sure about the naming but, 'attr_item' is registered as a way to pick up one of the possible items at random
- and we register an Individual (ie the goal of the whole thing) as a set of 5 Items
- 'population' says we'll work with a whole lot of bags at a time - the 'evolutionary' point being that we choose good bags to work more with and discard bad ones
- so we start with a population of 50 bags of ? items
- and it just hands the lot over to a [library algorithm "eaMuPlusLambda"](https://github.com/DEAP/deap/blob/master/deap/algorithms.py#L244)!?
- ok, but again we get to define how to meddle with the bags for each generation via a 'crossover' and a 'mutate' routine
- the crossover routine takes two bags and returns two bags: one with the items common to both and the other with the items unique to each
- the mutation routine randomly removes and adds items to a given bag
- we tell the library algorithm to run 50 generations of the 50 best bags from 100 crossover/mutations
- the selection is done via a [library routine "selNSGA2"](https://github.com/DEAP/deap/blob/master/deap/tools/emo.py#L14) which, I dare say, doesn't do much other than sort them; and introduce the concept of one Individual "dominate"ing another.

* **Start trying to understand _Genetic Programming_ concepts with 'Symbolic Regression'**

## 12 Mar 2015

* **Create environment, install notebook, DEAP, document it**

See the README.md

* **Run the "onemax" problem and work out what it does, and how.**

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

* **Run the 'onemax_short' problem**

http://deap.readthedocs.org/en/master/api/algo.html#deap.algorithms.eaSimple

- turns out there is an "algorithm" routine available in DEAP to do something like the above (crossover and mutate randomly)
 just by 'registering' into the 'toolbox' module all the necessary routines and probability constants.

* **Look over the library** Wander [Evolutionary Tools](http://deap.readthedocs.org/en/master/api/tools.html) getting an idea of what is there.

* **Document everything up and commit it and email Nigel.**
