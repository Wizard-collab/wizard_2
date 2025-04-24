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
This module provides functionality for creating and initializing projects 
within the Wizard framework. It includes methods for setting up project 
settings, assets, deadlines, and software configurations, as well as 
initializing project-specific hooks and folders.

Functions:
    - get_default_deadline(): Calculates and returns a default deadline date.
    - create_project(): Creates a new project with specified parameters.
    - init_project(): Initializes a project with settings, assets, and structure.
    - init_hooks(): Sets up project-specific hooks by copying hook files.

Dependencies:
    - Python modules: os, time, datetime, logging
    - Wizard modules: project, user, db_utils, assets, environment, tools, path_utils
    - Wizard variables: assets_vars, project_vars, softwares_vars
"""

# Python modules
import os
import time
import datetime
import logging

# Wizard modules
from wizard.core import project
from wizard.core import user
from wizard.core import db_utils
from wizard.core import assets
from wizard.core import environment
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import assets_vars
from wizard.vars import project_vars
from wizard.vars import softwares_vars

logger = logging.getLogger(__name__)


def get_default_deadline():
    """
    Calculates and returns a default deadline date as a string.

    The default deadline is set to approximately 270 days (23328000 seconds)
    from the current time. The returned date is formatted as 'DD/MM/YYYY'.

    Returns:
        str: The default deadline date in 'DD/MM/YYYY' format.
    """
    deadline_string = datetime.datetime.fromtimestamp(
        time.time()+23328000).strftime('%d/%m/%Y')
    return deadline_string


def create_project(project_name,
                   project_path,
                   project_password,
                   frame_rate=24,
                   image_format=[1920, 1080],
                   project_image=None,
                   deadline=get_default_deadline()):
    """
    Creates a new project with the specified parameters.

    Args:
        project_name (str): The name of the project. Must not be empty.
        project_path (str): The file path where the project will be created. Must not be empty.
        project_password (str): The password for the project. Must not be empty.
        frame_rate (int, optional): The frame rate for the project. Defaults to 24.
        image_format (list, optional): The resolution of the project in [width, height] format. Defaults to [1920, 1080].
        project_image (str, optional): Path to an image associated with the project. Defaults to None.
        deadline (str, optional): The deadline for the project in string format. Defaults to the value returned by `get_default_deadline()`.

    Returns:
        int: Returns 1 if the project is successfully created, otherwise returns None.

    Notes:
        - Logs warnings if required parameters (project_name, project_path, project_password) are not provided.
        - Validates the deadline string and converts it to a float. If invalid, the project creation is aborted.
        - Updates the environment and database with the new project details.
        - Logs the previous project (if any) without credentials.
    """
    # Initialize a flag to determine if project creation should proceed
    do_creation = 1

    # Validate the project name
    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0

    # Validate the project path
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0

    # Validate the project password
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0

    # Convert the deadline string to a float timestamp
    deadline_float = tools.get_time_float_from_string_date(deadline)
    if not deadline_float:
        do_creation = 0

    # Abort project creation if any validation failed
    if not do_creation:
        return

    # Retrieve the name of the currently active project, if any
    old_project_name = environment.get_project_name()

    # Attempt to create the project in the database
    if not project.create_project(project_name, project_path, project_password, project_image):
        return

    # Update the database name to match the new project
    db_utils.modify_db_name('project', project_name)

    # Set up the environment variables for the new project
    environment.build_project_env(project_name, project_path)

    # Initialize the project with its settings, assets, and software configurations
    init_project(project_name, project_path, project_password,
                 frame_rate, image_format, deadline_float)

    # Log the previous project (if any) without credentials
    if old_project_name is not None:
        user.log_project_without_cred(old_project_name)

    # Return success indicator
    return 1


def init_project(project_name,
                 project_path,
                 project_password,
                 frame_rate=24,
                 image_format=[1920, 1080],
                 deadline=time.time()+23328000):
    """
    Initializes a new project with the specified settings and structure.
    Args:
        project_name (str): The name of the project. Must not be empty.
        project_path (str): The file path where the project will be created. Must not be empty.
        project_password (str): The password for the project. Must not be empty.
        frame_rate (int, optional): The frame rate for the project. Defaults to 24.
        image_format (list, optional): The resolution of the project in [width, height] format. Defaults to [1920, 1080].
        deadline (float, optional): The project deadline as a UNIX timestamp. Defaults to the current time plus 23328000 seconds (approximately 270 days).
    Returns:
        int: Returns 1 if the project is successfully initialized, otherwise returns None.
    Raises:
        None: This function does not raise exceptions but logs warnings if required arguments are missing.
    Notes:
        - Creates the project settings, domains, categories, and software configurations.
        - Initializes folders for shared files, scripts, hooks, and plugins.
        - Calls `init_hooks()` to set up project-specific hooks.
        - Logs warnings and halts initialization if required arguments are not provided.
    """
    # Initialize a flag to determine if project initialization should proceed
    do_creation = 1

    # Validate the project name
    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0

    # Validate the project path
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0

    # Validate the project password
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0

    # Abort initialization if any validation failed
    if not do_creation:
        return

    # Create the project settings row in the database
    project.create_settings_row(frame_rate, image_format, deadline)

    # Create domains for the project (e.g., assets, library, sequences)
    for domain in assets_vars._domains_list_:
        assets.create_domain(domain)

    # Create categories within the assets domain
    assets_domain_id = 1
    for category in assets_vars._assets_categories_list_:
        assets.create_category(category, assets_domain_id)

    # Add software configurations to the project
    for software in softwares_vars._softwares_list_:
        software_id = project.add_software(
            software,
            softwares_vars._extensions_dic_[software],
            softwares_vars._file_command_[software],
            softwares_vars._no_file_command_[software],
            softwares_vars._batch_file_command_[software],
            softwares_vars._batch_no_file_command_[software]
        )

        # Create extension rows for each stage and software
        for stage in assets_vars._ext_dic_.keys():
            if software in assets_vars._ext_dic_[stage].keys():
                extension = assets_vars._ext_dic_[stage][software][0]
                project.create_extension_row(stage, software_id, extension)

    # Create necessary folders for the project
    tools.create_folder(project.get_shared_files_folder())
    tools.create_folder(project.get_scripts_folder())
    tools.create_folder(project.get_hooks_folder())
    tools.create_folder(project.get_plugins_folder())

    # Initialize project-specific hooks
    init_hooks()

    # Return success indicator
    return 1


def init_hooks():
    """
    Initializes project hooks by copying hook files from the source directory 
    to the project's hooks folder.

    This function iterates through all files in the 'ressources/hooks' directory 
    and copies each file to the hooks folder of the current project.

    Raises:
        FileNotFoundError: If the source hooks directory does not exist.
        PermissionError: If there are insufficient permissions to read from 
                         the source directory or write to the destination.
        OSError: If an error occurs during file copying.

    Note:
        Ensure that the 'ressources/hooks' directory exists and contains the 
        necessary hook files before calling this function.
    """
    hooks_dir = 'ressources/hooks'
    for file in os.listdir(hooks_dir):
        base = path_utils.join(hooks_dir, file)
        destination = path_utils.join(project.get_hooks_folder(), file)
        path_utils.copyfile(base, destination)
