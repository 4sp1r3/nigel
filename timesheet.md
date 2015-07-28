# Timesheet

4+5+7.5+8 = 24.5

# Tues 28 (9-3,3:30:5:30 = 6+2 = 8)

* still mucking around with integrals and paths!
* rework the faces to respect the edges by keeping vertices in order of a path
* implement "is_behind" routine

# Mon 27 (10-1, 2:30-7pm = 3+4.5 = 7.5)

* loads data into new little Vertex, Edge, Face classes and hooks it into nige's integral function then
   tries to loop over every face/vertex/edge to decide if a vertex is visible
* sort the edges to ensure the integrate is calculated via sequential vertices

# Fri 24 Jul (10-?, 3-7 = call it 5 hrs).

* ug. loading in the new face/vertice/edge data
* still loading in the data, trying to loop over it the correct way: vert -> face->vert mech.

# Thu 23 Jul (10---7 -- call it 4 hrs).

* walking through vector arithmetic
* on and off all day whilst nige fiddles around with calculus
* painfully walking through calculation of an integral at the lowest of low levels

# INVOICE 8 (5.5 + 6 + 6.5 + 8.5 + 8.5 + 2 + 3 + 4.5 = 44.5)

## Mon 20 Jul (10:1, 3-4, 5-6:30 = 4.5)

* find and consume academic articles about GP esp. those that describe looping
* document 'the problem with deap re: loops and state' 
* deploy and play with the ant problem

## Fri 17 Jul (9:30-1:00,2-4 = 3.5+2= 5.5)

* much discussion with nigel
* demonstrating fibonacci like an ant

## Thu 16 Jul (9-12,2-5 = 3+3 = 6)

* watched it run pythag matrix a whole bunch of times
* working out specs for 'doloop' with nige in 10min bursts because the phones are bad
* trying to isolate the problem with genGrow that sends it off in a spin sometimes
* change the grow routine completely; simpler but raises errors more often
* quick attempt to multiprocess failed quickly - the routines need to be pickleable
* fibonacci, let, set, do loop. Long discussion with Nige.


## Wed 15 Jul (9:30-2:00, 5:00-7:00 = 4.5+2 = 6.5)

* add ephemeral instances to the global/population context
* crossover adfs with the same name/signature, but not those without, testing it does what I think it does.
* do a bunch of runs, put the node counter back into the evaluation, post it up
* tidy up the presentation on the notepad (evaluate pops, list prims and ephs values)

## Tues 14 Jul (9-1:30,2:30-6:30,10-11p = 4.5+3+1 = 8.5)

* create a notebook for matrix-pythagoras. not working yet, but might push it up to give nige something to look
   at again. Done.
* combined everything back into one—removing imports from ourMods
* migrated FunctionSet functionality into Individual and removed it
* refactor everything into the "geneticprogramming" app
* rework the mutate routine, so that it actually works, and resets the score
* reworking the mate routine... hard! working out how to ensure the receiver knows what all the nodes are, but
   taking into account the exceptions (ephemerals, rpb or adf)
* worked out an is_compatible routine for checking crossover slices

## Mon 13 Jul (10-1, 3-6:30, 8-10 = 8.5)

* putting together another pythagoras solver, shoehorning in some numpy arrays
* been quite a while since we did a complete problem, much has changed.  Adapting to the new paradigm (and
   yet again balancing which bits of deap to discard/keep)
* lots of fiddling around to reapply everything (regeneration, mate, mutate, even cloning)
   because the structure of trees/psets has changed considerably since untyped unrandom pythagoras
* got so far as running without the notebook, abeit not very sensibly

## Sun 12 Jul (2-4pm = 2)

* isolate the global problem baseset by implementing a local FunctionSet class over the top.

## Fri 10 Jul (10:00-1:00pm = 3)

* phaffing, cleaning up the ephemerals. Discussing problem of global empherals vs local functions in the face
   of crossovers.
* trying to work out how to do it

# INVOICE 7 (June 30-July 9)

## Thu 9 Jul (9-12, 3:30-5:00=4.5)

* new strategy; it's only the empheral that's causing issues, and the initial construction of it at that, so
   alter the way it works in deap such that it is a 'symbolic' terminal.
* That works. We create a new terminal whenever an Ephemeral is called for and put it's value into the context so
   it can be refered to as a variable.
* A bit of tooing-froing about when new ephemeral instances should be generated. I have it adding them as terminals,
   currently, so the existing ones could be used, or a new one could be created? Something like that?

## Wed 8 Jul (10-12, 3-6:30=5.5)

* ok, I'm writing strings, but how to read them back? __repr__ and __str__ on numpy behave oddly, as do __new__ and
   __init__; probably because they're C routines underneath
* going nowhere... idea #39: create a Terminal and poke values into the evaluation context, or #40 do some
   funky string replace sort of variable implementation?
* blew out deap's compile routines, looking again at exactly how these guys are evaluating

## Tues 7 Jul (3:30-6.30, 9-10:30=4.5)

* push ahead trying to stringify everything into functions and making up type tokens.
* bah. default load/dump pickle routines includes carriage returns which stuffs up the lambdas.
* banged around between bytes, and str's, and encodings, internal representations, and hell in general, kinda
   getting there, but never actually getting there.

## Fri 3 Jul (9:30-12:30, 3-6:30, 8-9pm=7.5)

* playing around with matrix inputs/outputs and does the typing actually work? Is it something we want?
* found 'bug' in our grow function: failure to grow a specific signature would just change the signature, something
   we don't want to occur on the RPB
* tried wrapping the matrix type in a class so we can pass them around as types.  But they still won't evaluate:
   deap evaluates programs by converting them to a string, then passing the string to python and saying "run this".
   Complex objects—ones that cannot be passed by converting to and from a string—don't seem amenable to this type
   of compilation.  Seeking a better understanding or way around it.
* checked pete's original code, his evaluations didn't run either for the same reasons... 
   Ouch, took me an awful long time to reach the same blockage point 8-/
* One way might be to take the 'ant' approach where, rather than trying to output a number-or array-we have an
   object and the output is a series of operations on that object. ie: move left, go forward. So we might 'rotate
   head to left', 'move vertex 192, 2 units to the right'.  That kind of thing.
* The rolls royce solution would be to ditch DEAP and implement a more granular language parser in which the nodes
   of our tree are not just functions and values, but expressions and flow controls as well.  Something I've looked
   long at aka in python as AST (abstract symbol tree) which allows us to manipulate actual python code; removing
   the constraints of DEAP's approach which limits us to purely functional primitive nodes.

## Thur 2 Jul (8:30-11:00, 1:00-2:00, 4:00-6:30, 8:00-9:30=1.5+2.5+1+2.5=7.5)

* cleaned up the typed random adf generation and pushed out a notebook for it
* regenerate the signature if growing fails repeatedly
* add adfs to urns of random input/output selections
* for loops and if_then_else implementations... running into questions about type: what type does an if-then-else
   return if the two working branches are different types? What type is a working branch which has not been
   evaluated yet?

## Wed 1 Jul (8:30-1:00,  -1hr, 3:30-7, 7:30-11:30=3.5+3.5+4=11hrs)

* generating random adfs and evaluating whether they use all their arguments
* generating the RPF using the same adf routines and the adfs themselves.  A little tangent that
   started trying to ensure the RPB used all the ADFs, but that was silly, so aborted.
* evaluates the adfs fine, until routines start refering to each other-then kapow
* bang away trying to decode out deap's weird (er, immature?) ADF compilation; their addADF doesn't practically
   nothing and we need to track the pset and tree for each adf ourselves (and keep them in sync/together)
* refactor everything(!) because we'd ran straight back into the chicken/egg syndrome
* woot. evaluatable nested adfs/rpb. just one more refactor to go (hopefully).

## Tues 30 June (2hr, 2.5, 2.5: 7hrs)

* (1) ProgramTree - randomising the number and types of adfs
* (2) DummyTerminal - trying to implement morphing terminals and add them to the fsets
* Work with nigel, one tiny step at a time.
* building the adf generation little bit at a time, trying to tie it together with deap

# Invoice #6 (hrs June 15 - June 29)

## Mon 29 June (2hrs, 2hr, 4hrs: 8hrs)

* plugging away trying to get some shape; first tried using __new__ to setup the individuals class to generate adfs,
   but that went nowhere.  Now making classes for 'Branch' and 'FunctionSet' to try and grow typed branches in a 
   self managed object which is tied together by 'Individual'.
* (1) FunctionSet - add types and pick any terminal or prim, or any term/prim of a type
* (2) FunctionSet - add methods to proportionately randomize and select types of primitives and terminals or either
* (3) FunctionSet - still thrashing out the set of primitive functions in order to pull random type or node within
       primitive, terminal, or both scope sets. Return sets or lists of nodes, terminals, or primitives.
* (4) FunctionSet - pumping out prims, then got down to grow and realized which ones I really need; just random_node
       and list of all nodes really.  Start over toward that end.
* (5) FunctionSet - random_nodes, primitives/terminals of specified types, working into grow
* (6) FunctionSet - tada! the grow works, and is much simpler than before; doesn't have the no nodes of type
       problem we used to?!?
* fiddled around with Branch but couldn't stick with it, spent.

## Fri 26 June (1+1.5: 2.5)

* getting back into creating a tidy typed library drawing from deap underneath. Creating a FunctionSet to oversee
   their psets.
* nope. population? nope... extracting the Individual and focusing on generalizing it's instansiation-with a view
   to better controlling the subsets within.

## Thu 25 June (3.0)

* still divergent on the AST track. Been interesting, but I'm going to have to switch back.  I've learned a lot, and
   better understand the concepts, but it's taking too long and I'm concerned about the deap response that they've
   tried it and lambda's were faster.  I can see they're probably easier to get your head around but, on the other hand,
   I'm not convinced they're adaptable to more advanced program structures, like loops or assignments.

## Wed 24 June (7hrs)

* pushing ahead with new code; currently feeling a little perplexed where the obstacle is. Why did deap take the path
   they did with the lambda's and all?
* I've wound up back at ASTs.  It was all going well until I started doing expressions.  Basically these 'trees' are
   expressions which need to defer evaluation until instantiation - by providing input arguments.  Which might relate
   to Kosa's 'dummy' arguments: you need a placeholder in the unevaluated expression.  Am I building a lexer, a
   parser, a compiler, or interpreter!?  The missing concept of the moment has been 'expression'.

## Tues 23 June (7hrs)

* implementing typed ADFs
* Hmm, difficult to get traction. Deap PrimitiveSets require input and output parameters, which strikes me as odd
   as well as making it hard to apply to our problem.  Add to that the PrimtiiveTree, makes sense at least, also
   expects to know certain things at instantiation time, but we don't—we just want to give it an 'urn' of options
   and say pick one for yourself.  Not insurmountable issues, but more untidyness working around these issues, I found
   myself constantly gravitating back toward replacing more bits of deap.
* So working on growing our own Function Trees, which know what a Function Set is and how to use it.  So far its
   proving quite easy and tidy, so... no reason to stop yet.

## Mon 22 June (5hrs)

* start applying uber-adfs to pythagoras to expose the most pertinent questions
* much discussion of the spec on how to handle generation of typed ADFs
* discuss and document exactly that (issue #13)

## Fri Jun 19 (4.5,5.5: 10hrs)

* show, tell, and tweak with nige
* examined the way the signature of the pop skews over time toward uniformity
* profiled the runs and established most of the time is consumed running the programs to evaluate their score
* tweaked the 'nor' to bitwise (halves the run time), removed some unnecessary cloning - speeds it up a bit more.
* looking into multiprocessing
* show and tell
* configure the mate/mutate/clone proportions
* configure the initial/mutate maximum tree sizes: took some time making sure that the growth is working properly;
   it is, a big growth depth can make for enourmous trees!

## Thu Jun 18 (3+3+1: 7hrs)

* working on grafting adfs with variable argument counts. done.
* insert the score and function arity into the actual graph
* do many runs for testing and experimentation.
* enable nige to configure number of adfs and arg counts
* identified a problem that the population is morphing the signatures... I don't think it is supposed to do that:
    due to the normalized selection the pop quickly skews towards a uniform signature.

## Wed Jun 17 (3+3+2: 8hrs)

* rewrite the mating routines over and over until it actually works considering branches and psets nodetypes etc.
* do lots of runs and watch it get worse results than ever; it's so focused on short nodecounts the popset gets
    increasingly uniform and never makes any breakthrough to a lower score
* rejig the evaluation scores.  First trying the deap weighting to no avail, then back to raw count of nodes,
    now to raw score and an exponential scaling of the number of nodes
* attempt to implement dynamic argument counts within the ADFs
* aah, if you change the arity of a function, you need to modify everywhere it gets used... hence preservation
   of the 'signature' of the program; or crossovers are injecting twigs containing calls to functions with a
   a different argument count to the current individual. 
* So, as per Kosa, reject crossovers where the twig contains a call to an ADF with a different argument count 
   (item 4 in his point-typing list).


## Tues Jun 16 (2+3: 5hrs)

* added pset parameter to the cxPTreeGraft routine to ensure it only proposes a graft that has elements known
    to the receiving branch and play around trying to get it to work without breaking backward compat

## Mon Jun 15 (2hr, 2hr, 1hr, 3hr: 8hrs)

* try to get some ast going. Found GreeTreeSnakes then a winding path lead to [Astor](https://github.com/berkerpeksag/astor)
    had a play with that; seems it can convert code to ast and back.  Trying to work out how to apply it: rather than
    a long rebuild of deap core, I'll have another go at just rebuilding the compile portion; but with ast. The idea
    being that we still get all deap, but can remove the lambda obsfucation and thence call other ADFs.
* contact with nigel - don't worry about pruning adfs that don't get used. push on with ast if that offers more
    predictability wrt time
* DOH! got through it - the deap code is calling adfs between themselves; matter of getting the psets lined up exactly,
    oh, and removing the list reversal in their code.  I'm not a fan of the way they've done it, but if it works...
* moving on to rewriting the mating (again) to accomodate adfs that are aware of other adfs.


# Invoice #5 (hrs May 18 - June 13)

## Fri Jun 12 (3+1+2=6)

* tried to resimplify the problem back to using deap compile and compileADF. The debugger can't penetrate
   the lambdas, but whilst it is simpler with just the KosaProgramTree (without KosaFunctionTree), I'm
   increasingly convinced it can't handle the ADF's nesting inside one another, but can't nail it, because the
   RPB can do one layer of nesting but the lambda's hide everything else.
* painfully back to exploring AST's for a solution  
 
## Thur Jun 11 (2hrs+2.5hrs+2.5hrs=7)

* delving through how deap evaluates the adfs and trying to get it to play nice with variable psets.
   This is as far a deap with carry us; their psets are very clear when it comes to subbranches/functions
   I'm gonna have to create our own trees and functions and evaluations.  Now, it is kosatree time?
* talk to nige about the critical program signature to retain
* recreate an outline of the kosa class and run it
* researching into ast (abstract syntax trees) which we might want to use very soon now
* baaah, this is hard.  No matter what I do deap leads me back to insufferable `lambda` statements

## Tues Jun 9 (6hrs)

* dynamic numbers of adfs finally
* drawing dynamic numbers of adfs
* mating across adfs (but not rpb's yet)
* score by number of nodes called during a run (rather than just count of nodes total)

## Sat Jun 6 (2hrs)

* did the last of the refactoring to remove the deap toolbox in favour of regular python. still 2 adfs,
    and should be clear path now to implement dynamic adfs.

## Fri Jun 5 (7hrs)

* still hacking away trying to inject Kosa style ADF's into DEAP. Calling it "KosaTree" :-) for now.
* ok, managed to de-deap the whole initialisation process and population instantiation, so it now looks
     like regular old object-oriented and functional python programming.  Now I just need to create a 
     KosaTree, abstract the creation of adfs to a function call, and tackle the graphing again to show
     arbitrary KosaTrees. Gee, that's all '-P
* nup. To get to dynamic numbers of adfs within each individual they'll need to handle their own primitive sets;
     more specifically knowing which adfs it has in order to do a crossover; which, in turn, means I need to
     migrate the rest of the deap toolbox stuff into the internals of each individual.

## Thu Jun 4 (5hrs)

* talk to nige, working toward multiple adfs
* 2 indepedent ADFs of 2 args, drawn.
* No joy getting one ADF to use another; deap wouldn't compile them and it looks like a rabbit hole to resolve.
* struggled to balance adding ADF functionality against retaining deap's valuable bits, lots of thinking
   and puzzling out how deap is contructed and where to cut in and start doing our ADF thing. Toyed with
   another module, but too risky, resolved to a chip-away approach, cycling over tiny incremental changes
   to approach the whole.

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
