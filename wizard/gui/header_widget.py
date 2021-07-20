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

class header_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(header_widget, self).__init__(parent)
        self.user_widget = user_widget.user_widget()
        self.quotes_widget = quotes_widget.quotes_widget()
        self.build_ui()

    def refresh(self):
        self.user_widget.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(2,2,8,2)
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

        self.window_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Help')
        self.documentation_action = self.window_action.addAction("Documentation")

        self.main_layout.addWidget(self.quotes_widget)
        self.main_layout.addWidget(self.user_widget)

