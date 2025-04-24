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

# This module build the wizard environment
# ( Current project and current user )
# It permits to avoid some database access
# during the use of the application

"""
This module is responsible for building and managing the Wizard environment.
It provides functions to set and retrieve various environment variables 
related to the current project, user, and application settings. These 
environment variables help reduce database access during the application's 
runtime by storing necessary information in the environment.

Key functionalities include:
- Setting and retrieving GUI mode status.
- Managing user-related environment variables (username, email).
- Managing project-related environment variables (project name, path).
- Setting and retrieving server ports for different services.
- Managing PostgreSQL DNS and team DNS configurations.
- Setting and retrieving repository information.

The module uses the `os` module to interact with environment variables 
and the `json` module for handling JSON data in environment variables.
"""

# Pyton modules
import os
import json
import logging

# Wizard modules
from wizard.vars import env_vars

logger = logging.getLogger(__name__)


# Function to set whether the application is running in GUI mode
def set_gui(is_gui):
    os.environ[env_vars._wizard_gui_] = str(is_gui)
    return 1

# Function to check if the application is running in GUI mode


def is_gui():
    return int(os.environ[env_vars._wizard_gui_])


# Function to build the user environment variables
# Sets the username and email in the environment
def build_user_env(user_row):
    os.environ[env_vars._username_env_] = user_row['user_name']
    os.environ[env_vars._useremail_env_] = user_row['email']
    return 1

# Function to build the project environment variables
# Sets the project name and project path in the environment


def build_project_env(project_name, project_path):
    os.environ[env_vars._project_name_env_] = project_name
    os.environ[env_vars._project_path_env_] = project_path
    return 1


# Function to set the PostgreSQL DNS in the environment
def set_psql_dns(DNS):
    os.environ[env_vars._psql_dns_] = DNS
    return 1

# Function to set the OpenColorIO (OCIO) configuration in the environment


def set_OCIO(OCIO):
    os.environ['OCIO'] = OCIO


# Function to get the PostgreSQL DNS from the environment
def get_psql_dns():
    if env_vars._psql_dns_ not in os.environ.keys():
        logger.error('No PostgreSQL DNS defined')
        return
    return os.environ[env_vars._psql_dns_]

# Function to set the communicate server port in the environment


def set_communicate_server_port(port):
    os.environ[env_vars._communicate_server_port_] = str(port)
    return 1


# Function to set the softwares server port in the environment
def set_softwares_server_port(port):
    os.environ[env_vars._softwares_server_port_] = str(port)
    return 1

# Function to get the softwares server port from the environment


def get_softwares_server_port():
    if env_vars._softwares_server_port_ not in os.environ.keys():
        logger.error('No softwares server port defined')
        return
    return int(os.environ[env_vars._softwares_server_port_])

# Function to set the GUI server port in the environment


def set_gui_server_port(port):
    os.environ[env_vars._gui_server_port_] = str(port)
    return 1

# Function to get the GUI server port from the environment


def get_gui_server_port():
    if env_vars._gui_server_port_ not in os.environ.keys():
        logger.debug('No gui server port defined')
        return
    return int(os.environ[env_vars._gui_server_port_])


# Function to set the subtasks server port in the environment
def set_subtasks_server_port(port):
    os.environ[env_vars._subtasks_server_port_] = str(port)
    return 1


# Function to get the subtasks server port from the environment
def get_subtasks_server_port():
    if env_vars._subtasks_server_port_ not in os.environ.keys():
        logger.debug('No subtasks server port defined')
        return
    return int(os.environ[env_vars._subtasks_server_port_])


# Function to set the local database server port in the environment
def set_local_db_server_port(port):
    os.environ[env_vars._local_db_server_port_] = str(port)
    return 1


# Function to get the local database server port from the environment
def get_local_db_server_port():
    if env_vars._local_db_server_port_ not in os.environ.keys():
        logger.error('No local db server port defined')
        return
    return int(os.environ[env_vars._local_db_server_port_])


# Function to set the team DNS in the environment
# Stores the DNS as a JSON string in the environment variable
def set_team_dns(DNS):
    os.environ[env_vars._team_dns_] = json.dumps(DNS)
    return 1


# Function to get the team DNS from the environment
# Retrieves and parses the JSON string stored in the environment variable
def get_team_dns():
    if env_vars._team_dns_ not in os.environ.keys():
        logger.debug('No team DNS defined')
        return
    return json.loads(os.environ[env_vars._team_dns_])


# Function to get the username from the environment
def get_user():
    if env_vars._username_env_ not in os.environ.keys():
        logger.error('No user defined')
        return
    return os.environ[env_vars._username_env_]

# Function to get the user email from the environment


def get_user_email():
    if env_vars._useremail_env_ not in os.environ.keys():
        logger.error('No user email defined')
        return
    return os.environ[env_vars._useremail_env_]


# Function to get the project name from the environment
# Retrieves the project name stored in the environment variable
def get_project_name():
    if env_vars._project_name_env_ not in os.environ.keys():
        logger.info('No project defined')
        return
    return os.environ[env_vars._project_name_env_]


# Function to get the project path from the environment
# Retrieves the project path stored in the environment variable
def get_project_path():
    if env_vars._project_path_env_ not in os.environ.keys():
        logger.info('No project defined')
        return
    return os.environ[env_vars._project_path_env_]


# Function to get the repository from the environment
# Retrieves the repository stored in the environment variable
def get_repository():
    if env_vars._repository_env_ not in os.environ.keys():
        logger.error('No repository defined')
        return
    return os.environ[env_vars._repository_env_]


# Function to set the repository in the environment
# Stores the repository in the environment variable with a prefix
def set_repository(repository):
    os.environ[env_vars._repository_env_] = f"repository_{repository}"
    return 1
