# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.vars import ressources
from wizard.gui import gui_server

class create_playlist_widget(QtWidgets.QDialog):
    def __init__(self, data="{}", thumbnail_temp_path=None, parent=None):
        super(create_playlist_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create playlist")

        self.data = data
        self.thumbnail_temp_path = thumbnail_temp_path
        self.playlist_id = None
        self.playlist_name = None

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.accept_button.clicked.connect(self.create_playlist)
        self.cancel_button.clicked.connect(self.reject)

    def create_playlist(self):
        playlist_name = self.playlist_name_field.text()
        print(self.thumbnail_temp_path)
        playlist_id = assets.create_playlist(name=playlist_name, data=self.data, thumbnail_temp_path=self.thumbnail_temp_path)
        if playlist_id:
            self.playlist_id = playlist_id
            self.playlist_name = playlist_name
            gui_server.refresh_team_ui()
            self.accept()

    def build_ui(self):
        self.setMinimumWidth(350)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.playlist_name_field = QtWidgets.QLineEdit()
        self.playlist_name_field.setPlaceholderText("Playlist name")
        self.main_layout.addWidget(self.playlist_name_field)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding,
                                                    QtWidgets.QSizePolicy.Policy.MinimumExpanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.cancel_button)

        self.accept_button = QtWidgets.QPushButton('Add')
        self.accept_button.setObjectName('blue_button')
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.accept_button)
