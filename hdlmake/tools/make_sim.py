"""Module providing the simulation functionality for writing Makefiles"""

import os
import string

from .makefile import ToolMakefile


class ToolSim(ToolMakefile):

    """Class that provides the Makefile writing methods and status"""

    def __init__(self):
        super(ToolSim, self).__init__()

    def makefile_sim_top(self, top_module):
        """Generic method to write the simulation Makefile top section"""
        top_parameter = string.Template("""\
TOP_MODULE := ${top_module}
PWD := $$(shell pwd)
""")
        self.writeln(top_parameter.substitute(
            top_module=top_module.manifest_dict["sim_top"]))

    def makefile_sim_options(self, top_module):
        """End stub method to write the synthesis Makefile options section"""
        pass

    def makefile_sim_local(self, top_module):
        """Generic method to write the simulation Makefile local target"""
        self.writeln("#target for performing local simulation\n"
                     "local: sim_pre_cmd simulation sim_post_cmd\n")

    def makefile_sim_sources(self, fileset):
        """Generic method to write the simulation Makefile HDL sources"""
        from hdlmake.srcfile import VerilogFile, VHDLFile
        self.write("VERILOG_SRC := ")
        for vlog in fileset.filter(VerilogFile):
            self.writeln(vlog.rel_path() + " \\")
        self.writeln()
        self.write("VERILOG_OBJ := ")
        for vlog in fileset.filter(VerilogFile):
            # make a file compilation indicator (these .dat files are made even
            # if the compilation process fails) and add an ending according
            # to file's extension (.sv and .vhd files may have the same
            # corename and this causes a mess
            self.writeln(
                os.path.join(
                    vlog.library,
                    vlog.purename,
                    "." +
                    vlog.purename +
                    "_" +
                    vlog.extension(
                    )) +
                " \\")
        self.writeln()
        self.write("VHDL_SRC := ")
        for vhdl in fileset.filter(VHDLFile):
            self.write(vhdl.rel_path() + " \\\n")
        self.writeln()
        # list vhdl objects (_primary.dat files)
        self.write("VHDL_OBJ := ")
        for vhdl in fileset.filter(VHDLFile):
            # file compilation indicator (important: add _vhd ending)
            self.writeln(
                os.path.join(
                    vhdl.library,
                    vhdl.purename,
                    "." +
                    vhdl.purename +
                    "_" +
                    vhdl.extension(
                    )) +
                " \\")
        self.writeln()

    def makefile_sim_command(self, top_module):
        """Generic method to write the simulation Makefile user commands"""
        if top_module.manifest_dict["sim_pre_cmd"]:
            sim_pre_cmd = top_module.manifest_dict["sim_pre_cmd"]
        else:
            sim_pre_cmd = ''
        if top_module.manifest_dict["sim_post_cmd"]:
            sim_post_cmd = top_module.manifest_dict["sim_post_cmd"]
        else:
            sim_post_cmd = ''
        sim_command = string.Template("""# USER SIM COMMANDS
sim_pre_cmd:
\t\t${sim_pre_cmd}
sim_post_cmd:
\t\t${sim_post_cmd}
""")
        self.writeln(sim_command.substitute(sim_pre_cmd=sim_pre_cmd,
                                            sim_post_cmd=sim_post_cmd))

    def makefile_sim_clean(self):
        """Generic method to write the simulation Makefile user clean target"""
        self.makefile_clean()
        self.makefile_mrproper()

    def makefile_sim_phony(self, top_module):
        """Print simulation PHONY target list to the Makefile"""
        self.writeln(
            ".PHONY: mrproper clean sim_pre_cmd sim_post_cmd simulation")