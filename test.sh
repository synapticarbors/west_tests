#! /bin/bash

if [[ -z $WEST_ROOT ]]; then
    echo 'WEST_ROOT must be set.'
    exit 1
fi

# Ensure everything we need is added to the path.
PATH_AFFIX="$WEST_ROOT/lib/blessings:$WEST_ROOT/lib/h5py:$WEST_ROOT/lib/wwmgr:$WEST_ROOT/src:$WEST_ROOT/lib/west_tools"
if [ -z "$PYTHONPATH" ] ; then
    export PYTHONPATH="$PATH_AFFIX"
else
    export PYTHONPATH="$PATH_AFFIX:$PYTHONPATH"
fi

nosetests
