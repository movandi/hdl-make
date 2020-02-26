#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 - 2020 CERN
# Author: Pawel Szostek (pawel.szostek@cern.ch)
# Multi-tool support by Javier D. Garcia-Lasheras (javier@garcialasheras.com)
#
# This file is part of Hdlmake.
#
# Hdlmake is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hdlmake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hdlmake.  If not, see <http://www.gnu.org/licenses/>.
#

"""Module providing support for Cadence Incisive simulation"""


from __future__ import absolute_import
from .makefilesim import MakefileSim
from ..sourcefiles.srcfile import VerilogFile, VHDLFile, SVFile

class ToolIncisiveSim(MakefileSim):

    """Class providing the interface for Cadence Incisive synthesis"""

    TOOL_INFO = {
        'name': 'incisive',
        'id': 'incisive',
        'windows_bin': 'irun',
        'linux_bin': 'irun',
    }

    STANDARD_LIBS = ['ieee', 'std']

    HDL_FILES = {VerilogFile: '', VHDLFile: '', SVFile: ''}

    CLEAN_TARGETS = {'clean': [],
                     'mrproper': []}

    SIMULATOR_CONTROLS = {'vlog': 'ncvlog -sv $(VLOGCOMP_FLAGS) $<',
                          'vhdl': 'ncvhdl $<',
                          'compiler': 'ncelab -access +r -v200x -vhdlsync $(TOP_MODULE) '}

    def __init__(self):
        super(ToolIncisiveSim, self).__init__()

    def _makefile_sim_compilation(self):
        """Generate compile simulation Makefile target for Incisive Simulator"""

        self.writeln("")
        self.writeln("")
        self.writeln("VLOGCOMP_FLAGS := \\")
        for inc in self.manifest_dict.get("include_dirs", []):
            self.writeln("\t\t-incdir " + inc + "\\")
        self.writeln("")
        self.writeln("simulation: $(VERILOG_OBJ) $(VHDL_OBJ)")
        self.writeln("\t\t" + self.SIMULATOR_CONTROLS['compiler'])
        self.writeln()
        self._makefile_sim_dep_files()
