# NFA & DFA Rendering in JGraph
## Getting Started
Make sure `numpy` version > `19.0.0` is installed, alongside Python 3.7+. Older versions of Python 3 should work but
type annotations may be an issue.
Please read the following sections on how to use this software. The basic usage is:

`python3 main.py [-h] [--det] [--graph-path GRAPH_PATH] [--out OUT] fsm_path`

Run `python3 main.py -h` for more detailed usage instructions.

## Specifying State Machines
State machines can be described in a text file. Integers and strings not containing whitespace
are acceptable names for states. The format is as follows:

`Start:START_STATE`

`Accept:{STATE1,STATE2,...}` where these braces are required.

`Edges:`

`FROM_STATE,SYMBOL->TO_STATE` where the arrow is required.

`...`

`EOF` This is not a string literal, just denoting that the file may end after the last edge.

The state machine description file is the first and only positional argument.

## Specifying Graphing Configuration:
State machines require a graphing file in order to be represented in JGraph. Following the
rules and conventions set by the state machine description format, the format of these files
is as follows:

`States:`

`STATE:X,Y`

`...`

`Edges:`

`X1,Y1,X2,Y2` where (X1, Y1) is the second point of a Bezier curve and (X2, Y2) is the third point.
The first and fourth points are the locations of the states being transition from and to, respectively.

`...`

`EOF` Again, this is not a string literal, just denoting that the file may end after the last edge's curve.

The edges should be given in the same order in the graphing file as they appear in the state machine
description file. A blank file can be generated using the following code:

`graph = Graph(fsm)` assuming we already have a state machine initialized. This will set all the curve control points
to zero, including the positions for the states.

`fp.write(graph.dumps())` where `fp` is an open file handle for the graph file we want to write to.

From here, this graph file can be edited in a text editor to manipulate how the edges and states are drawn.