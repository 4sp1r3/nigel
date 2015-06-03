# Timesheet

## Wed Jun 3 (9hrs)

* We'll crossover like with like, so if the contributing node is in the Result Producing Branch then that is where it
   will go in the receiver, likewise with if the node is from inside an ADF.  So I'll create a crossover routine
   to consume ADF inclusive individuals which, in turn, calls the current crossover with appropriate inputs. Try that.
* Keeping the same procreation of clone, crossover, or mutate each individual-at the highest level
* removed restriction on crossovers-now they can replace the receiver from the root down (ie: replace the receiver completely)
* phew, we have a single adf going for the five parity prob. Now setting up a playbook/visualisations.
* pita, but we have drawings of adf based trees (had to go back to primitives)
* saved a notebook with 350gens/500pop/1adf = solved 130nodes

## Tue Jun 2 (4hrs)

* ADF's I think I've got it compiling the trees/prims now.  I suspect there is an error in the docs for compileADF
  (it says the main pset should be last, but things finally started working for me when I put it first!?)
* now I just need to work out how to mate/crossover etc.


## Mon Jun 1 (3hrs)

* ADFs! Loooong look over the deap support for adfs. It makes sense and is just different enough to Kosa to be
  a real pain deciding how to tackle.
* ok, found an old deap adf example to try and work from. trying it for the parity problem

## May 29 (2hrs+)

* remould the fiveparity problem to work with our selection/minimisation scoring
* push it up and run through with Nigel
* try again using just NOR gates - only one primitive
* try again adding a number of nodes penalty to the scoring routine
* leave a run of nor's, without adf, in the fiveparity notebook.

## May 28 (2hrs)

* implemented the parity problem
* adapt the stock parity problem to use our methods


## May 22 - May 27

* the great hard drive crash of 2015

## 19 May 2015 (2hrs)

* a few tweaks to pythagoras with neil
* implemented then trying to get something sensible out of the history, but not getting any satisfaction
    just some unintelligible graphs.  The solutions just appear without any recorded parentage :-(

# Invoice #4 (50hrs May 7 - May 18) PAID.

## 18 May 2015 (6hrs)

* fix #7
* having trouble with pythagoras and the app hierarchy... are we running a notebook, a module, a test?
* started working through an algorithm (pick clone, mate, mutate)
* find and fix bug in Crossover routine
* created our own algorithm to run based on 30/30/30-clone/mate/mutate
* now solving pythagoras again

## 14 May 2015 (6hrs)

* tried the new selection routine on Pythag; the avg fit score fluctuates wildly from generation
   to generation
* discussed crossover with Neil and knocked up specs, got started on it.
* worked up the crossover routine, and a notebook to demonstrate it, and commit

## 13 May 2015 (6hrs)

* set up the Draw-Trees notebook to exhibit ourGrow
* code tidy and working out how to attack the selection problem
* create the "probablistic selection" routine for #2

## 12 May 2015 (8hrs)

* prepared pythagoras in a notebook and spent time running through it with Neil
* set out to add a min tree spec to ourGrow routine, but after several hours it wasn't done.
* another hour with Neil and we alter the spec to clarify what "min" means, then decide to drop it
   in favour of a probability—start a node here or put a terminal- effectively specifying
   how 'dense' the tree should be.
* head off start down that road
* wrote up some specs
* implemented
* pushed

## 11 May 2015 (9hrs)

* built a generator which doesn't suffer from the pitfalls of the default ones:
  - can handle not having terminals, or primitives, of the type it finds itself needing
  - can grow a tree of the specified depth, not more (although maybe less)
  - doesn't raise exceptions (unless there is something genuinely wrong)
* it can now return a program which solves pythagorus (albeit not very efficiently).

## 9 May 2015 (2hrs)

* pushed it out to johnmee.com and repeated the process of getting the graphing to work, this time on Linux
* tidied up the notebook demo ready for Neil
* made a start on the normalized selection requirements

## 8 May 2015 (12pm-8pm 8hrs)

* consolidate all the mess of code and versions and repositories scattered about into one repository.  Delete the
   duplicates and put it up on my github as an authoritative version. run up the johnmee notebook and leave it running
   Start using the ticketing system there to chart the course and track priorities
* worked out how to get the plotting of trees happening, then do it within the notebook, then do it on the
   johnmee.com server, and leave some documentation on how to do it again.

## 7 May 2015 (1pm-6pm 5hrs)

* Nigel came over and, using this document ["DEAP - Enabling Nimbler Evolutions" - SIGEvolution Vol 6 Issue 2](https://www.google.com.au/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0CB4QFjAA&url=http%3A%2F%2Fvision.gel.ulaval.ca%2F~cgagne%2Fpubs%2Fsigevolution2014.pdf&ei=iRJMVc3ZB8immAWf3IHgCQ&usg=AFQjCNFg8rgyqx61ochAF1ajB04xcNzqrA&bvm=bv.92765956,d.dGY)
   we worked through the internals of DEAP and examined exactly what the default routines do—and how that
   differed from Nige's expectations.
* walked through ["Tom's" generate/treegrow routine](https://gist.github.com/macrintr/9876942) and how it varies from
   DEAP's default
* the selection routines don't include a fitness normalised and weighted probablistic routine so we need to
   write one of those
* the visualization of the trees being generated is a priority.

# Invoice #3 (38.5hrs, Apr 1-May 6)

## 6 May 2015 (2hrs)

* spoke to neil for 30mins at 9:30am but got pulled away be fbm then
   wound up not getting back to this till 6:30pm!
* discovered and reading 3 academic papers on deap 
    * "DEAP - Enabling Nimbler Evolutions" - SIGEvolution Vol 6 Issue 2
    * "DEAP: A python framework for Evolutionary Algorithms"
    * "DEAP: Evolutionary Algorithms made easy" - Journal of machine learning Research 2012.

## 5 May 2015 (11:00-6:00)

* reorientate.  spent most of the day getting it to run a pythagoras problem.
* At the end of the day it was running although it wasn't finding the answer.
* poignant questions about how it is:
   * selecting the next generation
   * building the initial population
   * crossing over nodes

## 17 April 2015 (11:00-15:00)

* Got a python notebook and up and running on my hosting and shared it around
* Worked out the problem with the "None Available" error and the terminals and the depth of the tree, and found
  an alternative 'generate' routine to try.

## 16 April 2015 (1:00-4:00)

* Went over to Nigels and gleaned what we could from Pete and got Nige up to speed

## 15 April 2015 (11:30-5:00)

* Nigel came over and we spent the day between running up his laptop (i had a flat battery on the bike so he came to me)
* running up yet another sample, this time 'find the dot on this photo'
* same issue generating populations - 'cannot choose from empty sequence'—trying to add a primitive which returns
   a photo, but there are none; just the inputs.

## 13 April 2015 (9-1 4hrs)

* add some primitive primitives (add, subtract, loop). I confess I'm not very confident it will work but that's the
    instruction and it has to happen at some point so time to try.  Runs currently get the "none available" issue as 
    mentioned on April 7th.
* added them. It's still asking for more primitives (type Photo).  I don't understand it so posted up on StackOverflow
    in hope.


## 7 April 2015 (3hrs)

* trying to add primitives. not quite understanding why it keeps complaining "generate tried to add a primitive of
    type '<class ...whatever>', but there are none available" when it seems to me that there are some there, it
    just refuses to use the same one twice :-(
* something more concerning is that the programs appear to be the same but are getting different scores?!
    I'm guessing that's because they're not all being fed the same triangles... but they are! so that's an
    unsettling mystery.
* nup. still going backwards - need to reduce further—focus on
        start with a photo of a triangle
        terminals are: the size (x,y) of the photo
        empherals are: integers -10, 10
        primitives are: is_black? is_white?
                      : add 1/-1 to ? - how to coorelate the coordinates of a vertex with a point on the photo!?
    It's a search for the transition from black/white, then a strategy to find the edges/points!
    Is it like the ant problem?

## 4 April 2015 (1hr)

* increased the number of triangles it tests for each evaluation. results are non-coalesing as expected.

## 3 April 2015 (3hrs)

* hey, it runs.  No idea what it's doing since I only gave it one primitive (translate), but, hey, it runs :-)
* found bug in the distance calculation. now getting numbers!
* worked out how to see the algorithms it's generating, and then the triangles it's producing
* concluded it is only running the program once to evaluate it - needs to be more, much more. I'm worried
    the results are skewed according to the random triangle it gets given.  Would be good to try and 
    ensure all evals are done with the same random triangles.
* still, happy we're into "IT" now.  It's doing stuff!

## 2 April 2015 (4hrs)

* awesome generation of random triangles, saving their vertices, drawing a photo, saving & loading the photo back in.

## 1 April 2015 (2hrs)

* ok so I was right, and wrong. Deap does just stringify the objects, but I'm expected to create
    the primitives in a way such that doesn't present as a problem. Tried some different algorithms
    and they didn't have the same issue, but time to put more effort into the construction of
    the primates.
* still confused about the PrimitiveSetTyped inputs & outputs; what they do and how to use them—if at all!
    - oh! maybe it declares the start args/type and end-type so gen program has start/end nodes.
* thinking to try doing triangles. Give it 3 2D points and a 2D "photo" of a triangle. It has to move the
    points to better match the shape of the photo.
* well that's odd—I did solely work on this yesterday, quite a bit, although there were substantial distractions, I clocked
   a few hours.  But most of that time was drained away by a preference switch back to pycharm; thus run up a new venv, 
   then trying to get the 'photo's of the triangles to inline into notebook. Bah! Just call it 2hrs actually 'on point'.

# INVOICE #2 (38hrs)

## 31 Mar 2015 (9hrs)

* problem I've been puzzling over for the past two hours (IndexError in gp.generate) is a bug in deap.
   Installing 12day old deap 1.0.2.  Won't work.  Whatever, got 1.1.0 from github.
* well `gp.genGrow` is now creating trees which is progress!
* i thought it would be nice to get a visualization of the trees but no joy. there's something not
   quite right about this Canopy environment. Might've hit a paywall <sigh>.
* ok. moved on. Now I'm stuck on a Syntax Error with the 'if_then_else'.  I though I'd be able to have
   it as a primitive with objects (Head) as the result but no joy. Seems like DEAP didn't have this in 
   mind because it casts to a lambda which stringifys the objects into their names, which is pretty useless.
   Have to rethink what my minimal program can do?!  Or resolve in deap.
* wasted heaps of time fiddling around with the triangles idea, thinking how it would work, writing generation
   code and messing with environments and imaging libraries again


## 30 Mar 2015 (10hrs)

* formulate the difference between two faces (for use as fit-test)
* working through creating the absolute minimal GP (one terminal)
* wow. this is tricky. the documentation could be be expansive
   trying to work out all the routines in deap and how to feed them
* still working out how to initialize the GP: define the individuals and generate them


## 25 Mar 2015 (5hrs)

* had a go at adding the edges to the imaging, without any luck
* messing about trying to get the two heads side by side for comparison, no luck, best was one on top of the other.
* assembling tidily into a commit in a new repo, pushing to bitbucket, discovering their markdown is broken (grumble, unlike githubs, grumble)

## 24 Mar 2015 (12hrs)

* refresher on matrix algebra and application to 2D and 3D objects (3hr)
* nutting out the generation, storage, and display of numpy matricies representing greyscale images (3hr)
* captured the 2d image load into a simple class and wrote a test
* researching how to load, store, plot, display the face mesh (mayavi?)
* discovered and installed enthought/canopy. Plot a mesh surface.
* discovered numpy.loadtxt-obviating pete's import routine
* managed to 3D plot the face!

## 23 Mar 2015 (2hrs)

* **move repo to bitbucket**
* Worked on the notebook trying to devise the simplest problem to get started with

# INVOICE #1 --- (16hrs)
## 18 Mar 2015 

* **still working through pete's script, transposing into a workbook**
   - [Pete's workbook](http://nbviewer.ipython.org/github/johnmee/nigel/blob/master/Petes%20Workbook.ipynb)

## 17 Mar 2015

* **watched the second video on genetic programming**
* **scoured the internets for similar work/training samples**
* **walkthrough the 'Artificial Ant Problem'**
* **working through Pete's script**


## 16 Mar 2015

* **watch the video - pretty cool!**
* **sift through the incoming code dump from pete**
	- tried running it but the virtualenv is incomplete
	- shouldn't be too hard to rebuild as there's enough clues nonetheless
* **long chat with Pete going through where he got to in detail**
* **rereading the 'Job Requirements' document again**
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
