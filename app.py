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

# Python modules
import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import loading_widget
from wizard.gui import main_widget
import error_handler

# Wizard modules
from wizard.core import application
from wizard.core import custom_logger
import version_database_modification
custom_logger.get_root_logger()

logger = logging.getLogger('wizard')

class app():
    def __init__(self, project_manager,
                        log_user,
                        change_repo, 
                        change_psql):
        self.stats_schedule = None

        # Init
        self.app = app_utils.get_app()
        self.warning_tooltip = app_utils.init_warning_tooltip()
        app_utils.set_wizard_gui()
        app_utils.init_psql_dns(self, change_psql)
        app_utils.init_repository(self, change_repo)
        app_utils.init_user(self, log_user)
        app_utils.init_project(self, project_manager)
        self.stats_schedule = app_utils.init_stats()
        
        # Main gui app
        start_time = time.perf_counter()
        self.loading_widget = loading_widget.loading_widget()
        self.loading_widget.show()
        QtWidgets.QApplication.processEvents()

        version_database_modification.main()

        self.main_widget = main_widget.main_widget()
        self.main_widget.stop_threads.connect(self.stats_schedule.stop)
        self.main_widget.refresh()
        self.main_widget.init_floating_windows()
        QtWidgets.QApplication.processEvents()
        self.main_widget.init_contexts()
        self.loading_widget.close()
        self.main_widget.whatsnew()
        self.main_widget.is_latest_build(force=0)
        logger.info(f"Wizard start time : {str(round((time.perf_counter()-start_time), 1))}s")

    def quit(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.stats_schedule:
            self.stats_schedule.stop()
        QtWidgets.QApplication.closeAllWindows()
        QtWidgets.QApplication.quit()
        sys.exit()

def main(project_manager=False,
            log_user=False,
            change_repo=False,
            change_psql=False):
    sys.excepthook = app_utils.excepthook
    application.log_app_infos()
    wizard_app = app(project_manager,
                        log_user,
                        change_repo,
                        change_psql)
    ret = wizard_app.app.exec_()
    sys.exit(ret)

if __name__ == '__main__':
    main()
