InvInc is a system for generating incremental and demand-driven
implementations of object-set queries. The current source tree
is a development version.

## Configuration

InvInc requires Python 3.4.

To clone, run

    git clone https://github.com/InvInc/invinc.git

cd to the project directory, and run

    git submodule update --init

The following directories should be on the PYTHONPATH, relative to
the project root:

    .        (i.e., the project root)
    simplestruct
    iast
    frexp    (optional; needed for benchmarks)
    distalgo (optional; needed for distalgo benchmarks)
    gendb    (optional; not yet publicly available)
    osq      (optional; not yet publicly available)

These paths can be added to a bash shell by sourcing the env.sh script.
Use the -w flag on Windows/Cygwin.

In addition, the following 3rd-party Python libraries are used:

    bintrees    (needed for aggregate queries, can otherwise be omitted)
    tabulate    (optional)
    numpy       (optional; needed for benchmarks)
    matplotlib  (optional; needed for benchmarks)

 ## Invocation
 
 A single input file may be transformed by running
 
     python34 -m invinc <input file> <output file>
