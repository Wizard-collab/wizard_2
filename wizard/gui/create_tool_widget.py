# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import script_editor_widget
from wizard.gui import choose_icon_widget
from wizard.gui import gui_server
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import project
from wizard.core import shelf
from wizard.core import path_utils
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class create_tool_widget(QtWidgets.QWidget):
    def __init__(self, parent=None, script_id=None):
        super(create_tool_widget, self).__init__(parent)

        self.icon = ressources._python_icon_
        self.script_id = script_id
        self.script_row = None

        self.choose_icon_widget = choose_icon_widget.choose_icon_widget()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create tool")

        self.build_ui()
        self.connect_functions()
        self.refresh()

    def connect_functions(self):
        self.apply_button.clicked.connect(self.apply)
        self.cancel_button.clicked.connect(self.close)
        self.icon_button.clicked.connect(self.modify_icon)

    def refresh(self):
        if self.script_id is not None:
            self.apply_button.setText('Edit')
            self.script_row = project.get_shelf_script_data(self.script_id)
            self.icon = self.script_row['icon']
            self.name_field.setText(self.script_row['name'])
            self.name_field.setEnabled(False)
            self.help_textEdit.setText(self.script_row['help'])
            self.only_subtask_checkBox.setChecked(self.script_row['only_subprocess'])
            if path_utils.isfile(self.script_row['py_file']):
                with open(self.script_row['py_file']) as f:
                    script_data = f.read()
                self.script_editor_widget.setText(script_data)
            else:
                logger.error(f"{self.script_row['py_file']} not found")
        else:
            self.apply_button.setText('Create')
        self.icon_button.setIcon(QtGui.QIcon(self.icon))

    def apply(self):
        name = self.name_field.text()
        script = self.script_editor_widget.text()
        help = self.help_textEdit.toPlainText()
        only_subprocess = self.only_subtask_checkBox.isChecked()
        if self.script_id is None:
            if shelf.create_project_script(name, script, help, icon=self.icon, only_subprocess=only_subprocess):
                self.close()
                gui_server.refresh_ui()
        else:
            with open(self.script_row['py_file'], 'w') as f:
                f.write(script)
            if shelf.edit_project_script(self.script_id, help, icon=self.icon, only_subprocess=only_subprocess):
                self.close()
                gui_server.refresh_ui()

    def modify_icon(self):
        menu = gui_utils.QMenu()
        custom_icon_action = menu.addAction('Choose from disk')
        existing_icon_action = menu.addAction('Choose from wizard')
        action = menu.exec_(QtGui.QCursor().pos())
        if action == custom_icon_action:
            self.custom_icon()
        elif action == existing_icon_action:
            self.existing_icon()

    def custom_icon(self):
        options = QtWidgets.QFileDialog.Options()
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select tool icon", "",
                            "All Files (*);;Images Files (*.png);;Images Files (*.svg);;Images Files (*.jpg);;Images Files (*.jpeg)",
                            options=options)
        if image_file:
            self.icon = image_file
            self.icon_button.setIcon(QtGui.QIcon(self.icon))

    def existing_icon(self):
        if self.choose_icon_widget.exec_() == QtWidgets.QDialog.Accepted:
            self.icon = self.choose_icon_widget.icon_path
            self.icon_button.setIcon(QtGui.QIcon(self.icon))

    def build_ui(self):
        self.resize(QtCore.QSize(800, 600))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.header = QtWidgets.QWidget()
        self.header.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(3)
        self.header.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header)

        self.icon_button = QtWidgets.QPushButton()
        self.icon_button.setFixedSize(QtCore.QSize(26,26))
        self.header_layout.addWidget(self.icon_button)
        self.name_field = QtWidgets.QLineEdit()
        self.name_field.setPlaceholderText('Tool name')
        self.header_layout.addWidget(self.name_field)
        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.script_editor_widget = script_editor_widget.script_editor_widget()
        self.main_layout.addWidget(self.script_editor_widget)

        self.help_textEdit = QtWidgets.QTextEdit()
        self.help_textEdit.setMaximumHeight(200)
        self.help_textEdit.setPlaceholderText('Please enter a comment about your tool and how to use it.')
        self.main_layout.addWidget(self.help_textEdit)

        self.subtask_widget = QtWidgets.QWidget()
        self.subtask_layout = QtWidgets.QHBoxLayout()
        self.subtask_layout.setContentsMargins(0,0,0,0)
        self.subtask_layout.setSpacing(6)
        self.subtask_widget.setLayout(self.subtask_layout)
        self.main_layout.addWidget(self.subtask_widget)

        self.subtask_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.only_subtask_checkBox = QtWidgets.QCheckBox('Only execute as subtask')
        self.subtask_layout.addWidget(self.only_subtask_checkBox)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('transparent_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.cancel_button)
        self.apply_button = QtWidgets.QPushButton()
        self.apply_button.setObjectName('blue_button')
        self.apply_button.setDefault(True)
        self.apply_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.apply_button)
