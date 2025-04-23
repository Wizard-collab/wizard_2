# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtGui
import json
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.vars import softwares_vars
from wizard.core import project
from wizard.core import path_utils

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import script_editor_widget

logger = logging.getLogger(__name__)


class project_hooks_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(project_hooks_widget, self).__init__(parent)

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.softwares_comboBox.currentTextChanged.connect(self.refresh)
        self.apply_button.clicked.connect(self.apply)

    def fill_softwares(self):
        self.softwares_comboBox.clear()
        for software in softwares_vars._softwares_list_:
            icon = ressources._softwares_icons_dic_[software]
            self.softwares_comboBox.addItem(QtGui.QIcon(icon), software)
        self.softwares_comboBox.addItem(
            QtGui.QIcon(ressources._wizard_icon_), 'wizard')

    def showEvent(self, event):
        self.fill_softwares()

    def refresh(self):
        software = self.softwares_comboBox.currentText()
        if software != '':
            hook_file = path_utils.join(
                project.get_hooks_folder(), softwares_vars._hooks_files_[software])
            if not path_utils.isfile(hook_file):
                hook_file = path_utils.join(
                    'ressources/hooks', softwares_vars._hooks_files_[software])
            with open(hook_file, 'r') as f:
                self.script_editor_widget.setText(f.read())

    def build_ui(self):
        self.container_layout = QtWidgets.QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(12)
        self.main_widget.setLayout(self.main_layout)
        self.container_layout.addWidget(self.main_widget)

        self.title = QtWidgets.QLabel('Hooks')
        self.title.setObjectName('title_label')
        self.main_layout.addWidget(self.title)

        self.main_layout.addWidget(gui_utils.separator())

        self.softwares_comboBox = gui_utils.QComboBox()
        self.softwares_comboBox.setFixedWidth(200)
        self.main_layout.addWidget(self.softwares_comboBox)

        self.script_editor_widget = script_editor_widget.script_editor_widget()
        self.main_layout.addWidget(self.script_editor_widget)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.apply_button.setObjectName('blue_button')
        self.apply_button.setDefault(True)
        self.apply_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.apply_button)

    def apply(self):
        software = self.softwares_comboBox.currentText()
        hook_file = path_utils.join(
            project.get_hooks_folder(), softwares_vars._hooks_files_[software])
        with open(hook_file, 'w') as f:
            f.write(self.script_editor_widget.text())
        logger.info(f"{hook_file} modified")
