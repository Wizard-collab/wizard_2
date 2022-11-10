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
import os
import shutil
import logging

# Wizard modules
from wizard.core import environment
from wizard.vars import env_vars

logger = logging.getLogger(__name__)

def mkdir(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.mkdir(path)

def makedirs(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	if os.path.isdir(path):
		return True
	return os.makedirs(path)

def remove(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.remove(path)

def copyfile(base, destination):
	if base is None:
		logger.info("No base file given")
		return
	if destination is None:
		logger.info("No destination file given")
		return
	base = clean_path(base)
	destination = clean_path(destination)
	return shutil.copyfile(base, destination)

def rmtree(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return shutil.rmtree(path)

def rmdir(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.rmdir(path)

def isdir(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.path.isdir(path)

def listdir(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.listdir(path)

def isfile(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.path.isfile(path)

def join(*args):
	path = os.path.join(*args)
	path = clean_path(path)
	return path

def abspath(path):
	if path is None:
		logger.info("No path given")
		return
	path = os.path.abspath(path)
	path = clean_path(path)
	return path

def dirname(path):
	if path is None:
		logger.info("No path given")
		return
	path = os.path.dirname(path)
	path = clean_path(path)
	return path

def clean_path(path):
	if path is None:
		logger.info("No path given")
		return
	path = path.replace('\\', '/')
	return path

def startfile(path):
	if path is None:
		logger.info("No path given")
		return
	path = clean_path(path)
	return os.startfile(path)