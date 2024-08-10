# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import repository
from wizard.core import db_utils
from wizard.core import environment
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import message_widget
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class create_repository_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(create_repository_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create repository")

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.spaceItem = QtWidgets.QSpacerItem(100,12,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.title_label = QtWidgets.QLabel("Create repository")
        self.title_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(0,12,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.repository_name_lineEdit = QtWidgets.QLineEdit()
        self.repository_name_lineEdit.setPlaceholderText('Repository name')
        self.main_layout.addWidget(self.repository_name_lineEdit)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Administrator password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.confirm_password_lineEdit = gui_utils.password_lineEdit()
        self.confirm_password_lineEdit.setPlaceholderText('Confirm password')
        self.main_layout.addWidget(self.confirm_password_lineEdit)

        self.email_lineEdit = QtWidgets.QLineEdit()
        self.email_lineEdit.setPlaceholderText('Administrator email')
        self.main_layout.addWidget(self.email_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100,12,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.button_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.button_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Policy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton('Quit')
        self.quit_button.setDefault(False)
        self.quit_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.quit_button)

        self.continue_button = QtWidgets.QPushButton('Continue')
        self.continue_button.setObjectName('blue_button')
        self.continue_button.setDefault(True)
        self.continue_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.continue_button)

    def connect_functions(self):
        self.continue_button.clicked.connect(self.apply)
        self.quit_button.clicked.connect(self.reject)

    def apply(self):
        repository_name = self.repository_name_lineEdit.text()
        admin_password = self.password_lineEdit.text()
        confirm_password = self.confirm_password_lineEdit.text()
        admin_email = self.email_lineEdit.text()

        if admin_password == confirm_password:
            environment.set_repository(repository_name)
            repository.create_repository_database()
            db_utils.modify_db_name('repository', environment.get_repository())
            repository.init_repository(admin_password, admin_email)
            self.accept()
        else:
            logger.warning("Administrator passwords doesn't matches")