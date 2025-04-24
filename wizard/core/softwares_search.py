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
This module provides functions to search for installed software executables
on a Windows system. It specifically targets software commonly used in
3D modeling, rendering, and visual effects, such as Blender, Maya, Houdini,
and others. The functions return the paths to the executables if found,
or None otherwise.

Each function is tailored to search for a specific software by checking
its default installation directory under the "Program Files" environment
variable. The paths are formatted with forward slashes for consistency.

Functions:
    - get_blender: Searches for Blender installations.
    - get_maya: Searches for Autodesk Maya installations.
    - get_guerilla: Searches for Guerilla Render installations.
    - get_substance_painter: Searches for Adobe Substance 3D Painter installations.
    - get_substance_designer: Searches for Adobe Substance 3D Designer installations.
    - get_houdini: Searches for Houdini installations.
    - get_nuke: Searches for Nuke installations.
    - get_software_executables: Retrieves executable paths for a given software name.

Dependencies:
    - os: For interacting with the file system.
    - logging: For logging messages.
    - path_utils: Custom utility module for path operations.

Note:
    This module assumes a Windows environment and standard installation paths.
"""

# Python modules
import os
import logging

# Wizard modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)

program_files = os.environ.get("PROGRAMFILES")


def get_blender():
    """
    Searches for installed versions of Blender in the default installation directory
    and returns a dictionary of version folders mapped to their respective executable paths.

    Returns:
        dict: A dictionary where keys are version folder names and values are the paths
              to the corresponding 'blender.exe' executables, with paths formatted using
              forward slashes. Returns None if no Blender installations are found.
    """
    to_list = path_utils.join(program_files, 'Blender Foundation')
    executables_dic = dict()
    if not path_utils.isdir(to_list):
        return
    versions = os.listdir(to_list)
    for version_folder in versions:
        executable = path_utils.join(to_list, version_folder, 'blender.exe')
        if path_utils.isfile(executable):
            executables_dic[version_folder] = executable.replace('\\', '/')
    if executables_dic == dict():
        return
    return executables_dic


def get_maya():
    """
    Searches for installed Autodesk Maya versions on the system and returns a dictionary
    mapping version folder names to their respective executable paths.

    The function looks for Maya installations in the 'Autodesk' directory under the 
    'Program Files' directory. It checks for the presence of the 'maya.exe' executable 
    in the 'bin' folder of each version directory.

    Returns:
        dict: A dictionary where the keys are version folder names and the values are 
              the paths to the 'maya.exe' executables, with forward slashes as path 
              separators. Returns None if no Maya installations are found or if the 
              'Autodesk' directory does not exist.
    """
    to_list = path_utils.join(program_files, 'Autodesk')
    executables_dic = dict()
    if not path_utils.isdir(to_list):
        return
    versions = os.listdir(to_list)
    for version_folder in versions:
        executable = path_utils.join(to_list, version_folder, 'bin/maya.exe')
        if path_utils.isfile(executable):
            executables_dic[version_folder] = executable.replace('\\', '/')
    if executables_dic == dict():
        return
    return executables_dic


def get_guerilla():
    """
    Retrieves the file path to the Guerilla Render executable if it exists.

    This function constructs the path to the Guerilla Render executable
    located in the Program Files directory. If the executable file exists,
    it returns a dictionary containing the software name as the key and the
    executable path (with forward slashes) as the value. If the file does not
    exist, the function returns None.

    Returns:
        dict: A dictionary with the software name as the key and the executable
              path as the value, or None if the executable is not found.
    """
    executable = path_utils.join(program_files,
                                 'Guerilla Render',
                                 'guerilla.exe')
    if not path_utils.isfile(executable):
        return
    return {'Guerilla Render': executable.replace('\\', '/')}


def get_substance_painter():
    """
    Retrieves the file path for the Adobe Substance 3D Painter executable if it exists.

    This function constructs the expected file path for the Adobe Substance 3D Painter
    executable based on the standard installation directory. It checks if the file exists
    at the constructed path and returns a dictionary containing the software name as the key
    and the executable path (with forward slashes) as the value. If the executable is not found,
    the function returns None.

    Returns:
        dict or None: A dictionary with the software name as the key and the executable path
        as the value if the file exists, otherwise None.
    """
    executable = path_utils.join(program_files,
                                 'Adobe',
                                 'Adobe Substance 3D Painter',
                                 'Adobe Substance 3D Painter.exe')
    if not path_utils.isfile(executable):
        return
    return {'Adobe Substance 3D Painter': executable.replace('\\', '/')}


def get_substance_designer():
    """
    Retrieves the file path for the Adobe Substance 3D Designer executable if it exists.

    This function constructs the expected file path for the Adobe Substance 3D Designer
    executable based on the standard installation directory. It checks if the file exists
    at the constructed path. If the executable is found, it returns a dictionary containing
    the software name as the key and the file path (with forward slashes) as the value.
    If the executable is not found, the function returns None.

    Returns:
        dict: A dictionary with the software name as the key and the executable path as the value,
              or None if the executable is not found.
    """
    executable = path_utils.join(program_files,
                                 'Adobe',
                                 'Adobe Substance 3D Designer',
                                 'Adobe Substance 3D Designer.exe')
    if not path_utils.isfile(executable):
        return
    return {'Adobe Substance 3D Designer': executable.replace('\\', '/')}


def get_houdini():
    """
    Searches for installed Houdini software versions in the default installation directory
    and returns a dictionary of version folders mapped to their executable paths.

    The function checks the "Side Effects Software" directory inside the Program Files
    directory for Houdini installations. It iterates through the version folders, verifies
    the existence of the Houdini executable, and collects the paths.

    Returns:
        dict: A dictionary where keys are version folder names and values are the paths
              to the corresponding Houdini executables, with backslashes replaced by forward slashes.
              Returns None if the directory does not exist or no executables are found.
    """
    to_list = path_utils.join(program_files, 'Side Effects Software')
    executables_dic = dict()
    if not path_utils.isdir(to_list):
        return
    versions = os.listdir(to_list)
    for version_folder in versions:
        executable = path_utils.join(
            to_list, version_folder, 'bin/houdini.exe')
        if path_utils.isfile(executable):
            executables_dic[version_folder] = executable.replace('\\', '/')
    if executables_dic == dict():
        return
    return executables_dic


def get_nuke():
    """
    Searches for Nuke executable files within a specified directory structure.
    This function scans the `program_files` directory for folders starting with "Nuke".
    Within each of these folders, it looks for executable files that also start with "Nuke"
    and have a `.exe` extension. If found, it constructs a dictionary where the keys are
    the version folder names and the values are the paths to the corresponding executables.
    Returns:
        dict: A dictionary mapping version folder names to their respective executable paths,
              with paths formatted using forward slashes. Returns `None` if no executables
              are found or if the `program_files` directory does not exist.
    """
    to_list = program_files
    executables_dic = dict()
    if not path_utils.isdir(to_list):
        return
    versions = os.listdir(to_list)
    for version_folder in versions:
        if version_folder.startswith("Nuke"):
            files = os.listdir(path_utils.join(to_list, version_folder))
            for file in files:
                if file.startswith("Nuke") and file.endswith('.exe'):
                    executable = path_utils.join(to_list, version_folder, file)
                    if path_utils.isfile(executable):
                        executables_dic[version_folder] = executable.replace(
                            '\\', '/')

    if executables_dic == dict():
        return
    return executables_dic


def get_software_executables(software_name):
    """
    Retrieves the executable path or relevant information for a given software.

    This function maps software names to their corresponding retrieval functions
    and executes the appropriate function to get the desired information.

    Args:
        software_name (str): The name of the software for which the executable 
                             or relevant information is to be retrieved.

    Returns:
        The result of the corresponding retrieval function for the given software 
        name, or None if the software name is not recognized.

    Note:
        Supported software names include:
        - 'guerilla_render'
        - 'blender'
        - 'maya'
        - 'substance_painter'
        - 'substance_designer'
        - 'houdini'
        - 'nuke'
    """
    functions_dic = dict()
    functions_dic['guerilla_render'] = get_guerilla
    functions_dic['blender'] = get_blender
    functions_dic['maya'] = get_maya
    functions_dic['substance_painter'] = get_substance_painter
    functions_dic['substance_designer'] = get_substance_designer
    functions_dic['houdini'] = get_houdini
    functions_dic['nuke'] = get_nuke
    if software_name not in functions_dic.keys():
        return
    return functions_dic[software_name]()
