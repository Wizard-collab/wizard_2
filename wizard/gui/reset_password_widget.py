# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import repository
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class reset_password_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(reset_password_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Reset password")

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.spaceItem = QtWidgets.QSpacerItem(300,12,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.title_label = QtWidgets.QLabel("Reset user password")
        self.title_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(0,12,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.user_name_lineEdit = QtWidgets.QLineEdit()
        self.user_name_lineEdit.setPlaceholderText('User name')
        self.main_layout.addWidget(self.user_name_lineEdit)

        self.administrator_password_lineEdit = gui_utils.password_lineEdit()
        self.administrator_password_lineEdit.setPlaceholderText('Administrator password')
        self.main_layout.addWidget(self.administrator_password_lineEdit)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.confirm_password_lineEdit = gui_utils.password_lineEdit()
        self.confirm_password_lineEdit.setPlaceholderText('Confirm password')
        self.main_layout.addWidget(self.confirm_password_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(300,12,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.cancel_button)
        self.reset_password_button = QtWidgets.QPushButton('Reset password')
        self.reset_password_button.setObjectName('blue_button')
        self.reset_password_button.setDefault(True)
        self.reset_password_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.reset_password_button)

    def connect_functions(self):
        self.cancel_button.clicked.connect(self.reject)
        self.reset_password_button.clicked.connect(self.apply)

    def apply(self):
        user_name = self.user_name_lineEdit.text()
        administrator_password = self.administrator_password_lineEdit.text()
        new_passord = self.password_lineEdit.text()
        confirm_password = self.confirm_password_lineEdit.text()
        if new_passord == '':
            logger.warning("Please enter a password")
            return
        if new_passord != confirm_password:
            logger.warning("Passwords doesn't match")
            return
        if repository.reset_user_password(user_name,
                                            administrator_password,
                                            new_passord):
            self.accept()
