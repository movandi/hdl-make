#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 CERN
# Author: Pawel Szostek (pawel.szostek@cern.ch)
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

# Note that the order here is important. The constants must be
# defined first! If they are not, there will likely be an obscure error
# when doing the imports within the imports that come afterwards.
GIT = 1
SVN = 2
LOCAL = 3


from .svn import Svn
from .git import Git
from .local import Local
from .backend_factory import BackendFactory


# Initialize an instance of BackendFactory which will be made publicly available
fetch_type_lookup = BackendFactory()
fetch_type_lookup.register_backend(GIT, Git)
fetch_type_lookup.register_backend(SVN, Svn)
fetch_type_lookup.register_backend(LOCAL, Local)
