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
import os
import traceback
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import message_widget
from wizard.gui import psql_widget
from wizard.gui import repository_widget
from wizard.gui import team_dns_widget
from wizard.gui import user_log_widget
from wizard.gui import project_manager_widget
from wizard.gui import loading_widget
from wizard.gui import main_widget
from wizard.gui import warning_tooltip
from wizard.gui import logging_widget
import error_handler

# Wizard modules
from wizard.core import application
from wizard.core import user
from wizard.core import environment
from wizard.core import repository
from wizard.core import project
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import stats
from wizard.core import hooks
from wizard.core import custom_logger
custom_logger.get_root_logger()

logger = logging.getLogger('wizard')

class app():
    def __init__(self, project_manager):

        self.db_server = None

        self.app = gui_utils.get_app()
        QtCore.qInstallMessageHandler(customQtMsgHandler)

        self.warning_tooltip = warning_tooltip.warning_tooltip()
        self.custom_handler = logging_widget.custom_handler(long_formatter=False, parent=None)
        self.custom_handler.log_record.connect(self.warning_tooltip.invoke)
        logging.getLogger().addHandler(self.custom_handler)
        print('Wizard Gui')
        environment.set_gui(1)

        '''
        if gui_server.try_connection():
            gui_server.raise_ui()
            self.instance_running_info_widget = message_widget.message_widget("Multiple application instance",
                                                                "You're already running an instance of Wizard.")
            self.instance_running_info_widget.exec_()
            sys.exit()
        '''
        
        if not user.user().get_psql_dns():
            self.psql_widget = psql_widget.psql_widget()
            if self.psql_widget.exec_() != QtWidgets.QDialog.Accepted:
                self.quit()

        while not user.user().get_repository():
            self.repository_widget = repository_widget.repository_widget()
            if self.repository_widget.exec_() != QtWidgets.QDialog.Accepted:
                self.quit()

        self.db_server = db_core.db_server()
        self.db_server.start()

        user.user().get_team_dns()

        db_utils.modify_db_name('repository', environment.get_repository())
        repository.add_ip_user()

        if not user.get_user():
            self.user_log_widget = user_log_widget.user_log_widget()
            if self.user_log_widget.exec_() != QtWidgets.QDialog.Accepted:
                self.quit()

        if (not user.get_project()) or project_manager:
            self.project_manager_widget = project_manager_widget.project_manager_widget()
            if self.project_manager_widget.exec_() != QtWidgets.QDialog.Accepted:
                self.quit()

        db_utils.modify_db_name('project', environment.get_project_name())
        project.add_user(repository.get_user_row_by_name(environment.get_user(),
                                                            'id'))
        hooks.init_wizard_hooks()

        stats.add_progress_event()
        self.stats_schedule = stats.schedule()
        self.stats_schedule.start()

        start_time = time.time()
        
        self.loading_widget = loading_widget.loading_widget()
        self.loading_widget.show()
        QtWidgets.QApplication.processEvents()

        self.main_widget = main_widget.main_widget()
        self.main_widget.stop_threads.connect(self.db_server.stop)
        self.main_widget.stop_threads.connect(self.stats_schedule.stop)
        self.main_widget.refresh()
        self.main_widget.showMaximized()
        QtWidgets.QApplication.processEvents()
        self.main_widget.init_contexts()
        self.loading_widget.close()

        self.main_widget.whatsnew()
        logger.info(f"Wizard start time : {str(round((time.time()-start_time), 1))}s")

    def quit(self):
        if self.db_server:
            self.db_server.stop()
        self.stats_schedule.stop()
        QtWidgets.QApplication.closeAllWindows()
        QtWidgets.QApplication.quit()
        sys.exit()

def customQtMsgHandler(msg_type, msg_log_context, msg_string):
    if msg_string.startswith('QWindowsWindow::setGeometry:'):
        pass
    else:
        print(msg_string)

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    QtWidgets.QApplication.closeAllWindows()
    logger.critical(tb)
    command = f'error_handler.exe "{tb}"'
    if sys.argv[0].endswith('.py'):
        command = f'python error_handler.py "{tb}"'
    subprocess.Popen(command, start_new_session=True)

def main(project_manager=False):
    sys.excepthook = excepthook
    application.log_app_infos()
    wizard_app = app(project_manager)
    ret = wizard_app.app.exec_()

    sys.exit(ret)

if __name__ == '__main__':
    main()
