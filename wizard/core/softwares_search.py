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
import logging

# Wizard modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)

program_files = os.environ.get("PROGRAMFILES")

def get_blender():
	to_list = path_utils.join(program_files, 'Blender Foundation')
	executables_dic = dict()
	if path_utils.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			executable = path_utils.join(to_list, version_folder, 'blender.exe')
			if path_utils.isfile(executable):
				executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_maya():
	to_list = path_utils.join(program_files, 'Autodesk')
	executables_dic = dict()
	if path_utils.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			executable = path_utils.join(to_list, version_folder, 'bin/maya.exe')
			if path_utils.isfile(executable):
				executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_guerilla():
	executable = path_utils.join(program_files,
								'Guerilla Render',
								'guerilla.exe')
	if path_utils.isfile(executable):
		return {'Guerilla Render':executable.replace('\\', '/')}
	else:
		return None

def get_substance_painter():
	executable = path_utils.join(program_files,
								'Adobe',
								'Adobe Substance 3D Painter',
								'Adobe Substance 3D Painter.exe')
	if path_utils.isfile(executable):
		return {'Adobe Substance 3D Painter':executable.replace('\\', '/')}
	else:
		return None

def get_substance_designer():
	executable = path_utils.join(program_files,
								'Adobe',
								'Adobe Substance 3D Designer',
								'Adobe Substance 3D Designer.exe')
	if path_utils.isfile(executable):
		return {'Adobe Substance 3D Designer':executable.replace('\\', '/')}
	else:
		return None


def get_houdini():
	to_list = path_utils.join(program_files, 'Side Effects Software')
	executables_dic = dict()
	if path_utils.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			executable = path_utils.join(to_list, version_folder, 'bin/houdini.exe')
			if path_utils.isfile(executable):
				executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_nuke():
	to_list = program_files
	executables_dic = dict()

	if path_utils.isdir(to_list):
		versions = os.listdir(to_list)
		for version_folder in versions:
			if version_folder.startswith("Nuke"):
				files = os.listdir(path_utils.join(to_list, version_folder))
				for file in files:
					if file.startswith("Nuke") and file.endswith('.exe'):
						executable = path_utils.join(to_list, version_folder, file)
						if path_utils.isfile(executable):
							executables_dic[version_folder] = executable.replace('\\', '/')

	if executables_dic != dict():
		return executables_dic
	else:
		return None

def get_software_executables(software_name):
	functions_dic = dict()
	functions_dic['guerilla_render'] = get_guerilla
	functions_dic['blender'] = get_blender
	functions_dic['maya'] = get_maya
	functions_dic['substance_painter'] = get_substance_painter
	functions_dic['substance_designer'] = get_substance_designer
	functions_dic['houdini'] = get_houdini
	functions_dic['nuke'] = get_nuke
	if software_name in functions_dic.keys():
		return functions_dic[software_name]()
	else:
		return None