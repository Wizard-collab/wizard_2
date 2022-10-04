# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard modules
from wizard.core import image
from wizard.core import tools
from wizard.core import repository
from wizard.core import project
from wizard.core import environment
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class project_users_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(project_users_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

        self.users_ids = dict()

    def refresh(self):
        self.refresh_users_list()

    def refresh_users_list(self):
        all_users = repository.get_users_list()
        users = dict()
        for user_row in all_users:
            users[user_row['id']] = dict()
            users[user_row['id']]['row'] = user_row
            users[user_row['id']]['pixmap'] = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 30)

        project_user_ids = []
        for user_id in project.get_users_ids_list():
            project_user_ids.append(user_id)
            if user_id not in self.users_ids.keys():
                widget = user_widget(users[user_id]['row'], users[user_id]['pixmap'])
                widget.remove_user_signal.connect(self.remove_user_from_project)
                self.users_ids[user_id] = dict()
                self.users_ids[user_id]['row'] = users[user_id]['row']
                self.users_ids[user_id]['pixmap'] = users[user_id]['pixmap']
                self.users_ids[user_id]['widget'] = widget
                self.users_container.addWidget(widget)

        user_ids = list(self.users_ids.keys())
        for user_id in user_ids:
            if user_id not in project_user_ids:
                self.remove_user(user_id)

    def connect_functions(self):
        pass

    def remove_user_from_project(self, user_id):
        project.remove_user(user_id)
        gui_server.refresh_team_ui()

    def remove_user(self, user_id):
        if user_id in self.users_ids.keys():
            self.users_ids[user_id]['widget'].setParent(None)
            self.users_ids[user_id]['widget'].deleteLater()
            del self.users_ids[user_id]

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setContentsMargins(24,24,24,24)
        self.scrollArea_layout.setSpacing(12)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)

        self.main_layout.addWidget(self.scrollArea)

        self.title = QtWidgets.QLabel('Users')
        self.title.setObjectName('title_label')
        self.scrollArea_layout.addWidget(self.title)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.list_title = QtWidgets.QLabel('Users list')
        self.list_title.setObjectName('bold_label')
        self.scrollArea_layout.addWidget(self.list_title)

        self.info_label = QtWidgets.QLabel("This list shows all the users who have logged in the project.")
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('gray_label')
        self.scrollArea_layout.addWidget(self.info_label)

        self.users_container = QtWidgets.QVBoxLayout()
        self.users_container.setContentsMargins(0,0,0,0)
        self.users_container.setSpacing(2)
        self.scrollArea_layout.addLayout(self.users_container)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

class user_widget(QtWidgets.QFrame):

    remove_user_signal = pyqtSignal(int)

    def __init__(self, user_row, pixmap, parent=None):
        super(user_widget, self).__init__(parent)
        self.user_row = user_row
        self.user_pixmap = pixmap
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def fill_ui(self):
        self.user_section_image.setPixmap(self.user_pixmap)
        self.user_section_name.setText(self.user_row['user_name'])

    def connect_functions(self):
        self.ignore_user_button.clicked.connect(lambda:self.remove_user_signal.emit(self.user_row['id']))

    def build_ui(self):
        self.setObjectName('dark_round_frame')
        self.user_section_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.user_section_layout)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.user_section_layout.addLayout(self.header_layout)

        self.user_section_image = QtWidgets.QLabel()
        self.header_layout.addWidget(self.user_section_image)

        self.user_section_name = QtWidgets.QLabel()
        self.header_layout.addWidget(self.user_section_name)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.ignore_user_button = QtWidgets.QPushButton('Remove user')
        self.ignore_user_button.setStyleSheet('padding:2px;')
        self.header_layout.addWidget(self.ignore_user_button)

