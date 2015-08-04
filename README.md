![Plot of two heads](canobox/snapshot.png?raw=true "Plot of two heads")

---

This codebase is https://github.com/johnmee/nigel.git

It consists of many python notebooks in various states of tidy and untidiness.  Some of them will still run, some
probably will not.  This is because the code they draw from has evolved over time and we haven't gone back to
update the older notebooks, prefering to preserve them as they were when they last ran cleanly.

```
├── ADFFiveParity.ipynb       - the five parity problem using Automatically Defined Functions
├── AntSimulator.ipynb        - copied straight from deap and run locally
├── App.ipynb                 - a discardable workbook based on an attempt to consolidate code into 'app'
├── Crossover.ipynb           - a breakdown of exactly how crossovers work
├── DeapFeatures.md           - documents all the main routines DEAP make available for Genetic Programming
├── Draw-Trees.ipynb          - a demonstration of drawing a graphic of a generated tree
├── DynamicADFFiveParity.ipynb - a template for nige to run the five parity problem with dynamic ADFs
├── Enter\ the\ Matrix.ipynb   - a demonstration of issues getting DEAP to work with matrices as ephemerals
├── FacesVerticesIntegrals.ipynb - a workbook to help build routines to resolve graphics:which faces are not obscured by others
├── FiveParity.ipynb          - example runs of the basic five parity problem
├── Integral.ipynb            - workbook for identifying issues in integral calculations
├── Integral2.ipynb           - workbook for identifying issues in integral calculations
├── LastJ.ipynb               - workbook to try and understand why `do` loops won't work (without a robot)
├── Mutate.ipynb              - early drawings of mutation
├── Playbook.ipynb            - early drawings of a grown tree
├── ProbablisticSelection.ipynb - workbook to expose probablistic selection algorithm
├── Pythagoras.ipynb          - successful evolution of pythagoras' theorem
├── PythagorasMatrix.ipynb    - successful evolution of pythagoras' theorem using a matix as the program input type
├── README.md                 - this file
├── The\ None\ Available\ Problem.ipynb - exposition of our very first problem growing trees with DEAP
├── Triangles.ipynb           - disposable workbook from trying to come up with a problem to solve involving 2D shapes
├── TwoADFFiveParity.ipynb    - successful evolution of the five parity problem using 2 non-dynamic adfs
├── TypedRandomADF.ipynb      - disposable workbook exposing the generation of adfs
├── ant_santafe_trail.txt     - data for the ant robot problem
├── app                       + DEAP based code which most of the notebooks are based upon
├── canobox                   + an early to attempt to use the 'canobox' python environment
├── deap                      + a copy of DEAP 1.1.0 or thereabouts modified for python3 and USED extensively throughout this project
├── geneticprogramming        + the last iteration of relatively stable code gathered into a module
├── headmesh                  + working copy of PETE's code used for the initial handover and orientation
├── if_then_else_for_but_stuff.ipynb  - workbook attempting loops
├── tests                     + unit tests for pieces of code scattered throughout. Many of the highlevel tests are copied into notebooks for nigels consumption
└── timesheet.md              - a frank daily account of time consumption
```

# Setting up a Python environment (OS X)

Hopefully it is obvious that the penultimate step to getting started is to **clone this repository**.

### Install git

Everybody needs git.
http://www.git-scm.com/

Probably easiest to just use their download install [at downloads](http://www.git-scm.com/downloads)

There's a free GUI for git here, which does have it's uses:  
http://sourcetreeapp.com/


### Install Homebrew

OS X comes with a version of python but Apple have butchered it for their own purposes, so you need to install it again. 
The least painful way is to use brew.  Even if that means installing brew...

http://brew.sh/

which simply instructs you to open a command shell and run this 

```ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```

### Install Python

```brew install python```

**Pip** is python's package manager and is installed with brew. 

So at this point you should be able to run `pip --version` and it should respond with something _vaguely_ like

```
$ pip --version
pip 6.0.8 from /Users/johnmee/Code/nigel/venv/lib/python3.4/site-packages (python 3.4)
```

### Update pip

If pip has a much lower version number.  Upgrade it, and setuptools, with

`pip install -U pip setuptools`

# Install packages

[[ Do not install DEAP from pypi; it is not current, so we have a copy of DEAP commited to our codebase. ]]

*numpy* is used for matrix manupulations used here and there; install trivially with pip
*matplotlib*, *graphviz*, *networkx* are used to make drawings of the generated trees and depends on OS binaries.
*virtualenv* is suggested if you have multiple python projects on one machine
*ipython notebook* is very useful for sharing and visualising python code execution

## Numpy

```$ pip install numpy
```

## virtualenv

https://virtualenv.pypa.io/en/latest/

I use virtualenv to keep all my python projects from interfering with each other.
You almost certainly don't need it, but references to it will inevitably creep into my work
so I mention it here so you've some idea what it is.

* install virtualenv (`pip install virtualenv`)
* create a virtualenv (`virtualenv -p python3 venv`)
* activate the env (`source venv/bin/activate`)
* upgrade pip and setuptools (`pip install -U pip setuptools`)

## python notebook

http://ipython.org/notebook.html

Notebook is extremely useful if a python development involves imaging.
It is generally handy for developing python code.

```
$ pip install ipython[notebook]
$ ipython notebook
```

A browser window will open. There are perhaps some notebooks in there.

## networkx, graphviz, etc for pretty pictures:

_On OS X:_


### Graphviz

Is a binary package of some age, but brew seems to be on top of it.
Note this starts **without** the virtualenv activated—brew doesn't behave predictably otherwise:
```
$ brew install graphviz
```

### Pygraphviz

Now **activate virtualenv**, and I cloned this packages from git because it was unclear if the pypi
version had python3 support.

```
$ git clone https://github.com/pygraphviz/pygraphviz.git
$ cd pygraphviz
$ python3 setup.py install
```

### Networkx

Perfectly straightforward after all that:

```
(venv)$ pip3 install networkx
```

If you want it to draw graphs inside the notebook you must declare matplotlib inline:

```
%matplotlib inline
```

_On Ubuntu:_

I tried a bunch of things so I'm guessing this is the minimal combination.  Ideally, use the `apt` packaging system.
If the virtualenv was created with `no-site-packages` [you'll have to undo that](http://stackoverflow.com/questions/3371136/).

### Graphviz

$ sudo apt-get install graphviz
$ sudo apt-get install python3-matplotlib

### Pygraphviz & Networkx

Thence just use pip, same as above (for OS X).  The pygraphviz had to be the bleeding edge version from git (for py3)


---

The result of `pip freeze` on my development machine currently reads:

```
alabaster==0.7.4
astor==0.5
Babel==1.3
certifi==14.5.14
decorator==3.4.2
docutils==0.12
gnureadline==6.3.3
ipython==3.0.0
Jinja2==2.7.3
jsonschema==2.4.0
MarkupSafe==0.23
matplotlib==1.4.3
mistune==0.5.1
networkx==1.9.1
nose==1.3.4
numpy==1.9.2
Pillow==2.8.0
ptyprocess==0.4
Pygments==2.0.2
pygraphviz==1.3rc2
pyparsing==2.0.3
python-dateutil==2.4.2
pytz==2015.4
pyzmq==14.5.0
six==1.9.0
snowballstemmer==1.2.0
Sphinx==1.3.1
sphinx-rtd-theme==0.1.8
terminado==0.5
tornado==4.1
```

# References

"Elements of Evolutionary Algorithms" Lecture Slides  
http://lmarti.com/wp-content/uploads/2014/09/02-elements-of-eas.pdf  
http://lmarti.com/aec-2014  
["DEAP - Enabling Nimbler Evolutions" - SIGEvolution Vol 6 Issue 2](http://nbviewer.ipython.org/github/DEAP/notebooks/blob/master/SIGEvolution.ipynb)
["DEAP: A python framework for Evolutionary Algorithms"](http://vision.gel.ulaval.ca/~cgagne/pubs/deap-gecco-2012.pdf)
["DEAP: Evolutionary Algorithms made easy" - Journal of machine learning Research 2012](http://www.jmlr.org/papers/volume13/fortin12a/fortin12a.pdf)
["Tom's" dummy-node rewrite of the generate routine](https://gist.github.com/macrintr/9876942)

Distributed Evolutionary Algorithms in Python  
https://github.com/DEAP/deap  
http://deap.readthedocs.org/en/master/  
https://github.com/DEAP/notebooks  
