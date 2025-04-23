# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtGui
import logging

# Wizard modules
from wizard.core import user
from wizard.core import environment
from wizard.vars import ressources

logger = logging.getLogger(__name__)


class team_dns_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(team_dns_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Team connection")

        self.build_ui()
        self.connect_functions()
        self.fill_ui()

    def fill_ui(self):
        team_dns = environment.get_team_dns()
        if team_dns is not None:
            self.host_lineEdit.setText(team_dns[0])
            self.port_lineEdit.setText(str(team_dns[1]))
            logger.warning("Can't reach server with this DNS")

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel(
            'Contact your IT to get those informations')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.spaceItem = QtWidgets.QSpacerItem(
            100, 25, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.host_lineEdit = QtWidgets.QLineEdit()
        self.host_lineEdit.setPlaceholderText('Host ( ex: 127.0.0.1 )')
        self.main_layout.addWidget(self.host_lineEdit)

        self.port_lineEdit = QtWidgets.QLineEdit()
        self.port_lineEdit.setPlaceholderText('Port ( ex: 11111 )')
        self.main_layout.addWidget(self.port_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(
            100, 25, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.button_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.button_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.button_widget)

        self.spaceItem = QtWidgets.QSpacerItem(
            100, 0, QtWidgets.QSizePolicy.Policy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton(
            'Continue without setting team DNS')
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
        team_host = self.host_lineEdit.text()
        team_port = self.port_lineEdit.text()
        try:
            team_port = int(team_port)
        except:
            team_port = None
            logger.info('The port needs to be an int')
        if team_port is not None:
            if user.user().set_team_dns(
                team_host,
                team_port
            ):
                self.accept()
