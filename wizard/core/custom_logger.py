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
import logging
import os

# Wizard modules
from wizard.vars import user_vars

def get_logger(name=None):
    # create logger
    # Use this module to keep logger format
    # integrity across wizard application
    logger_level = logging.INFO
    logging.basicConfig(level=logger_level,
        format="%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s")
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger()
    create_prefs_folder()
    file_handler = logging.FileHandler(user_vars._user_logger_file_)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s'))
    logger.addHandler(file_handler)
    return logger

def create_prefs_folder():
    if not os.path.isdir(user_vars._user_path_):
        os.mkdir(user_vars._user_path_)