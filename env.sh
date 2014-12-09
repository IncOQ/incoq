#!/bin/sh

# Adjust PYTHONPATH in the current shell to include Oinc and dependencies.
# Invoke as `source env.sh` or `source env.sh -w`.
#
# The -w flag is for Cygwin environments which use a non-Cygwin
# (native Windows) Python interpreter. It causes the path entries
# to be added in Windows format.


getopts w WINPATH
# Since we're invoked as a source script, clean up after ourselves
# or we can't run twice.
OPTIND=1
OPTARG=

# Courtesy http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

NEWENTRIES="$DIR/oinc:$DIR/simplestruct:$DIR/iast:$DIR/frexp:$DIR/gendb:$DIR/distalgo"

if [ $WINPATH = "w" ]; then
    NEWENTRIES=`cygpath -wp $NEWENTRIES`
    SEP=';'
else
    SEP=':'
fi

if [ -z $PYTHONPATH ]; then
    SEP=''
fi

export PYTHONPATH="${PYTHONPATH}${SEP}${NEWENTRIES}"
echo "Updated PYTHONPATH."
