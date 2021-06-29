# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.core import db_utils

# Wizard gui modules
from wizard.gui import message_widget
from wizard.gui import gui_utils

class create_db_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(create_db_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel('Database init')
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.infos_label = QtWidgets.QLabel('You need to init the database')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Administrator password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.email_lineEdit = QtWidgets.QLineEdit()
        self.email_lineEdit.setPlaceholderText('Administrator email')
        self.main_layout.addWidget(self.email_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.button_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.button_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton('Quit')
        self.buttons_layout.addWidget(self.quit_button)

        self.continue_button = QtWidgets.QPushButton('Continue')
        self.continue_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.continue_button)

    def connect_functions(self):
        self.continue_button.clicked.connect(self.apply)
        self.quit_button.clicked.connect(self.reject)

    def apply(self):
        admin_password = self.password_lineEdit.text()
        admin_email = self.email_lineEdit.text()
        site.create_site_database()
        db_utils.modify_db_name('site', 'site')
        site.init_site(admin_password, admin_email)
        self.accept()