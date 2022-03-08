# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import custom_tab_widget
from wizard.gui import softwares_preferences_widget

# Wizard modules
from wizard.vars import ressources
from wizard.core import application
from wizard.core import user
from wizard.core import site
from wizard.core import environment
from wizard.core import image

logger = logging.getLogger(__name__)

class project_preferences_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(project_preferences_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Project preferences")

        self.softwares_preferences_widget = softwares_preferences_widget.softwares_preferences_widget()

        self.build_ui()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.close()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def refresh(self):
        if self.isVisible():
            self.softwares_preferences_widget.refresh()

    def build_ui(self):
        self.resize(600,800)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.tabs_widget = custom_tab_widget.custom_tab_widget()
        self.main_layout.addWidget(self.tabs_widget)

        self.softwares_tab_index = self.tabs_widget.addTab(self.softwares_preferences_widget,
                                                            'Softwares',
                                                            QtGui.QIcon(ressources._plug_icon_))
