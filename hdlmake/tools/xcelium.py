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

"""Module providing support for Cadence xcelium simulation"""


from __future__ import absolute_import
import os
import string

import six

from .makefilesim import MakefileSim
from ..sourcefiles.srcfile import VerilogFile, VHDLFile, SVFile
from ..util import shell
from ..util import path as path_mod

class ToolXceliumSim(MakefileSim):

    """Class providing the interface for Cadence xcelium synthesis"""

    TOOL_INFO = {
        'name': 'xcelium',
        'id': 'xcelium',
        'windows_bin': 'xrun',
        'linux_bin': 'xrun',
    }

    STANDARD_LIBS = ['ieee', 'std']

    HDL_FILES = {VerilogFile: '', VHDLFile: '', SVFile: ''}

    CLEAN_TARGETS = {'clean': ['cds.lib', 'xm*.log','hdl.var', '.simvision', 'xmsim.key'],
                     'mrproper': []}

    SIMULATOR_CONTROLS = {'vlog' : 'xmvlog -quiet -64bit $(VLOG_FLAGS) $<',
                          'svlog': 'xmvlog -quiet -64bit $(VLOG_FLAGS) -sv $<',
                          'vhdl' : 'xmvhdl -quiet -64bit $(VCOM_FLAGS) $<',
                          'map'  : 'xmelab -quiet -64bit $(VMAP_FLAGS) -timescale 1ns/10ps $(TOP_MODULE) ',
                          'run'  : 'xmsim  -quiet -64bit $(VSIM_FLAGS) $(TOP_MODULE) ',
                          'cdslib':'cds.lib',
                          'incdir':'-incdir '}

    def __init__(self):
        super(ToolXceliumSim, self).__init__()
        # These are variables that will be set in the makefile
        # The key is the variable name, and the value is the variable value
        self.custom_variables = {}
        # Additional sim dependencies (e.g. tcl)
        self.additional_deps = []
        # These are files copied into your working directory by a make rule
        # The key is the filename, the value is the file source path
        self.copy_rules = {}

    def _makefile_sim_options(self):
        """Print the vsim options to the Makefile"""
        vcom_flags = "" + self.manifest_dict.get("vcom_opt", '')
        vsim_flags = "" + self.manifest_dict.get("vsim_opt", '')
        vlog_flags = "" + self.manifest_dict.get("vlog_opt", '')
        vmap_flags = "" + self.manifest_dict.get("vmap_opt", '')
        for var, value in six.iteritems(self.custom_variables):
            self.writeln("%s := %s" % (var, value))
        self.writeln()
        self.writeln("VCOM_FLAGS := %s" % vcom_flags)
        self.writeln("VSIM_FLAGS := %s" % vsim_flags)
        self.writeln("VLOG_FLAGS := %s" % vlog_flags)
        self.writeln("VMAP_FLAGS := %s" % vmap_flags)

        sim_post_cmd = self.manifest_dict.get("sim_post_cmd", '')
        self.manifest_dict["sim_post_cmd"] = '\n\t\t'.join([self.SIMULATOR_CONTROLS['map'], self.SIMULATOR_CONTROLS['run'], sim_post_cmd])

    def _makefile_sim_compilation(self):
        """Write a properly formatted Makefile for the simulator.
        The Makefile format is shared, but flags, dependencies, clean rules,
        etc are defined by the specific tool.
        """
        fileset = self.fileset
        if self.manifest_dict.get("include_dirs") is None:
            self.writeln("INCLUDE_DIRS :=")
        else:
            self.writeln("INCLUDE_DIRS := %s" %
#                ((' '+self.SIMULATOR_CONTROLS['incdir']).join(self.manifest_dict.get("include_dirs"))))
                (" ".join([self.SIMULATOR_CONTROLS['incdir']+d for d in self.manifest_dict.get("include_dirs")])))
        libs = sorted(set(f.library for f in fileset))
        self.write('LIBS := ')
        self.write(' '.join(libs))
        self.write('\n')
        # tell how to make libraries
        self.write('LIB_IND := ')
        self.write(' '.join([lib + shell.makefile_slash_char() +
                   "." + lib for lib in libs]))
        #self.write(" ".join(['cds.lib', 'hdl.var']))
        self.write(" hdl.var")
        self.write('\n')
        self.writeln()
        self.writeln(
            "simulation: %s $(LIB_IND) $(VERILOG_OBJ) $(VHDL_OBJ)" %
            (' '.join(self.additional_deps)),)
        self.writeln("\t\t{tool}".format(
            tool=self.SIMULATOR_CONTROLS['run']))
        self.writeln()
        self.writeln("$(VERILOG_OBJ): " + ' '.join(self.additional_deps))
        self.writeln("$(VHDL_OBJ): $(LIB_IND) " + ' '.join(self.additional_deps))
        self.writeln()
        for filename, filesource in six.iteritems(self.copy_rules):
            self.writeln("{}: {}".format(filename, filesource))
            self.writeln("\t\t{} $< . 2>&1".format(shell.copy_command()))

        cdspath = os.environ.get("CDS_SITE")
        if not cdspath:
            cdshome=os.environ.get("VRST_HOME")
            if cdshome:
                cdspath=cdshome+"/tools.lnx86/xcelium/files/"

        if cdspath:
            self.writeln("\t\techo \"SOFTINCLUDE {cdspath}/$@\" > $@".format(cdspath=cdspath))
        else:
            self._makefile_touch_stamp_file()
        self.writeln()

        self.writeln("cds.lib:Makefile")
        if cdspath:
            self.writeln("\t\techo \"SOFTINCLUDE {cdspath}/$@\" > $@".format(cdspath=cdspath))
        else:
            self._makefile_touch_stamp_file()
        self.writeln()

        for lib in libs:
            libpath=lib
            self.write(libpath + shell.makefile_slash_char() + "." + lib + ":cds.lib\n")
            self.writeln("\t\t@echo define {lib} {libpath}>>{cdslib}"
                         "".format(
                lib=lib, libpath=libpath, cdslib=self.SIMULATOR_CONTROLS['cdslib'],
                touch=shell.touch_command(), slash=shell.makefile_slash_char(),
                rm=shell.del_command()))
            self._makefile_touch_stamp_file()
            self.writeln()
        # rules for all _primary.dat files for sv
        for vlog in fileset.filter(VerilogFile).sort():
            self._makefile_sim_file_rule(vlog)
            incdirs=" ".join([self.SIMULATOR_CONTROLS['incdir']+d for d in vlog.include_dirs])
            self.writeln("\t\t{vlogtool} -work {library} {incdirs} $(INCLUDE_DIRS)".format(
                vlogtool=self.SIMULATOR_CONTROLS['svlog'] if isinstance(vlog, SVFile) else self.SIMULATOR_CONTROLS['vlog'],
                library=vlog.library,
                incdirs=incdirs,
                ))
            self._makefile_touch_stamp_file()
            self.writeln()
        # list rules for all _primary.dat files for vhdl
        for vhdl in fileset.filter(VHDLFile).sort():
            self._makefile_sim_file_rule(vhdl)
            self.writeln("\t\t{vhdltool} -work {library}".format(
                vhdltool=self.SIMULATOR_CONTROLS['vhdl'], library=vhdl.library))
            self._makefile_touch_stamp_file()
            self.writeln()

        self.writeln("debug:VMAP_FLAGS+= -access +rwc")
        self.writeln("debug:VSIM_FLAGS+= -gui")
        self.writeln("debug: sim_pre_cmd simulation sim_post_cmd")
        self.writeln("local:VSIM_FLAGS+= -batch")

        self.writeln()

