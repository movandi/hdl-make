"""Provides the core functionality for the HDLMake module"""

import os
import logging

from hdlmake import fetch
from hdlmake.util import path as path_mod


class ModuleConfig(object):
    """This class containt the base properties and methods that
    need to be initialized for a proper behavior"""
    def __init__(self):
        self.source = None
        self.parent = None
        self.url = None
        self.branch = None
        self.revision = None
        self.path = None
        self.isfetched = False

    def process_manifest(self):
        """process_manifest does nothing for ModuleConfig"""
        pass

    def basename(self):
        """Get the basename for the module"""
        if self.source == fetch.SVN:
            return path_mod.svn_basename(self.url)
        else:
            return path_mod.url_basename(self.url)

    def fetchto(self):
        """Get the fetchto folder for the module"""
        return os.path.dirname(self.path)

    def init_config(self, parent, url, source, fetchto):
        """This initializes the module configuration.
        The function is executed by Module constructor"""
        self.source = source
        self.parent = parent

        if self.source != fetch.LOCAL:
            self.url, self.branch, self.revision = \
                path_mod.url_parse(url)
            basename = self.basename()
            path = os.path.abspath(os.path.join(fetchto, basename))
            # Check if the module dir exists and is not empty
            if os.path.exists(path) and os.listdir(path):
                self.path = path
                self.isfetched = True
                logging.debug("Module %s (parent: %s) is fetched.",
                    url, self.parent.path)
            else:
                self.path = path
                self.isfetched = False
                logging.debug("Module %s (parent: %s) is NOT fetched.",
                    url, self.parent.path)
        else:
            self.url, self.branch, self.revision = url, None, None

            if not os.path.exists(url):
                logging.error(
                    "Path to the local module doesn't exist:\n" + url
                    + "\nThis module was instantiated in: " + str(self.parent))
                quit()
            self.path = url
            self.isfetched = True



class ModuleCore(ModuleConfig):
    """This is the class providing the module core functionality"""
    def __init__(self):
        # Universal Manifest Properties
        self.library = "work"
        self.action = None
        self.force_tool = None
        self.pool = None
        self.top_module = None
        self.manifest_dict = None
        self.top_entity = None
        super(ModuleCore, self).__init__()


    def set_pool(self, pool):
        """Set the associated pool for the module instance"""
        self.pool = pool
        self.top_module = pool.get_top_module()


    def process_manifest(self):
        """Method that process the core manifest section"""
        self._process_manifest_force_tool()
        self._process_manifest_universal()
        super(ModuleCore, self).process_manifest()


    def _process_manifest_force_tool(self):
        """Method processing the force_tool manifest directive"""
        if self.manifest_dict["force_tool"]:
            force_tool = self.manifest_dict["force_tool"]
            self.force_tool = force_tool.split(' ')
            if len(self.force_tool) != 3:
                logging.warning("Incorrect force_tool format %s. Ignoring",
                    self.force_tool)
                self.force_tool = None


    def _process_manifest_universal(self):
        """Method processing the universal manifest directives"""
        #if "top_module" in self.manifest_dict:
        #    self.top_module = self.manifest_dict["top_module"]
        # Libraries
        self.library = self.manifest_dict["library"]
        self.action = self.manifest_dict["action"].lower()


