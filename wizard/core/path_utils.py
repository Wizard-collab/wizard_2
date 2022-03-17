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

# Wizard modules
from wizard.core import environment
from wizard.vars import env_vars

def mkdir(path):
	path = clean_path(path)
	return os.mkdir(path)

def makedirs(path):
	path = clean_path(path)
	return os.makedirs(path)

def remove(path):
	path = clean_path(path)
	return os.remove(path)

def copyfile(base, destination):
	base = clean_path(base)
	destination = clean_path(destination)
	return shutil.copyfile(base, destination)

def rmtree(path):
	path = clean_path(path)
	return shutil.rmtree(path)

def rmdir(path):
	path = clean_path(path)
	return os.rmdir(path)

def isdir(path):
	path = clean_path(path)
	return os.path.isdir(path)

def isfile(path):
	path = clean_path(path)
	return os.path.isfile(path)

def join(*args):
	path = os.path.join(*args)
	path = clean_path(path)
	return path

def abspath(path):
	path = os.path.abspath(path)
	path = clean_path(path)
	return path

def dirname(path):
	path = os.path.dirname(path)
	path = clean_path(path)
	return path

def clean_path(path):
	path = path.replace('\\', '/')
	return path

def startfile(path):
	path = clean_path(path)
	return os.startfile(path)