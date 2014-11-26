#!/bin/sh

# Adjust PYTHONPATH to include InvInc and dependencies.
# Assumes we're being run from the root of the project tree.
# For Cygwin environments, invoke as `env.sh true` to use
# windows-style paths and separators, which is necessary
# when using a native windows (non-Cygwin) Python.

export PYTHONPATH="$PWD/invinc:$PWD/simplestruct:$PWD/iast:$PWD/frexp:$PWD/gendb:$PWD/distalgo"

if ${1-false} ; then
    export PYTHONPATH=`cygpath -wp $PYTHONPATH`
fi
