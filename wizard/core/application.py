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

# Python modules
import yaml
import os
import sys
import time
import logging

# Wizard modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)


def get_version():
    version_file = 'ressources/version.yaml'
    if not path_utils.isfile(version_file):
        logger.error(f'{version_file} not found')
        return None
    with open(version_file, 'r') as f:
        version_dic = yaml.load(f, Loader=yaml.Loader)
    return version_dic


def add_binaries_to_path():
    binaries_path = os.path.abspath('binaries')
    os.environ['PATH'] += os.pathsep+binaries_path


def log_app_infos():
    print('')
    log_version()
    print('')
    log_license()
    print('')


def log_version():
    version_dic = get_version()
    print(
        f"Wizard {version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']} build {version_dic['builds']},{time.ctime(version_dic['date'])}")


def log_license():
    with open('ressources/LICENSE', 'r') as f:
        print(f.read())


sys.path.append(os.path.abspath(''))
add_binaries_to_path()
