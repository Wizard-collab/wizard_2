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
This module provides functionalities for managing and executing scripts 
in the context of a project shelf. It includes methods for creating, 
editing, and executing scripts, as well as adding separators to the shelf.

The module interacts with various core components of the Wizard framework, 
such as project management, user execution, and subtasks. It also ensures 
proper validation and logging for the operations performed.

Functions:
    - create_project_script: Creates and adds a script to the project's shelf.
    - create_separator: Adds a separator to the shelf.
    - edit_project_script: Edits an existing script in the shelf.
    - execute_script: Executes a script by its ID.
    - execute_script_as_subtask: Executes a script as a subtask.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import project
from wizard.core import subtask
from wizard.core import user
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import ressources

logger = logging.getLogger(__name__)


def create_project_script(name,
                          script,
                          help,
                          only_subprocess=0,
                          icon=ressources._default_script_shelf_icon_):
    """
    Creates a project script and adds it to the project's shelf.
    Args:
        name (str): The name of the tool/script. Must not be empty.
        script (str): The script content to be written to the file. Must not be empty.
        help (str): A short description or help text for the tool. Must not be empty.
        only_subprocess (int, optional): Indicates if the script should only run in a subprocess. Defaults to 0.
        icon (str, optional): The icon to represent the script in the shelf. Defaults to `ressources._default_script_shelf_icon_`.
    Returns:
        int: Returns 1 if the script is successfully created and added to the shelf.
        None: Returns None if any validation fails or if the script cannot be added to the shelf.
    Raises:
        None: This function does not raise exceptions but logs warnings for invalid inputs.
    Notes:
        - The function validates the inputs and logs warnings if any required parameter is missing.
        - The script file is created in the project's scripts folder with a unique name if a file with the same name already exists.
        - The script is added to the project's shelf using the `project.add_shelf_script` method.
    """
    execute = True
    if name is None or name == '':
        logger.warning('Please provide a tool name')
        execute = False
    if script is None or script == '':
        logger.warning('Please provide a script')
        execute = False
    if help is None or help == '':
        logger.warning('Please provide a short help for your tool')
        execute = False
    if not execute:
        return
    scripts_folder = project.get_scripts_folder()
    file_name = f"{name}.py"
    file = tools.get_filename_without_override(
        path_utils.join(scripts_folder, file_name))
    if not project.add_shelf_script(name, file, help, only_subprocess, icon):
        return
    with open(file, 'w') as f:
        f.write(script)
    return 1


def create_separator():
    """
    Creates a separator in the shelf.

    This function adds a separator to the shelf by calling the 
    `add_shelf_separator` method from the `project` module.

    Returns:
        The result of the `add_shelf_separator` method, which 
        typically represents the created separator object or 
        confirmation of the action.
    """
    return project.add_shelf_separator()


def edit_project_script(id,
                        help,
                        icon,
                        only_subprocess=0):
    """
    Edits a project script in the shelf.

    Args:
        id (str): The identifier of the script to be edited.
        help (str): A help description or tooltip for the script.
        icon (str): The path or reference to the icon associated with the script.
        only_subprocess (int, optional): A flag indicating whether the script should 
            only be executed in a subprocess. Defaults to 0.

    Returns:
        Any: The result of the `edit_shelf_script` method from the `project` module.
    """
    return project.edit_shelf_script(id, help, icon, only_subprocess)


def execute_script(script_id):
    """
    Executes a Python script associated with the given script ID.

    Args:
        script_id (str): The identifier of the script to execute.

    Returns:
        int: Returns 1 if the script is successfully executed, otherwise None.
    """
    py_file = project.get_shelf_script_data(script_id, 'py_file')
    if not py_file:
        return
    user.user().execute_py(py_file)
    return 1


def execute_script_as_subtask(script_id):
    """
    Executes a script as a subtask based on the provided script ID.

    This function retrieves the Python file path associated with the given
    script ID from the project's shelf script data. If the file path exists,
    it creates and starts a subtask using the specified Python file.

    Args:
        script_id (str): The unique identifier of the script to execute.

    Returns:
        int: Returns 1 if the subtask is successfully started.
        None: Returns None if the Python file path is not found.
    """
    py_file = project.get_shelf_script_data(script_id, 'py_file')
    if not py_file:
        return
    task = subtask.subtask(pycmd=py_file)
    task.start()
    return 1
