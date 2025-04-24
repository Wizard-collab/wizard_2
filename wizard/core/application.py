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
This module provides core functionalities for the Wizard application, including:
- Retrieving version information from a YAML file.
- Adding the 'binaries' directory to the system PATH.
- Logging application information such as version and license details.

It also initializes a logger for logging errors and other messages.
"""

# Python modules
import yaml  # For reading and parsing YAML files
import os  # For interacting with the operating system
import sys  # For system-specific parameters and functions
import time  # For working with time-related functions
import logging  # For logging messages

# Wizard modules
from wizard.core import path_utils  # Custom module for path-related utilities

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def get_version():
    # Function to retrieve the version information from a YAML file
    version_file = 'ressources/version.yaml'  # Path to the version file
    if not path_utils.isfile(version_file):  # Check if the file exists
        # Log an error if the file is missing
        logger.error(f'{version_file} not found')
        return None  # Return None if the file is not found
    with open(version_file, 'r') as f:  # Open the version file in read mode
        # Parse the YAML file into a dictionary
        version_dic = yaml.load(f, Loader=yaml.Loader)
    return version_dic  # Return the parsed version dictionary


def add_binaries_to_path():
    # Function to add the 'binaries' directory to the system PATH
    # Get the absolute path of the 'binaries' directory
    binaries_path = os.path.abspath('binaries')
    # Append the path to the system PATH environment variable
    os.environ['PATH'] += os.pathsep + binaries_path


def log_app_infos():
    # Function to log application information
    print('')  # Print an empty line for formatting
    log_version()  # Log the version information
    print('')  # Print another empty line
    log_license()  # Log the license information
    print('')  # Print another empty line


def log_version():
    # Function to log the version information
    version_dic = get_version()  # Retrieve the version dictionary
    # Print the version details in a formatted string
    print(
        f"Wizard {version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']} build {version_dic['builds']},{time.ctime(version_dic['date'])}")


def log_license():
    # Function to log the license information
    with open('ressources/LICENSE', 'r') as f:  # Open the LICENSE file in read mode
        print(f.read())  # Print the contents of the LICENSE file


# Add the current directory to the system path
sys.path.append(os.path.abspath(''))

# Add the 'binaries' directory to the system PATH
add_binaries_to_path()
