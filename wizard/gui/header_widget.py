# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

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
    show_production_manager = pyqtSignal(object)
    show_quotes_manager = pyqtSignal(object)
    show_tables_viewer = pyqtSignal(object)
    show_groups_manager = pyqtSignal(object)
    show_batcher = pyqtSignal(object)
    show_console = pyqtSignal(object)
    show_user_preferences = pyqtSignal(object)
    show_project_preferences = pyqtSignal(object)
    show_championship = pyqtSignal(object)
    show_pywizard = pyqtSignal(object)
    show_license = pyqtSignal(object)
    show_splash_screen = pyqtSignal(object)
    show_latest_build = pyqtSignal(object)
    show_documentation = pyqtSignal(object)
    show_video_manager = pyqtSignal(object)
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
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        self.main_layout.addWidget(self.menu_bar)

        self.wizard_action = gui_utils.add_menu_to_menu_bar(
            self.menu_bar, title='', icon=QtGui.QIcon(ressources._wizard_icon_))
        self.license_action = self.wizard_action.addAction(
            QtGui.QIcon(ressources._license_icon_), "License")
        self.whatsnew_action = self.wizard_action.addAction(
            QtGui.QIcon(ressources._whatsnew_icon_), "Splash screen")
        self.latest_build_action = self.wizard_action.addAction(
            QtGui.QIcon(ressources._update_icon_), "Update")
        self.wizard_action.addSeparator()
        self.quit_action = self.wizard_action.addAction("Quit")

        self.window_action = gui_utils.add_menu_to_menu_bar(
            self.menu_bar, title='Window')
        self.production_manager_action = self.window_action.addAction(
            QtGui.QIcon(ressources._production_manager_icon_), "Production manager")
        self.video_manager_action = self.window_action.addAction(
            QtGui.QIcon(ressources._videos_manager_icon_), "Videos manager")
        self.groups_manager_action = self.window_action.addAction(
            QtGui.QIcon(ressources._group_icon_), "Groups manager")
        self.batcher_action = self.window_action.addAction(
            QtGui.QIcon(ressources._batcher_icon_), "Batcher")
        self.console_action = self.window_action.addAction(
            QtGui.QIcon(ressources._console_icon_), "Console")
        self.subtask_manager_action = self.window_action.addAction(
            QtGui.QIcon(ressources._tasks_icon_), "Subtask manager")
        self.championship_action = self.window_action.addAction(
            QtGui.QIcon(ressources._artefacts_icon_), "Championship")
        self.quotes_action = self.window_action.addAction(
            QtGui.QIcon(ressources._quote_icon_), "Quotes")
        self.table_viewer_action = self.window_action.addAction(
            QtGui.QIcon(ressources._table_viewer_icon_), "Tables editor")
        self.pywizard_action = self.window_action.addAction(
            QtGui.QIcon(ressources._python_icon_), "PyWizard")

        self.user_action = gui_utils.add_menu_to_menu_bar(
            self.menu_bar, title='User')
        self.user_log_action = self.user_action.addAction(
            QtGui.QIcon(ressources._user_icon_), "Change user")
        self.user_create_action = self.user_action.addAction(
            QtGui.QIcon(ressources._create_icon_), "Create user")
        self.user_action.addSeparator()
        self.user_preferences_action = self.user_action.addAction(
            QtGui.QIcon(ressources._settings_icon_), "Preferences")

        self.project_action = gui_utils.add_menu_to_menu_bar(
            self.menu_bar, title='Project')
        self.project_log_action = self.project_action.addAction(
            QtGui.QIcon(ressources._project_manager_), "Project manager")
        self.project_create_action = self.project_action.addAction(
            QtGui.QIcon(ressources._create_icon_), "Create project")
        self.project_action.addSeparator()
        self.project_preferences_action = self.project_action.addAction(
            QtGui.QIcon(ressources._settings_icon_), "Preferences")

        self.help_action = gui_utils.add_menu_to_menu_bar(
            self.menu_bar, title='Help')
        self.documentation_action = self.help_action.addAction(
            QtGui.QIcon(ressources._documentation_icon_), "Documentation")

        self.main_layout.addWidget(self.quotes_widget)
        self.main_layout.addWidget(self.user_widget)

    def connect_functions(self):
        self.license_action.triggered.connect(self.show_license.emit)
        self.whatsnew_action.triggered.connect(self.show_splash_screen.emit)
        self.latest_build_action.triggered.connect(self.show_latest_build.emit)
        self.quit_action.triggered.connect(self.close_signal.emit)
        self.subtask_manager_action.triggered.connect(
            self.show_subtask_manager.emit)
        self.console_action.triggered.connect(self.show_console.emit)
        self.championship_action.triggered.connect(self.show_championship.emit)
        self.quotes_action.triggered.connect(self.show_quotes_manager.emit)
        self.pywizard_action.triggered.connect(self.show_pywizard.emit)
        self.user_log_action.triggered.connect(self.change_user)
        self.user_create_action.triggered.connect(self.create_user)
        self.user_preferences_action.triggered.connect(
            self.show_user_preferences.emit)
        self.project_log_action.triggered.connect(self.change_project)
        self.project_create_action.triggered.connect(self.create_project)
        self.project_preferences_action.triggered.connect(
            self.show_project_preferences.emit)
        self.production_manager_action.triggered.connect(
            self.show_production_manager.emit)
        self.video_manager_action.triggered.connect(
            self.show_video_manager.emit)
        self.table_viewer_action.triggered.connect(
            self.show_tables_viewer.emit)
        self.groups_manager_action.triggered.connect(
            self.show_groups_manager.emit)
        self.batcher_action.triggered.connect(self.show_batcher.emit)
        self.documentation_action.triggered.connect(
            self.show_documentation.emit)

    def change_user(self):
        self.user_log_widget = user_log_widget.user_log_widget()
        self.user_log_widget.exec()

    def change_project(self):
        self.project_manager_widget = project_manager_widget.project_manager_widget(
            wait_for_restart=True)
        self.project_manager_widget.exec()

    def create_user(self):
        self.create_user_widget = create_user_widget.create_user_widget()
        self.create_user_widget.exec()

    def create_project(self):
        self.create_project_widget = create_project_widget.create_project_widget()
        self.create_project_widget.exec()
