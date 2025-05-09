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
This module defines the main application logic for the Wizard software.
It includes the initialization of the application, GUI setup, and the main event loop.
The module also handles logging, error handling, and database modifications.

Classes:
    app: Represents the main application, managing initialization, GUI setup, and quitting.

Functions:
    main: Entry point for the application, setting up the app instance and running the event loop.

Modules Imported:
    - Python modules: PyOpenColorIO, sys, time, PyQt6, logging
    - Wizard core modules: application, custom_logger, version_database_modification
    - Wizard GUI modules: app_utils, loading_widget, main_widget, table_viewer_widget, error_handler
"""

# Python modules
import PyOpenColorIO  # For OpenColorIO configuration
import sys  # For system-specific parameters and functions
import time  # For measuring performance and handling time
from PyQt6 import QtWidgets, QtCore, QtGui  # For GUI components
import logging  # For logging messages

# Wizard core modules
from wizard.core import application  # Core application utilities
from wizard.core import custom_logger  # Custom logging setup
# Handles version database updates
from wizard.core import version_database_modification

# Wizard GUI modules
from wizard.gui import app_utils  # GUI utility functions
from wizard.gui import loading_widget  # Loading screen widget
from wizard.gui import main_widget  # Main application widget
from wizard.gui import table_viewer_widget  # Table viewer widget
import error_handler  # Error handling utilities

# Initialize the root logger for the application
custom_logger.get_root_logger()
logger = logging.getLogger('wizard')  # Logger for this module


class app():
    """
    The `app` class serves as the main entry point for initializing and managing the Wizard application. 
    It sets up the application's GUI, initializes various components, and handles the application's lifecycle.
    Attributes:
        stats_schedule (object): Scheduler for managing application statistics.
        app (QApplication): The main Qt application instance.
        warning_tooltip (object): Tooltip for displaying warnings.
        loading_widget (object): Widget displayed during application loading.
        table_viewer (object, optional): Widget for viewing tables, initialized if requested.
        main_widget (object): The main application widget.
    Methods:
        __init__(project_manager, log_user, change_repo, change_psql, table_viewer):
            Initializes the application, sets up the GUI, and configures various components.
        quit():
            Cleans up resources, stops threads, and exits the application.
    """

    def __init__(self, project_manager,
                 log_user,
                 change_repo,
                 change_psql,
                 table_viewer):
        # Initialize application attributes
        self.stats_schedule = None

        # Initialize the main application
        self.app = app_utils.get_app()  # Create the main QApplication instance
        # Initialize warning tooltips
        self.warning_tooltip = app_utils.init_warning_tooltip()
        app_utils.set_wizard_gui()  # Set up the GUI environment
        app_utils.init_psql_dns(self, change_psql)  # Initialize PostgreSQL DNS
        # Initialize the repository
        app_utils.init_repository(self, change_repo)
        app_utils.init_user(self, log_user)  # Initialize user settings
        app_utils.init_project(self, project_manager)  # Initialize the project
        app_utils.init_OCIO()  # Initialize OpenColorIO configuration
        self.stats_schedule = app_utils.init_stats()  # Initialize statistics scheduler

        # Main GUI application setup
        start_time = time.perf_counter()  # Start measuring application load time
        self.loading_widget = loading_widget.loading_widget()  # Create a loading widget
        self.loading_widget.show()  # Display the loading widget
        logger.info("Opening Wizard")  # Log the application start
        QtWidgets.QApplication.processEvents()  # Process pending GUI events

        # Perform version database modifications
        version_database_modification.main()

        # Initialize the table viewer if requested
        if table_viewer:
            self.table_viewer = table_viewer_widget.table_viewer_widget()

        # Set up the main application widget
        self.main_widget = main_widget.main_widget()
        self.main_widget.stop_threads.connect(
            self.stats_schedule.stop)  # Connect thread stopping
        self.main_widget.refresh()  # Refresh the main widget
        self.main_widget.init_floating_windows()  # Initialize floating windows
        QtWidgets.QApplication.processEvents()  # Process pending GUI events
        self.main_widget.init_contexts()  # Initialize application contexts
        self.loading_widget.close()  # Close the loading widget
        self.main_widget.whatsnew()  # Display "What's New" information
        # Check if the build is the latest
        self.main_widget.is_latest_build(force=0)
        logger.info(
            # Log the startup time
            f"Wizard start time : {str(round((time.perf_counter()-start_time), 1))}s")

    def quit(self):
        # Restore standard output and error streams
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Stop the statistics scheduler if it exists
        if self.stats_schedule:
            self.stats_schedule.stop()

        # Close all application windows and quit
        QtWidgets.QApplication.closeAllWindows()
        QtWidgets.QApplication.quit()
        sys.exit()  # Exit the application


def main(project_manager=False,
         log_user=False,
         change_repo=False,
         change_psql=False,
         table_viewer=False):
    """
    Entry point for the wizard application.
    This function initializes the application, sets up the exception hook,
    logs application information, and starts the main event loop.
    Args:
        project_manager (bool): If True, enables project manager functionality.
        log_user (bool): If True, enables user logging functionality.
        change_repo (bool): If True, enables repository change functionality.
        change_psql (bool): If True, enables PostgreSQL change functionality.
        table_viewer (bool): If True, enables table viewer functionality.
    Returns:
        None: The function does not return a value. It exits the program with
        the application's return code.
    """
    # Set the exception hook for the application
    sys.excepthook = app_utils.excepthook

    # Log application information
    application.log_app_infos()

    # Create and run the main application
    wizard_app = app(project_manager,
                     log_user,
                     change_repo,
                     change_psql,
                     table_viewer)
    ret = wizard_app.app.exec()  # Execute the application event loop
    sys.exit(ret)  # Exit with the return code


if __name__ == '__main__':
    main()  # Run the main function if this script is executed directly
