# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources

class header_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(header_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(3,3,3,3)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.menu_bar = QtWidgets.QMenuBar()

        self.main_layout.addWidget(self.menu_bar)
        self.wizard_action = self.menu_bar.addMenu(QtGui.QIcon(ressources._wizard_icon_small_), '')

        self.license_action = self.wizard_action.addAction("License")
        self.about_action = self.wizard_action.addAction("About")
        self.quit_action = self.wizard_action.addAction("Quit")

        self.window_action = self.menu_bar.addMenu('Window')
        self.console_action = self.window_action.addAction("Console")

        self.window_action = self.menu_bar.addMenu('Help')
        self.documentation_action = self.window_action.addAction("Documentation")
