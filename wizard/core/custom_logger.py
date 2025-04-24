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
This module provides custom logging functionality for the Wizard application.

It includes the following features:
1. A root logger configuration function (`get_root_logger`) that sets up logging
    to both a file and the console, with log levels determined by command-line arguments.
2. A utility function (`create_prefs_folder`) to ensure the existence of the user
    preferences folder required for logging.

Dependencies:
- Python's built-in `logging` module for log handling.
- `sys` module for accessing command-line arguments.
- `wizard.vars.user_vars` for user-specific variables like log file paths.
- `wizard.core.path_utils` for file system path operations.

Usage:
- Call `get_root_logger()` to configure and retrieve the root logger.
- The logger writes logs to a file and outputs them to the console.
- Ensure the user preferences folder exists by invoking `create_prefs_folder()`.
"""

# Python modules
import logging
import sys

# Wizard modules
from wizard.vars import user_vars
from wizard.core import path_utils


def get_root_logger():
    """
    Configures and returns the root logger for the application.
    This function sets up the root logger with two handlers:
    1. A file handler that writes log messages to a file specified by 
       `user_vars._user_logger_file_`.
    2. A stream handler that outputs log messages to the console.
    The log level is determined based on the presence of 'DEBUG' in the 
    command-line arguments (`sys.argv`). If 'DEBUG' is present, the log 
    level is set to `DEBUG`. Otherwise, it defaults to `INFO`.
    The log message format for both handlers is:
    `%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s`.
    Additionally, this function ensures that the preferences folder is 
    created by calling `create_prefs_folder()`.
    Returns:
        logging.Logger: The configured root logger instance.
    """
    create_prefs_folder()
    root_logger = logging.getLogger()
    if 'DEBUG' in sys.argv:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(user_vars._user_logger_file_)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s'))
    root_logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s'))
    root_logger.addHandler(stream_handler)


def create_prefs_folder():
    """
    Ensures that the user preferences folder exists. If the folder does not exist,
    it creates the necessary directories.

    This function checks the directory path specified in `user_vars._user_path_`.
    If the directory does not exist, it uses `path_utils.makedirs` to create it.

    Dependencies:
        - `path_utils`: A module providing utilities for file system path operations.
        - `user_vars._user_path_`: A variable containing the path to the user preferences folder.

    Raises:
        OSError: If the directory cannot be created due to file system permissions or other issues.
    """
    if not path_utils.isdir(user_vars._user_path_):
        path_utils.makedirs(user_vars._user_path_)
