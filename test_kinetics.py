# Copyright (C) 2013 Matthew C. Zwier and Lillian T. Chong
#
# This file is part of WESTPA.
#
# WESTPA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WESTPA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WESTPA.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, print_function
from westpa.binning.assign import (RectilinearBinMapper, PiecewiseBinMapper, FuncBinMapper, VectorizingFuncBinMapper, 
                                 VoronoiBinMapper, RecursiveBinMapper)
from westpa.binning.assign import index_dtype, coord_dtype
from westpa.binning._assign import testfunc #@UnresolvedImport
from westpa import h5io

import numpy
from scipy.spatial.distance import cdist
import nose
import nose.tools

import w_direct, w_reweight, w_assign
import os, subprocess
# Import the work manager so we can hook into them.
import work_managers

import tempfile
EPS = numpy.finfo(numpy.float64).eps

#u_to_b = { 'direct': numpy.float64('3.001660233293609e-04'), 'reweight': numpy.float64('3.009828540338903e-04') }
#b_to_u = { 'direct': numpy.float64('3.744796693524487e-05'), 'reweight': numpy.float64('3.760925972510064e-05') }

import logging
log = logging.getLogger(__name__)

class TestKinetics:
    def setUp(self):
        # Here, we pull in the main h5 file, and run the assignment routines.
        self.path = tempfile.mkdtemp()
        assign_config = { 'west': 'odld/{}.h5'.format('west'), 'output': os.path.join(self.path, '{}.h5'.format('assign')) , 'states_from_file': 'odld/STATES', 'bins_from_file': 'odld/BINS' }
        args = []
        for key,value in assign_config.iteritems():
            args.append(str('--') + str(key).replace('_', '-'))
            args.append(str(value))
        assign = w_assign.WAssign()
        assign.make_parser_and_process(args=args)
        assign.work_manager = work_managers.SerialWorkManager()
        assign.go()
    def call_analysis(self, name):
        # This works for either analysis routine.  We tend to get slightly different answers from the reweighting routine (which is okay!), but they're usually the same.
        # u_to_b and b_to_u should be 'known good values' for each tool.
        analysis_config = { 'west': 'odld/{}.h5'.format('west'), 'assignments': os.path.join(self.path, '{}.h5'.format('assign')), 'output': os.path.join(self.path, '{}.h5'.format(name)), 'kinetics': os.path.join(self.path, '{}.h5'.format(name))}
        analysis_config.update({ 'step_iter': 1, 'e': 'cumulative' })
        if name == 'direct':
            analysis = w_direct.WDirect()
        if name == 'reweight':
            analysis = w_reweight.WReweight()
        args = ['all']
        for key,value in analysis_config.iteritems():
            args.append(str('--') + str(key).replace('_', '-'))
            args.append(str(value))
        # Don't print averages, and don't run bootstrap.  We're not testing the bootstrap, after all, just the estimator routines.
        args.append('--disable-averages')
        args.append('-db')
        analysis.make_parser_and_process(args=args)
        analysis.work_manager = work_managers.SerialWorkManager()
        analysis.go()
        # Load the output and test it against the known good file.
        output = h5io.WESTPAH5File(os.path.join(self.path, '{}.h5'.format(name)), 'r')
        test = h5io.WESTPAH5File(os.path.join('odld/{}.h5'.format(name)), 'r')
        # check rate evolution!
        # If our rates agree, we can generally assume that our other values are good, too.
        orates = output['rate_evolution'][-1,:,:]['expected']
        trates = output['rate_evolution'][-1,:,:]['expected']
        assert abs(orates[0,1] - trates[0,1]) <= EPS
        assert abs(orates[1,0] - trates[1,0]) <= EPS
    def test_direct(self):
        self.call_analysis('direct')
    def test_reweight(self):
        self.call_analysis('reweight')
    def tearDown(self):
        p = subprocess.Popen('rm -r ' + self.path, shell=True, env=os.environ)
