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
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import message_widget
from wizard.gui import psql_widget
from wizard.gui import team_dns_widget
from wizard.gui import create_db_widget
from wizard.gui import user_log_widget
from wizard.gui import project_manager_widget
from wizard.gui import loading_widget
from wizard.gui import main_widget

# Wizard modules
from wizard.core import user
from wizard.core import environment
from wizard.core import site
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class app():
	def __init__(self):
		os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
		QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
		QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
		self.app = QtWidgets.QApplication(sys.argv)

		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Black.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BlackItalic.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Bold.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-BoldItalic.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Light.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-LightItalic.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Medium.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-MediumItalic.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Regular.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-Thin.ttf")
		QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Roboto-ThinItalic.ttf")
		with open('ressources/stylesheet.css', 'r') as f:
			self.app.setStyleSheet(f.read())

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
				sys.exit()

		self.db_server = db_core.db_server()
		self.db_server.start()

		if not user.user().get_team_dns():
			self.team_dns_widget = team_dns_widget.team_dns_widget()
			self.team_dns_widget.exec_()

		if not site.is_site_database():
			self.create_db_widget = create_db_widget.create_db_widget()
			if self.create_db_widget.exec_() != QtWidgets.QDialog.Accepted:
				sys.exit()

		db_utils.modify_db_name('site', 'site')
		site.add_ip_user()

		if not user.get_user():
			self.user_log_widget = user_log_widget.user_log_widget()
			if self.user_log_widget.exec_() != QtWidgets.QDialog.Accepted:
				sys.exit()

		if not user.get_project():
			self.project_manager_widget = project_manager_widget.project_manager_widget()
			if self.project_manager_widget.exec_() != QtWidgets.QDialog.Accepted:
				sys.exit()

		db_utils.modify_db_name('project', environment.get_project_name())
		

		self.loading_widget = loading_widget.loading_widget()
		self.loading_widget.show()
		QtWidgets.QApplication.processEvents()

		self.main_widget = main_widget.main_widget()
		self.main_widget.refresh()
		self.main_widget.showMaximized()
		QtWidgets.QApplication.processEvents()
		self.main_widget.init_contexts()
		self.main_widget.stop_threads.connect(self.db_server.stop)
		self.loading_widget.close()

		sys.exit(self.app.exec_())

if __name__ == '__main__':
	app()
