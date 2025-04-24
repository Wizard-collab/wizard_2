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
This module provides functionality to launch batch export processes for specific software versions.
It includes methods to construct commands, set up environment variables, and execute batch processes.

Main Functions:
- batch_export: Launches a batch export process for a given version ID.
- add_settings_dic_to_env: Adds additional settings to the environment variables.
- build_command: Constructs the command string for launching the batch process.

Dependencies:
- Python modules: subprocess, shlex, json, logging
- Wizard modules: launch, project, path_utils, softwares_vars
"""

# Python modules
import subprocess
import shlex
import json
import logging

# Wizard modules
from wizard.core import launch
from wizard.core import project
from wizard.core import path_utils
from wizard.vars import softwares_vars

logger = logging.getLogger(__name__)


def batch_export(version_id, settings_dic=None):
    """
    Launches a batch export process for a given version ID using the specified settings.

    Args:
        version_id (int): The ID of the version to be exported.
        settings_dic (dict, optional): A dictionary of additional settings to be added to the environment. Defaults to None.

    Returns:
        int: Returns 1 if the batch process is successfully launched and completed.
             Returns None if the process cannot be launched due to missing data or invalid command.

    Raises:
        KeyError: If required keys are missing in the retrieved data.
        subprocess.SubprocessError: If there is an issue with launching the subprocess.

    Workflow:
        1. Retrieves version data for the given version ID.
        2. Extracts file path, work environment ID, and software ID from the version data.
        3. Builds the command to launch the batch process.
        4. Constructs the environment variables for the batch process.
        5. Adds additional settings from `settings_dic` to the environment.
        6. Launches the batch process using the constructed command and environment.
        7. Waits for the process to complete and logs the start and end of the process.
    """
    # Retrieve version data for the given version ID
    work_version_row = project.get_version_data(version_id)
    if not work_version_row:
        return

    # Extract file path, work environment ID, and software ID
    file_path = work_version_row['file_path']
    work_env_id = work_version_row['work_env_id']
    software_id = project.get_work_env_data(work_env_id, 'software_id')

    # Retrieve software data using the software ID
    software_row = project.get_software_data(software_id)

    # Build the command to launch the batch process
    command = build_command(file_path, software_row, version_id)

    # Construct the environment variables for the batch process
    env = launch.build_env(work_env_id, software_row, version_id, mode='batch')

    # Add additional settings from `settings_dic` to the environment
    env = add_settings_dic_to_env(env, settings_dic)

    # If the command is invalid, exit the function
    if not command:
        return

    # Launch the batch process using the constructed command and environment
    process = subprocess.Popen(args=shlex.split(
        command), env=env, cwd=path_utils.abspath('softwares'))

    # Log the start of the process
    logger.info(f"{software_row['name']} launched")

    # Wait for the process to complete
    process.wait()

    # Log the end of the process
    logger.info(f"{software_row['name']} closed")

    # Return 1 to indicate successful completion
    return 1


def add_settings_dic_to_env(env, settings_dic):
    """
    Adds a dictionary of settings to the provided environment dictionary by 
    serializing it into a JSON string and storing it under the key 
    'wizard_json_settings'.

    Args:
        env (dict): The environment dictionary to which the settings will be added.
        settings_dic (dict): The dictionary of settings to be serialized and added.

    Returns:
        dict: The updated environment dictionary containing the serialized settings.
    """
    env['wizard_json_settings'] = json.dumps(settings_dic)
    return env


def build_command(file_path, software_row, version_id):
    """
    Constructs a command string to launch a batch process for a given software.

    Args:
        file_path (str): The path to the file to be processed. If the file does not exist, 
                         the command will be adjusted to launch the software with an empty scene.
        software_row (dict): A dictionary containing software-specific information, including:
                             - 'batch_path': The path to the batch executable for the software.
                             - 'batch_file_command': The command template to use when a file exists.
                             - 'batch_no_file_command': The command template to use when no file exists.
                             - 'name': The name of the software.
        version_id (int): The version identifier for the software (not used in the current implementation).

    Returns:
        str: The constructed command string with placeholders replaced by actual values, or None if 
             the batch path is not defined.

    Logs:
        - Logs a warning if the batch path for the software is not defined.
        - Logs an informational message if the file does not exist and the software is launched with an empty scene.

    Notes:
        - The function uses `softwares_vars` for placeholder keys and script mappings.
        - The command templates in `software_row` should include placeholders such as `_executable_key_`, 
          `_file_key_`, and `_script_key_` for substitution.
    """
    # Retrieve the batch path for the software
    software_batch_path = software_row['batch_path']
    if software_batch_path == '':
        # Log a warning if the batch path is not defined
        logger.warning(f"{software_row['name']} batch path not defined")
        return

    # Check if the file exists and select the appropriate command template
    if path_utils.isfile(file_path):
        raw_command = software_row['batch_file_command']
    else:
        raw_command = software_row['batch_no_file_command']
        # Log an informational message if the file does not exist
        logger.info("File not existing, launching software with empty scene")

    # Replace placeholders in the command template with actual values
    raw_command = raw_command.replace(
        softwares_vars._executable_key_, software_batch_path)
    raw_command = raw_command.replace(softwares_vars._file_key_, file_path)

    # If the software has a specific batch script, replace the script placeholder
    if software_row['name'] in softwares_vars._batch_scripts_dic_.keys():
        raw_command = raw_command.replace(softwares_vars._script_key_,
                                          softwares_vars._batch_scripts_dic_[software_row['name']])

    # Return the constructed command
    return raw_command
