# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import user_widget
from wizard.gui import quotes_widget
from wizard.gui import user_log_widget
from wizard.gui import project_manager_widget
from wizard.gui import create_user_widget
from wizard.gui import create_project_widget

class header_widget(QtWidgets.QFrame):

    show_subtask_manager = pyqtSignal(object)
    show_console = pyqtSignal(object)
    show_user_preferences = pyqtSignal(object)
    close_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(header_widget, self).__init__(parent)
        self.user_widget = user_widget.user_widget()
        self.quotes_widget = quotes_widget.quotes_widget()
        self.build_ui()
        self.connect_functions()

    def refresh(self):
        self.user_widget.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.main_layout.addWidget(self.menu_bar)
        
        self.wizard_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='', icon=QtGui.QIcon(ressources._wizard_icon_small_))
        self.license_action = self.wizard_action.addAction("License")
        self.about_action = self.wizard_action.addAction("About")
        self.quit_action = self.wizard_action.addAction("Quit")

        self.window_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Window')
        self.console_action = self.window_action.addAction("Console")
        self.subtask_manager_action = self.window_action.addAction("Subtask manager")

        self.user_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='User')
        self.user_log_action = self.user_action.addAction("Change user")
        self.user_create_action = self.user_action.addAction("Create user")
        self.user_preferences_action = self.user_action.addAction("Preferences")

        self.project_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Project')
        self.project_log_action = self.project_action.addAction("Change project")
        self.project_create_action = self.project_action.addAction("Create project")

        self.help_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Help')
        self.documentation_action = self.help_action.addAction("Documentation")

        self.main_layout.addWidget(self.quotes_widget)
        self.main_layout.addWidget(self.user_widget)

    def connect_functions(self):
        self.quit_action.triggered.connect(self.close_signal.emit)
        self.subtask_manager_action.triggered.connect(self.show_subtask_manager.emit)
        self.console_action.triggered.connect(self.show_console.emit)
        self.user_log_action.triggered.connect(self.change_user)
        self.user_create_action.triggered.connect(self.create_user)
        self.user_preferences_action.triggered.connect(self.show_user_preferences.emit)
        self.project_log_action.triggered.connect(self.change_project)
        self.project_create_action.triggered.connect(self.create_project)

    def change_user(self):
        self.user_log_widget = user_log_widget.user_log_widget()
        self.user_log_widget.exec_()

    def change_project(self):
        self.project_manager_widget = project_manager_widget.project_manager_widget()
        self.project_manager_widget.exec_()

    def create_user(self):
        self.create_user_widget = create_user_widget.create_user_widget()
        self.create_user_widget.exec_()

    def create_project(self):
        self.create_project_widget = create_project_widget.create_project_widget()
        self.create_project_widget.exec_()

