# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import user
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class psql_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(psql_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - PostgreSQL connection")

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel('Contact your IT to get those informations')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.host_lineEdit = QtWidgets.QLineEdit()
        self.host_lineEdit.setPlaceholderText('Host ( ex: 127.0.0.1 )')
        self.main_layout.addWidget(self.host_lineEdit)

        self.port_lineEdit = QtWidgets.QLineEdit()
        self.port_lineEdit.setPlaceholderText('Port ( default: 5432 )')
        self.main_layout.addWidget(self.port_lineEdit)

        self.user_lineEdit = QtWidgets.QLineEdit()
        self.user_lineEdit.setPlaceholderText('User')
        self.main_layout.addWidget(self.user_lineEdit)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

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
        self.quit_button.clicked.connect(self.close)

    def apply(self):
        psql_host = self.host_lineEdit.text()
        psql_port = self.port_lineEdit.text()
        psql_user = self.user_lineEdit.text()
        psql_password = self.password_lineEdit.text()
        if user.user().set_psql_dns(
                            psql_host,
                            psql_port,
                            psql_user,
                            psql_password
                            ):
            self.accept()
