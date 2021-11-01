# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import user
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import logging_widget
from wizard.gui import create_user_widget
from wizard.gui import gui_utils
from wizard.gui import gui_server

class user_log_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(user_log_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Log in")

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.user_name_lineEdit = QtWidgets.QLineEdit()
        self.user_name_lineEdit.setPlaceholderText('User name')
        self.main_layout.addWidget(self.user_name_lineEdit)

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

        self.info_label = QtWidgets.QLabel("Doesn't have an account?")
        self.sign_up_line_layout.addWidget(self.info_label)

        self.register_button = QtWidgets.QPushButton('Register')
        self.register_button.setObjectName('blue_text_button')
        self.sign_up_line_layout.addWidget(self.register_button)

        self.logging_widget = logging_widget.logging_widget(self)
        self.main_layout.addWidget(self.logging_widget)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_in_button.clicked.connect(self.apply)
        self.register_button.clicked.connect(self.create_user)

    def apply(self):
        user_name = self.user_name_lineEdit.text()
        password = self.password_lineEdit.text()
        if user.log_user(user_name, password):
            gui_server.restart_ui()
            self.accept()

    def create_user(self):
        self.create_user_widget = create_user_widget.create_user_widget(self)
        self.create_user_widget.exec_()
