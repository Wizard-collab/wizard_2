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
PyWizard Application Module

This module defines the main application logic for PyWizard, a software tool designed to manage
projects, users, and tasks in a collaborative environment. It includes the initialization of 
various components such as servers, user settings, project settings, and an interactive console.

Classes:
    app: Represents the main application logic for PyWizard, managing initialization, 
         server setup, and graceful shutdown.

Usage:
    Run this module as the main script to start the PyWizard application.
"""

# Python modules
import OpenEXR
import sys
import os
import traceback
import code
from PyQt6 import QtWidgets
import logging

# Wizard modules
from wizard.core import application
from wizard.core import user
from wizard.core import project
from wizard.core import repository
from wizard.core import tools
from wizard.core import create_project
from wizard.core import communicate
from wizard.core import environment
from wizard.core import launch
from wizard.core import launch_batch
from wizard.core import db_core
from wizard.core import subtasks_library
from wizard.core import subtask
from wizard.core import hooks
from wizard.core import custom_logger

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import gui_server

custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

# Append current dir to sys.path
sys.path.append(os.path.abspath(''))


class app():
    """
    A class representing the main application logic for PyWizard.
    This class initializes and manages various components of the application, 
    including servers, user settings, project settings, and interactive console. 
    It also handles the proper shutdown of all components when the application quits.
    Attributes:
        stats_schedule: An object for managing application statistics scheduling.
        softwares_server: A server object for managing software-related tasks.
        communicate_server: A server object for handling communication tasks.
        tasks_server: A server object for managing subtasks.
    Methods:
        __init__():
            Initializes the application, sets up servers, and starts an interactive console.
        quit():
            Stops all running servers and gracefully exits the application.
    """

    def __init__(self):
        """
        Initializes the PyWizard application.
        This constructor sets up the necessary components and servers required for the application to function.
        It performs the following tasks:
        - Logs application information.
        - Retrieves the application instance.
        - Configures the PyWizard environment.
        - Initializes PostgreSQL DNS, repository, user, project, and OCIO settings.
        - Sets up the statistics scheduler.
        - Starts the communication server for inter-process communication.
        - Launches the software server for managing software-related tasks.
        - Starts the tasks server for handling subtasks.
        - Opens an interactive Python console for debugging or interaction.
        - Ensures proper cleanup and exit when the console is closed.
        """
        self.stats_schedule = None
        self.softwares_server = None
        self.communicate_server = None
        self.tasks_server = None

        application.log_app_infos()

        self.app = app_utils.get_app()

        app_utils.set_pywizard()
        app_utils.init_psql_dns(self)
        app_utils.init_repository(self)
        app_utils.init_user(self)
        app_utils.init_project(self)
        app_utils.init_OCIO()
        self.stats_schedule = app_utils.init_stats()
        self.communicate_server = communicate.communicate_server()
        self.communicate_server.start()
        self.softwares_server = launch.softwares_server()
        self.softwares_server.start()
        self.tasks_server = subtask.tasks_server()
        self.tasks_server.start()

        console = code.InteractiveConsole()
        console.interact(banner=None, exitmsg=None)
        self.quit()

    def quit(self):
        """
        Gracefully shuts down the application by stopping all active servers and schedules,
        and then exits the application.

        This method performs the following steps:
        1. Stops the `stats_schedule` if it is running.
        2. Stops the `softwares_server` if it is running.
        3. Stops the `communicate_server` if it is running.
        4. Stops the `tasks_server` if it is running.
        5. Quits the Qt application.
        6. Exits the Python interpreter.

        Note:
            Ensure that all servers and schedules are properly initialized before calling
            this method to avoid potential errors during shutdown.
        """
        if self.stats_schedule:
            self.stats_schedule.stop()
        if self.softwares_server:
            self.softwares_server.stop()
        if self.communicate_server:
            self.communicate_server.stop()
        if self.tasks_server:
            self.tasks_server.stop()
        QtWidgets.QApplication.quit()
        sys.exit()


if __name__ == '__main__':
    _app = app()
