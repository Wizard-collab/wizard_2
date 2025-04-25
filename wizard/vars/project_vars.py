# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module defines global variables used throughout the Wizard project.
It includes paths and filenames for various project resources such as the 
project database, shared files, thumbnails, scripts, hooks, and plugins.
Attributes:
    _project_database_file_ (str): The filename of the project database.
    _shared_files_folder_ (str): The folder containing shared files.
    _thumbnails_folder_ (str): The folder containing thumbnail images, 
        located within the shared files folder.
    _scripts_folder_ (str): The folder containing project-specific scripts.
    _hooks_folder_ (str): The folder containing hooks for extending functionality.
    _plugins_folder_ (str): The folder containing plugins for the project.
"""

_project_database_file_ = 'project.db'
_shared_files_folder_ = 'shared_files'
_thumbnails_folder_ = f'{_shared_files_folder_}/thumbnails'
_scripts_folder_ = 'scripts'
_hooks_folder_ = 'hooks'
_plugins_folder_ = 'plugins'
