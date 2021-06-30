# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.core import user

# Wizard gui modules
from wizard.gui import logging_widget
from wizard.gui import create_project_widget
from wizard.gui import gui_utils

class project_log_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(project_log_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.fill_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel("Connect to a project")
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.projects_comboBox = QtWidgets.QComboBox()
        self.projects_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.projects_comboBox)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.buttons_layout.addWidget(self.quit_button)
        self.sign_in_button = QtWidgets.QPushButton('Sign in')
        self.sign_in_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.sign_in_button)

        self.sign_up_line_widget = QtWidgets.QWidget()
        self.sign_up_line_layout = QtWidgets.QHBoxLayout()
        self.sign_up_line_layout.setContentsMargins(4,4,4,4)
        self.sign_up_line_layout.setSpacing(4)
        self.sign_up_line_widget.setLayout(self.sign_up_line_layout)
        self.main_layout.addWidget(self.sign_up_line_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        self.sign_up_line_layout.addSpacerItem(self.spaceItem)

        self.info_label = QtWidgets.QLabel("Or create a project :")
        self.sign_up_line_layout.addWidget(self.info_label)

        self.create_project_button = QtWidgets.QPushButton('New project')
        self.create_project_button.setObjectName('blue_text_button')
        self.sign_up_line_layout.addWidget(self.create_project_button)

        self.logging_widget = logging_widget.logging_widget(self)
        self.main_layout.addWidget(self.logging_widget)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_in_button.clicked.connect(self.apply)
        self.create_project_button.clicked.connect(self.create_project)

    def fill_ui(self):
        self.projects_comboBox.clear()
        for project_name in site.get_projects_names_list():
            self.projects_comboBox.addItem(project_name)

    def create_project(self):
        self.create_project_widget = create_project_widget.create_project_widget(self)
        self.create_project_widget.exec_()
        self.fill_ui()

    def apply(self):
        project_name = self.projects_comboBox.currentText()
        project_password = self.password_lineEdit.text()
        if user.log_project(project_name, project_password):
            self.accept()
