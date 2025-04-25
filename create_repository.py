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
This module provides the implementation of a PyQt6-based application for creating a repository.
It includes the main application class, custom exception handling, and a custom Qt message handler.
The application is designed to initialize the GUI, configure logging, and handle repository creation
through a dialog widget.

Modules:
- Python standard modules: sys, time, os, traceback, subprocess, logging
- PyQt6 modules: QtWidgets, QtCore, QtGui
- Wizard core modules: application, user, environment, repository, db_core, db_utils, custom_logger
- Wizard GUI modules: app_utils, gui_server, message_widget, create_repository_widget, warning_tooltip, logging_widget
- Error handling module: error_handler

Classes:
- app: Represents the main application logic for creating a repository.

Functions:
- customQtMsgHandler: Custom message handler for Qt logging.
- excepthook: Custom exception hook to handle uncaught exceptions in the application.
- main: Entry point for the application.

Usage:
Run this script as the main module to launch the repository creation application.
"""

# Python modules
import sys
import time
import os
import traceback
import subprocess
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import application
from wizard.core import user
from wizard.core import environment
from wizard.core import repository
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import custom_logger

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import gui_server
from wizard.gui import message_widget
from wizard.gui import create_repository_widget
from wizard.gui import warning_tooltip
from wizard.gui import logging_widget
import error_handler

custom_logger.get_root_logger()
logger = logging.getLogger('wizard')


class app():
    """
    A class representing the main application logic for creating a repository.
    This class initializes the application, sets up logging, configures the GUI,
    and handles the creation of a repository through a dialog widget.
    Attributes:
        app (object): The main application instance.
        warning_tooltip (warning_tooltip.warning_tooltip): A tooltip for displaying warnings.
        custom_handler (logging_widget.custom_handler): A custom logging handler for managing log records.
        create_repository_widget (create_repository_widget.create_repository_widget): 
            A widget for creating a repository.
    Methods:
        __init__():
            Initializes the application, sets up logging, configures the GUI, and
            launches the repository creation dialog.
        quit():
            Closes all application windows and exits the application.
    """

    def __init__(self):
        """
        Initializes the main application class.
        This constructor sets up the application environment, installs a custom
        message handler for Qt, initializes logging with a custom handler, and
        configures the GUI and database connection. It also creates and displays
        the repository creation widget, and exits the application if the dialog
        is accepted.
        Attributes:
            app: The main application instance retrieved using `app_utils.get_app()`.
            warning_tooltip: An instance of the warning tooltip for displaying warnings.
            custom_handler: A custom logging handler for capturing log records.
            create_repository_widget: The widget for creating a repository.
        """
        self.app = app_utils.get_app()
        QtCore.qInstallMessageHandler(customQtMsgHandler)

        self.warning_tooltip = warning_tooltip.warning_tooltip()
        self.custom_handler = logging_widget.custom_handler(
            long_formatter=False, parent=None)
        self.custom_handler.log_record.connect(self.warning_tooltip.invoke)
        logging.getLogger().addHandler(self.custom_handler)

        app_utils.set_wizard_gui()
        app_utils.init_psql_dns(self)

        self.create_repository_widget = create_repository_widget.create_repository_widget()
        if self.create_repository_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.quit()

    def quit(self):
        """
        Closes all open windows and terminates the application.

        This method performs the following actions:
        1. Closes all open windows in the application using `QtWidgets.QApplication.closeAllWindows()`.
        2. Quits the Qt application event loop using `QtWidgets.QApplication.quit()`.
        3. Exits the Python interpreter with `sys.exit()`.

        Note:
            This function will terminate the entire application and should be used with caution.
        """
        QtWidgets.QApplication.closeAllWindows()
        QtWidgets.QApplication.quit()
        sys.exit()


def customQtMsgHandler(msg_type, msg_log_context, msg_string):
    """
    Custom message handler for Qt logging.

    This function filters out specific Qt warning messages related to 
    'QWindowsWindow::setGeometry' and prints all other messages.

    Args:
        msg_type: The type of the message (e.g., QtDebugMsg, QtWarningMsg, etc.).
        msg_log_context: The context of the message, including file, line, and function.
        msg_string: The actual message string to be processed.

    Returns:
        None
    """
    if msg_string.startswith('QWindowsWindow::setGeometry:'):
        pass
    else:
        print(msg_string)


def excepthook(exc_type, exc_value, exc_tb):
    """
    Custom exception hook to handle uncaught exceptions in the application.

    This function formats the traceback of an uncaught exception, logs it 
    as a critical error, closes all open Qt application windows, and 
    launches an external error handler to process the error.

    Args:
        exc_type (type): The class of the exception that was raised.
        exc_value (Exception): The instance of the exception that was raised.
        exc_tb (traceback): A traceback object representing the call stack 
            at the point where the exception occurred.

    Behavior:
        - Formats the exception traceback into a string.
        - Closes all open Qt application windows using `QtWidgets.QApplication.closeAllWindows()`.
        - Logs the formatted traceback as a critical error using the `logger`.
        - Determines the appropriate command to invoke the error handler:
            - If the script is a `.py` file, it runs `error_handler.py` using Python.
            - Otherwise, it runs `error_handler.exe`.
        - Launches the error handler in a new process session using `subprocess.Popen`.

    Note:
        Ensure that `traceback`, `QtWidgets`, `logger`, `sys`, and `subprocess` 
        are properly imported and initialized in the script where this function is used.
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    QtWidgets.QApplication.closeAllWindows()
    logger.critical(tb)
    command = f'error_handler.exe "{tb}"'
    if sys.argv[0].endswith('.py'):
        command = f'python error_handler.py "{tb}"'
    subprocess.Popen(command, start_new_session=True)


def main():
    """
    Entry point for the application.
    This function sets up the global exception hook, logs application information,
    initializes the wizard application, and starts the application's event loop.
    Upon completion, it exits the program with the return code from the event loop.
    Steps:
    1. Sets a custom exception hook for handling uncaught exceptions.
    2. Logs application-specific information for debugging or tracking purposes.
    3. Initializes the wizard application instance.
    4. Executes the application's main event loop.
    5. Exits the program with the return code from the event loop.
    Note:
    - Ensure that `excepthook`, `application.log_app_infos`, and `app()` are properly defined
      and imported before calling this function.
    - This function terminates the program using `sys.exit()`.
    Returns:
        None
    """
    sys.excepthook = excepthook
    application.log_app_infos()
    wizard_app = app()
    ret = wizard_app.app.exec()

    sys.exit(ret)


if __name__ == '__main__':
    main()
