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
This script is the main entry point for the Wizard command-line interface.
It initializes the application environment, parses command-line arguments,
and executes a specified Python script within the Wizard environment.

The script performs the following tasks:
1. Sets up logging and application information.
2. Parses command-line arguments for PostgreSQL DNS, repository, user, project, team DNS, and a Python file to execute.
3. Validates the provided arguments and logs errors for missing ones.
4. Configures the environment based on the provided arguments.
5. Starts necessary servers for communication and software management.
6. Executes the specified Python file within the configured environment.
7. Ensures proper cleanup of resources upon completion or error.

Modules used:
- Python standard modules: argparse, traceback, json, logging
- Wizard core modules: application, environment, repository, user, project, assets, custom_logger, db_core, communicate, launch, hooks, launch_batch
- Wizard GUI modules: gui_utils, app_utils
"""

# Python modules
import PyOpenColorIO  # For OpenColorIO configuration
import argparse
import traceback
import json
import logging

# Wizard modules
from wizard.core import application
from wizard.core import environment
from wizard.core import repository
from wizard.core import user
from wizard.core import project
from wizard.core import assets
from wizard.core import custom_logger
from wizard.core import db_core
from wizard.core import communicate
from wizard.core import launch
from wizard.core import hooks
from wizard.core import launch_batch
from wizard.gui import gui_utils
from wizard.gui import app_utils

# Initialize the custom logger and get the logger for this module
custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

# Log application information and initialize the application
application.log_app_infos()
app = app_utils.get_app()
app_utils.set_wizard_cmd()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-psqlDns', dest='psql_dns', type=str,
                    help='PostgreSQL connection DNS')
parser.add_argument('-repository', dest='repository',
                    type=str, help='Wizard repository')
parser.add_argument('-user', dest='user', type=str, help='Wizard user')
parser.add_argument('-project', dest='project',
                    type=str, help='Wizard project')
parser.add_argument('-teamDns', dest='team_dns', type=str,
                    help='Wizard team connection DNS')
parser.add_argument('-pyfile', dest='pyfile', type=str,
                    help='The python file to execute')
args = parser.parse_args()

# Validate and log the provided arguments
if not args.psql_dns:
    logger.error("Please provide a PostgreSQL DNS")
else:
    logger.info(f"PostgreSQL DNS : {args.psql_dns}")

if not args.repository:
    logger.error("Please provide a repository")
else:
    logger.info(f"repository : {args.repository}")

if not args.user:
    logger.error("Please provide a user")
else:
    logger.info(f"User : {args.user}")

if not args.project:
    logger.error("Please provide a project")
else:
    logger.info(f"Project : {args.project}")

if not args.team_dns:
    logger.error("No team DNS defined")
else:
    logger.info(f"Team DNS : {args.team_dns}")

if not args.pyfile:
    logger.error("Please provide a python file to execute")
else:
    logger.info(f"Pyfile : {args.pyfile}")

# Configure the environment with the provided arguments
environment.set_psql_dns(args.psql_dns)
environment.set_repository(args.repository)
db_core.db_access_singleton().set_repository(environment.get_repository())

# Set up user environment
user_row = repository.get_user_row_by_name(args.user)
environment.build_user_env(user_row)

# Set up project environment
project_row = repository.get_project_row_by_name(args.project)
environment.build_project_env(
    project_row['project_name'], project_row['project_path'])

db_core.db_access_singleton().set_project(environment.get_project_name())

# Start communication and software servers
communicate_server = communicate.communicate_server()
communicate_server.start()

softwares_server = launch.softwares_server()
softwares_server.start()

# Initialize Wizard hooks
hooks.init_wizard_hooks()

# Set team DNS if provided
if args.team_dns:
    environment.set_team_dns(args.team_dns)

# Execute the specified Python file and handle errors
try:
    exec(open(args.pyfile).read())
except:
    logger.error(str(traceback.format_exc()))
finally:
    # Stop servers and clean up resources
    softwares_server.stop()
    communicate_server.stop()
