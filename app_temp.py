#import PyWizard
from wizard.gui import tree_widget
from wizard.gui import user_widget
from wizard.gui import quotes_widget
from wizard.gui import psql_widget
from wizard.gui import create_db_widget
from wizard.gui import user_log_widget
from wizard.gui import project_log_widget
from wizard.gui import create_project_widget

import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from wizard.core import user
from wizard.core import environment
from wizard.core import site
from wizard.core import db_core
from wizard.core import db_utils

app = QtWidgets.QApplication(sys.argv)

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

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Black.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-BlackItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Bold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-BoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraBold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraBoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraLight.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ExtraLightItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Medium.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-MediumItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Regular.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-SemiBold.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-SemiBoldItalic.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-Thin.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Poppins-ThinItalic.ttf")

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Rubik-Italic-VariableFont_wght.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Rubik-VariableFont_wght.ttf")

QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Cabin-Italic-VariableFont_wdth,wght.ttf")
QtGui.QFontDatabase.addApplicationFont("ressources/fonts/Cabin-VariableFont_wdth,wght.ttf")

with open('wizard/gui/stylesheet.css', 'r') as f:
	app.setStyleSheet(f.read())
#my_tree_widget = tree_widget.tree_widget()
#my_user_widget = user_widget.user_widget()
#my_quotes_widget = quotes_widget.quotes_widget()
#my_tree_widget.show()
#my_user_widget.show()
#my_quotes_widget.show()
#my_psql_widget.show()
#my_create_db_widget.show()

if not user.user().get_psql_dns():
	my_psql_widget = psql_widget.psql_widget()
	if my_psql_widget.exec_() != QtWidgets.QDialog.Accepted:
		sys.exit()

db_server = db_core.db_server()
db_server.start()

if not site.is_site_database():
	my_create_db_widget = create_db_widget.create_db_widget()
	if my_create_db_widget.exec_() != QtWidgets.QDialog.Accepted:
		sys.exit()

db_utils.modify_db_name('site', 'site')
site.add_ip_user()

if not user.get_user():
	my_user_log_widget = user_log_widget.user_log_widget()
	if my_user_log_widget.exec_() != QtWidgets.QDialog.Accepted:
		sys.exit()

if not user.get_project():
	if not site.get_projects_names_list():
		my_create_project_widget = create_project_widget.create_project_widget()
		if my_create_project_widget.exec_() != QtWidgets.QDialog.Accepted:
			sys.exit()
	my_project_log_widget = project_log_widget.project_log_widget()
	if my_project_log_widget.exec_() != QtWidgets.QDialog.Accepted:
		sys.exit()

db_utils.modify_db_name('project', environment.get_project_name())

my_tree_widget = tree_widget.tree_widget()
my_user_widget = user_widget.user_widget()
my_quotes_widget = quotes_widget.quotes_widget()
my_tree_widget.show()
my_user_widget.show()
my_quotes_widget.show()

sys.exit(app.exec_())
