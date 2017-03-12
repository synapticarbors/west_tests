=================
WESTPA 1.0b Tests
=================

--------
Overview
--------

Automated testing for the correctness of tool output (kinetics/flux/stateprobs/etc) from the WESTPA suite.

See https://github.com/westpa/westpa.

Currently using the nose framework to test the correctness of the estimator functions used for kinetics analysis.

When making modifications to the kinetics routines (either w_direct or w_reweight), re-run this analysis to ensure
that everything works.

When running, ensure that WEST_ROOT/{lib} is in your python path.

    export PYTHON_PATH=$WEST_ROOT:$PYTHON_PATH
    nosetests

Alternatively, source west and run nosetests.
