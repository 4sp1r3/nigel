# Setting up Canopy (OS X Yosemite)

- Install [Canopy Express](https://store.enthought.com/downloads/)
- Change `Preferences->Notebook->PyLab Backend` to `Interactive (wx)`.
- Install Mayavi package: `Tools->Package Manager`. Search for `mayavi` and click `free` to install it.
- Open the editor at this directory.

# Run

- [`playbook.ipynb`](playbook.ipynb) is the current state of fooling around trying to make things happen
- [`app.py`](app.py) is an accumulation of keep code 
- [`timesheet.md`](timesheet.md) maps where the all time goes

![Plot of two heads](canobox/snapshot.png?raw=true "Plot of two heads")

---

# Setting up a (true) Python environment on OS X 

Let's assume you have *nothing*, although that does lengthen the list of prerequisites a little.

## Prerequisites

### Install git

Everybody (in IT) needs git.

http://www.git-scm.com/

Probably easiest to just use their download install [at downloads](http://www.git-scm.com/downloads)

There's a free GUI for git here, which does have it's uses:  
http://sourcetreeapp.com/


### Install Homebrew

Yes, OS X comes with a version of python but Apple have butchered it for their own purposes so you need to install it again. 
There are a few pitfalls to doing it. The least painful is to use brew.  Except that means you need to install brew...

http://brew.sh/

which just says to open a command shell and run this 

```ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```

### Install Python

```brew install python```

Pip is python's package manager.  Because python is pretty boring without it, last I checked brew installs `pip` with `python`. 

At this point you should be able to run `pip --version` and it might respond with something _very_ vaguely like
```
$ pip --version
pip 6.0.8 from /Users/johnmee/Code/nigel/venv/lib/python3.4/site-packages (python 3.4)
```

### Update pip

If pip has a much lower version number.  Upgrade it, and setuptools, with

`pip install -U pip setuptools`

# Install DEAP

```$ pip install deap```

## you'll probably want numpy at some point...

```$ pip install numpy```


# Run the DEAP examples

Clone their repository, then run them:

```
$ git clone https://github.com/DEAP/deap.git deap
```

```
(venv)Johns-iMac:nigel johnmee$ python deap/examples/ga/onemax.py
Start of evolution
  Evaluated 300 individuals
-- Generation 0 --
  Evaluated 181 individuals
  Min 44.0
  Max 66.0
  Avg 54.833333333333336
  Std 4.349584909952722

...

-- Generation 39 --
  Evaluated 180 individuals
  Min 90.0
  Max 100.0
  Avg 98.83333333333333
  Std 2.1100289624131205
-- End of (successful) evolution --
Best individual is [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], (100.0,) 
```

```
(venv)Johns-iMac:nigel johnmee$ python deap/examples/ga/onemax_short.py
gen	nevals	avg    	std    	min	max
0  	300   	50.4933	5.33822	34 	64
1  	181   	54.8333	4.34958	44 	66
2  	191   	58.4567	3.45564	47 	68
3  	199   	60.9533	2.9025 	52 	68
4  	167   	62.96  	2.90719	47 	71
5  	175   	64.99  	2.84896	57 	73
6  	168   	66.9333	2.80515	58 	74
7  	187   	68.9167	2.82661	59 	76
8  	171   	70.8867	2.4455 	62 	76
9  	155   	72.69  	2.62435	62 	80
10 	171   	74.1233	2.61052	64 	82
11 	191   	75.64  	2.70007	65 	82
12 	171   	77.18  	2.55752	69 	84
13 	173   	78.7667	2.24475	69 	84
14 	185   	79.9067	2.36459	72 	86
15 	205   	81.4433	2.3805 	72 	88
16 	163   	82.6767	2.22534	74 	88
17 	175   	83.6833	2.37411	76 	88
18 	181   	84.8067	2.30274	74 	90
19 	179   	85.6233	2.51955	74 	91
20 	178   	86.58  	2.16416	78 	91
21 	173   	87.2533	2.33148	78 	91
22 	155   	88.06  	2.15787	79 	92
23 	187   	88.37  	2.20146	80 	92
24 	184   	89.2767	1.97825	82 	94
25 	198   	89.7767	2.3805 	80 	95
26 	185   	90.6233	2.41553	80 	96
27 	160   	91.62  	2.25291	82 	96
28 	182   	92.45  	2.36379	83 	97
29 	171   	93.2933	2.46589	84 	97
30 	184   	94.1433	2.39919	84 	97
31 	161   	94.91  	2.40594	85 	98
32 	181   	95.4633	2.28954	85 	99
33 	177   	96.02  	2.40962	88 	99
34 	182   	96.7733	2.09172	88 	99
35 	177   	97.0433	2.32554	86 	100
36 	161   	97.3567	2.50122	88 	100
37 	178   	97.9167	2.34302	90 	100
38 	176   	98.4   	2.11345	87 	100
39 	202   	98.2467	2.61007	88 	100
40 	180   	98.8333	2.11003	90 	100
(venv)Johns-iMac:nigel johnmee$
```

## Optional Stuff

### virtualenv

https://virtualenv.pypa.io/en/latest/

I use virtualenv to keep all my python projects from interfering with each other.
You almost certainly don't need it, but references to it will inevitably creep into my work
so I mention it here so you've some idea what it is.

1. (optional)
  * install virtualenv (`pip install virtualenv`)
  * create a virtualenv (`virtualenv -p python3 venv`)
  * activate the env (`source venv/bin/activate`)
  * upgrade pip and setuptools (`pip install -U pip setuptools`)

### python notebook

http://ipython.org/notebook.html

Notebook is extremely useful if a python development involves imaging.
It is generally handy for developing python code.

```
$ pip install ipython[notebook]
$ ipython notebook
```

A browser window will open. There are perhaps some notebooks in there.

(optional) We'll want the numpy library sooner or later so try installing it now (`pip install numpy`)


---

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
