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

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys
import os
import traceback
import code
from PyQt5 import QtWidgets
import logging

# Append current dir to sys.path
sys.path.append(os.path.abspath(''))

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import gui_server

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
custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

class app():
    def __init__(self):
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
