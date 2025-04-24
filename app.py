# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

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
