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

# This module is used to guess and find softwares paths easily

# Python modules
import os

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

program_files = os.environ.get("PROGRAMFILES")

def get_blender():
	to_list = os.path.join(program_files, 'Blender Foundation')
	executables_dic = dict()
	if os.path.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			executable = os.path.join(to_list, version_folder, 'blender.exe')
			if os.path.isfile(executable):
				executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_maya():
	to_list = os.path.join(program_files, 'Autodesk')
	executables_dic = dict()
	if os.path.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			executable = os.path.join(to_list, version_folder, 'bin/maya.exe')
			if os.path.isfile(executable):
				executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_substance_painter():
	executable = os.path.join(program_files,
								'Allegorithmic',
								'Adobe Substance 3D Painter',
								'Adobe Substance 3D Painter.exe')
	if os.path.isfile(executable):
		return {'Adobe Substance 3D Painter':executable.replace('\\', '/')}
	else:
		return None

def get_software_executables(software_name):
	functions_dic = dict()
	functions_dic['blender'] = get_blender
	functions_dic['maya'] = get_maya
	functions_dic['substance_painter'] = get_substance_painter
	return functions_dic[software_name]()