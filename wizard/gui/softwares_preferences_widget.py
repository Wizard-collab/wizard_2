# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import json
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.vars import softwares_vars
from wizard.core import project
from wizard.core import softwares_search

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class softwares_preferences_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(softwares_preferences_widget, self).__init__(parent)

        self.build_ui()
        self.fill_softwares()
        self.connect_functions()
        self.refresh()

    def connect_functions(self):
        self.softwares_comboBox.currentTextChanged.connect(self.refresh)
        self.apply_button.clicked.connect(self.apply)
        self.guess_button.clicked.connect(self.guess_path)
        self.open_folder_button.clicked.connect(self.open_folder)

    def build_ui(self):
        self.container_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.container_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(12)
        self.main_widget.setLayout(self.main_layout)
        self.container_layout.addWidget(self.main_widget)

        self.title = QtWidgets.QLabel('Softwares')
        self.title.setObjectName('title_label')
        self.main_layout.addWidget(self.title)

        self.main_layout.addWidget(gui_utils.separator())

        self.softwares_comboBox = gui_utils.QComboBox()
        self.softwares_comboBox.setFixedWidth(200)
        self.main_layout.addWidget(self.softwares_comboBox)

        self.path_widget = QtWidgets.QWidget()
        self.path_layout = QtWidgets.QHBoxLayout()
        self.path_layout.setContentsMargins(0,0,0,0)
        self.path_layout.setSpacing(6)
        self.path_widget.setLayout(self.path_layout)
        self.main_layout.addWidget(self.path_widget)

        self.path_lineEdit = QtWidgets.QLineEdit()
        self.path_lineEdit.setPlaceholderText('Software executable path')
        self.path_layout.addWidget(self.path_lineEdit)

        self.open_folder_button = QtWidgets.QPushButton()
        self.open_folder_button.setFixedSize(24, 24)
        self.open_folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.path_layout.addWidget(self.open_folder_button)

        self.guess_button = QtWidgets.QPushButton()
        self.guess_button.setIcon(QtGui.QIcon(ressources._guess_icon_))
        self.guess_button.setFixedSize(24, 24)
        self.path_layout.addWidget(self.guess_button)

        self.custom_script_paths_textEdit = QtWidgets.QTextEdit()
        self.custom_script_paths_textEdit.setPlaceholderText('path/to/my/scripts')
        self.main_layout.addWidget(self.custom_script_paths_textEdit)

        self.custom_env_textEdit = QtWidgets.QTextEdit()
        self.custom_env_textEdit.setPlaceholderText('PYTHONPATH=path/to/my/scripts')
        self.main_layout.addWidget(self.custom_env_textEdit)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.apply_button.setObjectName('blue_button')
        self.apply_button.setDefault(True)
        self.apply_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.apply_button)

    def open_folder(self):
        options = QtWidgets.QFileDialog.Options()
        software_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select software executable", "",
                            "All Files (*);;",
                            options=options)
        if software_path:
            self.path_lineEdit.setText(software_path.replace('\\', '/'))

    def guess_path(self):
        software = self.softwares_comboBox.currentText()
        versions_dic = softwares_search.get_software_executables(software)
        if versions_dic:
            menu = gui_utils.QMenu(self)
            for version in versions_dic.keys():
                action = menu.addAction(version)
                action.name = version
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.path_lineEdit.setText(versions_dic[action.name])

    def fill_softwares(self):
        for software in softwares_vars._softwares_list_:
            icon = ressources._sofwares_icons_dic_[software]
            self.softwares_comboBox.addItem(QtGui.QIcon(icon), software)

    def refresh(self):
        software = self.softwares_comboBox.currentText()
        software_row = project.get_software_data_by_name(software)
        self.path_lineEdit.setText(software_row['path'])
        self.custom_script_paths_textEdit.setText(software_row['additionnal_scripts'])
        self.custom_env_textEdit.setText(self.load_additionnal_env(software_row['additionnal_env']))

    def apply(self):
        software = self.softwares_comboBox.currentText()
        software_row = project.get_software_data_by_name(software)
        path = self.path_lineEdit.text()
        if path != software_row['path']:
            project.set_software_path(software_row['id'], path)
        additionnal_scripts = self.custom_script_paths_textEdit.toPlainText()
        if additionnal_scripts != software_row['additionnal_scripts']:
            project.set_software_additionnal_scripts(software_row['id'], additionnal_scripts)
        additionnal_env = self.custom_env_textEdit.toPlainText()
        if additionnal_env != software_row['additionnal_env']:
            project.set_software_additionnal_env(software_row['id'], self.convert_additionnal_env(additionnal_env))

    def convert_additionnal_env(self, additionnal_env):
        env_dic = dict()
        lines = additionnal_env.split('\n')
        for line in lines:
            if '=' in line:
                key = line.split('=')[0]
                data = line.split('=')[-1]
                env_dic[key] = data
        return env_dic

    def load_additionnal_env(self, additionnal_env):
        text = ""
        if additionnal_env is not None and additionnal_env != '':
	        dic = json.loads(additionnal_env)
	        for key in dic.keys():
	            text += f"{key}={dic[key]}\n"
        return text
