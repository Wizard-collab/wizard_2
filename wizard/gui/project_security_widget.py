# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import logging

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.vars import ressources
from wizard.core import repository
from wizard.core import environment

logger = logging.getLogger(__name__)

class project_security_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(project_security_widget, self).__init__(parent)
        self.ignore_admin_toggle = 0
        self.build_ui()
        self.refresh()
        self.connect_functions()

    def refresh(self):
        pass

    def clear_pwds(self):
        self.old_pwd_lineEdit.clear()
        self.new_pwd_lineEdit.clear()
        self.confirm_pwd_lineEdit.clear()
        self.admin_pwd_lineEdit.clear()

    def connect_functions(self):
        self.pwd_accept_button.clicked.connect(self.change_password)

    def change_password(self):
        old_password = self.old_pwd_lineEdit.text()
        new_password = self.new_pwd_lineEdit.text()
        confirm_password = self.confirm_pwd_lineEdit.text()
        admin_password = self.admin_pwd_lineEdit.text()
        process = 1
        if old_password == '':
            logger.warning("Please enter the actual project password")
            process = 0
        if new_password != confirm_password:
            logger.warning("The new passwords doesn't matches")
            process = 0
        if new_password == '' or confirm_password == '':
            logger.warning("Please enter a new password")
            process = 0
        if admin_password == '':
            logger.warning("Please enter the administrator password")
            process = 0
        if process:
            if repository.modify_project_password(environment.get_project_name(), old_password, new_password, admin_password):
                self.clear_pwds()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_widget.setObjectName('transparent_widget')
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setSpacing(12)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)

        self.main_layout.addWidget(self.scrollArea)

        self.title = QtWidgets.QLabel('Security')
        self.title.setObjectName('title_label')
        self.scrollArea_layout.addWidget(self.title)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.pwd_frame = QtWidgets.QFrame()
        self.pwd_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.pwd_layout = QtWidgets.QVBoxLayout()
        self.pwd_layout.setContentsMargins(0,0,0,0)
        self.pwd_layout.setSpacing(6)
        self.pwd_frame.setLayout(self.pwd_layout)
        self.scrollArea_layout.addWidget(self.pwd_frame)

        self.pwd_title = QtWidgets.QLabel('Change password')
        self.pwd_title.setObjectName('bold_label')
        self.pwd_layout.addWidget(self.pwd_title)

        self.old_pwd_lineEdit = gui_utils.password_lineEdit()
        self.old_pwd_lineEdit.setPlaceholderText('Old password')
        self.pwd_layout.addWidget(self.old_pwd_lineEdit)

        self.new_pwd_lineEdit = gui_utils.password_lineEdit()
        self.new_pwd_lineEdit.setPlaceholderText('New password')
        self.pwd_layout.addWidget(self.new_pwd_lineEdit)

        self.confirm_pwd_lineEdit = gui_utils.password_lineEdit()
        self.confirm_pwd_lineEdit.setPlaceholderText('Confirm password')
        self.pwd_layout.addWidget(self.confirm_pwd_lineEdit)

        self.admin_pwd_lineEdit = gui_utils.password_lineEdit()
        self.admin_pwd_lineEdit.setPlaceholderText('Enter the administrator password')
        self.pwd_layout.addWidget(self.admin_pwd_lineEdit)

        self.pwd_buttons_widget = QtWidgets.QWidget()
        self.pwd_buttons_layout = QtWidgets.QHBoxLayout()
        self.pwd_buttons_layout.setContentsMargins(0,0,0,0)
        self.pwd_buttons_layout.setSpacing(6)
        self.pwd_buttons_widget.setLayout(self.pwd_buttons_layout)
        self.pwd_layout.addWidget(self.pwd_buttons_widget)

        self.pwd_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.pwd_accept_button = QtWidgets.QPushButton('Apply')
        self.pwd_accept_button.setObjectName('blue_button')
        self.pwd_buttons_layout.addWidget(self.pwd_accept_button)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
