# Python modules
import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import psql_widget
from wizard.gui import team_dns_widget
from wizard.gui import create_db_widget
from wizard.gui import user_log_widget
from wizard.gui import project_log_widget
from wizard.gui import create_project_widget
from wizard.gui import loading_widget
from wizard.gui import main_widget

from wizard.gui import user_preferences_widget

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
			if not site.get_projects_names_list():
				self.create_project_widget = create_project_widget.create_project_widget()
				if self.create_project_widget.exec_() != QtWidgets.QDialog.Accepted:
					sys.exit()
			self.project_log_widget = project_log_widget.project_log_widget()
			if self.project_log_widget.exec_() != QtWidgets.QDialog.Accepted:
				sys.exit()

		db_utils.modify_db_name('project', environment.get_project_name())

		self.loading_widget = loading_widget.loading_widget()
		self.loading_widget.show()
		QtWidgets.QApplication.processEvents()

		self.main_widget = main_widget.main_widget()
		self.main_widget.refresh()
		self.main_widget.show()
		self.main_widget.toggle_size()
		QtWidgets.QApplication.processEvents()
		self.main_widget.init_contexts()
		self.main_widget.stop_threads.connect(self.db_server.stop)
		self.loading_widget.close()

		self.user_account_widget = user_preferences_widget.user_account_widget()
		self.user_account_widget.show()

		sys.exit(self.app.exec_())

if __name__ == '__main__':
	app()
