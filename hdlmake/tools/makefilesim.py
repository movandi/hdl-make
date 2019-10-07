"""Module providing the simulation functionality for writing Makefiles"""

from __future__ import absolute_import
import os
import sys
import logging

from .makefile import ToolMakefile
from ..util import shell
from ..sourcefiles.srcfile import VerilogFile, VHDLFile, SVFile


def _check_simulation_manifest(manifest_dict):
    """Check if the simulation keys are provided by the top manifest"""
    if manifest_dict.get("sim_top") is None:
        raise Exception("sim_top variable must be set in the top manifest.")


class MakefileSim(ToolMakefile):

    """Class that provides the Makefile writing methods and status"""

    def __init__(self):
        super(MakefileSim, self).__init__()
        self._simulator_controls = {}

    def write_makefile(self, config, fileset, filename=None):
        """Execute the simulation action"""
        _check_simulation_manifest(config)
        self.makefile_setup(config, fileset, filename=filename)
        self.makefile_check_tool('sim_path')
        self.makefile_includes()
        self._makefile_sim_top()
        self._makefile_sim_options()
        self._makefile_sim_local()
        self._makefile_sim_sources()
        self._makefile_sim_compilation()
        self._makefile_sim_command()
        self._makefile_sim_clean()
        self._makefile_sim_phony()
        self.makefile_close()

    def _makefile_sim_top(self):
        """Generic method to write the simulation Makefile top section"""
        top_parameter = """\
TOP_MODULE := {top_module}
"""
        self.writeln(top_parameter.format(
            top_module=self.manifest_dict["sim_top"]))

    def _makefile_sim_options(self):
        """End stub method to write the simulation Makefile options section"""
        pass

    def _makefile_sim_compilation(self):
        """End stub method to write the simulation Makefile compilation
        section"""
        pass

    def _makefile_sim_local(self):
        """Generic method to write the simulation Makefile local target"""
        self.writeln("#target for performing local simulation\n"
                     "local: sim_pre_cmd simulation sim_post_cmd\n")

    def get_stamp_file(self, file):
        """Stamp file for source file :param file:"""
        return os.path.join(
                    file.library,
                    file.purename,
                    ".{}_{}".format(file.purename, file.extension()))

    def _makefile_sim_sources(self):
        """Generic method to write the simulation Makefile HDL sources"""
        fileset = self.fileset
        self.write("VERILOG_SRC := ")
        for vlog in fileset.filter(VerilogFile).sort():
            if vlog.is_include:
                continue
            self.writeln(vlog.rel_path() + " \\")
        self.writeln()
        self.write("VERILOG_OBJ := ")
        for vlog in fileset.filter(VerilogFile).sort():
            if vlog.is_include:
                continue
            # make a file compilation indicator (these .dat files are made even
            # if the compilation process fails) and add an ending according
            # to file's extension (.sv and .vhd files may have the same
            # corename and this causes a mess
            self.writeln(self.get_stamp_file(vlog) + " \\")
        self.writeln()
        self.write("VHDL_SRC := ")
        for vhdl in fileset.filter(VHDLFile).sort():
            self.writeln(vhdl.rel_path() + " \\")
        self.writeln()
        # list vhdl objects (_primary.dat files)
        self.write("VHDL_OBJ := ")
        for vhdl in fileset.filter(VHDLFile).sort():
            # file compilation indicator (important: add _vhd ending)
            self.writeln(self.get_stamp_file(vhdl) + " \\")
        self.writeln()

    def _makefile_sim_dep_files(self):
        """Print dummy targets to handle file dependencies"""
        fileset = self.fileset.sort()
        for file_aux in fileset:
            # Consider only HDL files.
            if isinstance(file_aux, tuple(self._hdl_files)):
                self.write("{}: {}".format(self.get_stamp_file(file_aux), file_aux.rel_path()))
                # list dependencies, do not include the target file
                for dep_file in sorted(file_aux.depends_on, key=(lambda x: x.file_path)):
                    if dep_file is file_aux:
                        # Do not depend on itself.
                        continue
                    if dep_file in fileset:
                        self.write(" \\\n" + self.get_stamp_file(dep_file))
                    else:
                        # the file is included -> we depend directly on it
                        self.write(" \\\n" + dep_file.rel_path())
                self.writeln()
                is_include = False
                if isinstance(file_aux, VHDLFile):
                    command_key = 'vhdl'
                elif (isinstance(file_aux, VerilogFile) or
                      isinstance(file_aux, SVFile)):
                    is_include = file_aux.is_include
                    command_key = 'vlog'
                if is_include:
                    continue
                self.writeln("\t\t" + self._simulator_controls[command_key])
                self.write("\t\t@" + shell.mkdir_command() + " $(dir $@)")
                self.writeln(" && " + shell.touch_command()  + " $@ \n")
                self.writeln()

    def _makefile_sim_command(self):
        """Generic method to write the simulation Makefile user commands"""
        sim_pre_cmd = self.manifest_dict.get("sim_pre_cmd", '')
        sim_post_cmd = self.manifest_dict.get("sim_post_cmd", '')
        sim_command = """# USER SIM COMMANDS
sim_pre_cmd:
\t\t{sim_pre_cmd}
sim_post_cmd:
\t\t{sim_post_cmd}
"""
        self.writeln(sim_command.format(sim_pre_cmd=sim_pre_cmd,
                                        sim_post_cmd=sim_post_cmd))

    def _makefile_sim_clean(self):
        """Generic method to write the simulation Makefile user clean target"""
        self.makefile_clean()
        self.makefile_mrproper()

    def _makefile_sim_phony(self):
        """Print simulation PHONY target list to the Makefile"""
        self.writeln(
            ".PHONY: mrproper clean sim_pre_cmd sim_post_cmd simulation")