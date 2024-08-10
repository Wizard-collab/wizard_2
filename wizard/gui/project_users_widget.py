# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import logging
import json

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
        self.all_tag_groups = dict()
        self.build_ui()
        self.connect_functions()

        self.users_ids = dict()
        self.all_users_ids = dict()

    def refresh(self):
        self.refresh_users_list()
        self.refresh_tag_groups()

    def refresh_tag_groups(self):
        all_tag_groups = project.get_all_tag_groups()
        all_tag_ids = []
        for tag_group_row in all_tag_groups:
            all_tag_ids.append(tag_group_row['id'])
            if tag_group_row['id'] not in self.all_tag_groups:
                self.all_tag_groups[tag_group_row['id']] = dict()
                self.all_tag_groups[tag_group_row['id']]['widget'] = tag_group_widget(tag_group_row, self.all_users_ids)
                self.tag_groups_container.addWidget(self.all_tag_groups[tag_group_row['id']]['widget'])
            else:
                self.all_tag_groups[tag_group_row['id']]['widget'].tag_group_row = tag_group_row
                self.all_tag_groups[tag_group_row['id']]['widget'].refresh()
        
        ui_tag_groups = list(self.all_tag_groups.keys())
        for tag_group_id in ui_tag_groups:
            if tag_group_id not in all_tag_ids:
                self.remove_tag_group(tag_group_id)

    def remove_tag_group(self, tag_group_id):
        if tag_group_id in self.all_tag_groups.keys():
            self.all_tag_groups[tag_group_id]['widget'].setParent(None)
            self.all_tag_groups[tag_group_id]['widget'].deleteLater()
            del self.all_tag_groups[tag_group_id]

    def create_tag_group(self):
        self.tag_group_creation_widget = tag_group_creation_widget()
        if self.tag_group_creation_widget.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        tag_group_name = self.tag_group_creation_widget.name_field.text()
        project.create_tag_group(tag_group_name)
        gui_server.refresh_team_ui()

    def refresh_users_list(self):
        all_users = repository.get_users_list()
        users = dict()
        for user_row in all_users:
            self.all_users_ids[user_row['id']] = dict()
            self.all_users_ids[user_row['id']]['row'] = user_row
            self.all_users_ids[user_row['id']]['pixmap'] = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 30)

        project_user_ids = []
        for user_id in project.get_users_ids_list():
            project_user_ids.append(user_id)
            if user_id not in self.users_ids.keys():
                widget = user_widget(self.all_users_ids[user_id]['row'], self.all_users_ids[user_id]['pixmap'])
                widget.remove_user_signal.connect(self.remove_user_from_project)
                self.users_ids[user_id] = dict()
                self.users_ids[user_id]['row'] = self.all_users_ids[user_id]['row']
                self.users_ids[user_id]['pixmap'] = self.all_users_ids[user_id]['pixmap']
                self.users_ids[user_id]['widget'] = widget
                self.users_container.addWidget(widget)

        user_ids = list(self.users_ids.keys())
        for user_id in user_ids:
            if user_id not in project_user_ids:
                self.remove_user(user_id)

    def connect_functions(self):
        self.create_tag_group_button.clicked.connect(self.create_tag_group)

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

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.tag_groups_header_layout = QtWidgets.QHBoxLayout()
        self.tag_groups_header_layout.setContentsMargins(0,0,0,0)
        self.scrollArea_layout.addLayout(self.tag_groups_header_layout)

        self.tag_groups_title = QtWidgets.QLabel('Tag groups')
        self.tag_groups_title.setObjectName('bold_label')
        self.tag_groups_header_layout.addWidget(self.tag_groups_title)

        self.tag_groups_header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.create_tag_group_button = QtWidgets.QPushButton('Create tag group')
        self.create_tag_group_button.setStyleSheet('padding:2px;')
        self.tag_groups_header_layout.addWidget(self.create_tag_group_button)

        self.tags_info_label = QtWidgets.QLabel("Manage here the creation and subscription of tag groups.")
        self.tags_info_label.setWordWrap(True)
        self.tags_info_label.setObjectName('gray_label')
        self.scrollArea_layout.addWidget(self.tags_info_label)

        self.tag_groups_container = QtWidgets.QVBoxLayout()
        self.tag_groups_container.setContentsMargins(0,0,0,0)
        self.tag_groups_container.setSpacing(2)
        self.scrollArea_layout.addLayout(self.tag_groups_container)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

class tag_group_widget(QtWidgets.QFrame):
    def __init__(self, tag_group_row, users_ids, parent=None):
        super(tag_group_widget, self).__init__(parent)
        self.tag_group_row = tag_group_row
        self.users_ids = users_ids
        self.suscribed_users = dict()
        self.build_ui()
        self.refresh()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('dark_round_frame')
        self.group_tag_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.group_tag_layout)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(3)
        self.group_tag_layout.addLayout(self.header_layout)

        self.tag_group_image = QtWidgets.QLabel()
        self.tag_group_image.setFixedSize(23,23)
        self.tag_group_image.setPixmap(QtGui.QIcon(ressources._tag_icon_).pixmap(23))
        self.header_layout.addWidget(self.tag_group_image)

        self.tag_group_name = QtWidgets.QLabel()
        self.tag_group_name.setObjectName('tag_label')
        self.header_layout.addWidget(self.tag_group_name)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.suscribe_button = QtWidgets.QPushButton('')
        self.suscribe_button.setStyleSheet('padding:2px;')
        self.header_layout.addWidget(self.suscribe_button)

        self.delete_tag_group_button = QtWidgets.QPushButton()
        self.delete_tag_group_button.setFixedSize(QtCore.QSize(23,23))
        self.delete_tag_group_button.setIconSize(QtCore.QSize(15,15))
        self.delete_tag_group_button.setIcon(QtGui.QIcon(ressources._archive_icon_))
        self.header_layout.addWidget(self.delete_tag_group_button)

        self.group_tag_layout.addWidget(gui_utils.separator())

        self.users_layout = QtWidgets.QHBoxLayout()
        self.users_layout.setContentsMargins(0,0,0,0)
        self.users_layout.setSpacing(6)
        self.group_tag_layout.addLayout(self.users_layout)

        self.users_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def connect_functions(self):
        self.suscribe_button.clicked.connect(self.suscribe)
        self.delete_tag_group_button.clicked.connect(self.delete_tag_group)

    def suscribe(self):
        my_id = repository.get_user_row_by_name(environment.get_user(), 'id')
        users = json.loads(self.tag_group_row['user_ids'])
        if my_id in users:
            project.unsuscribe_from_tag_group(self.tag_group_row['name'])
        else:
            project.suscribe_to_tag_group(self.tag_group_row['name'])
        gui_server.refresh_team_ui()

    def refresh(self):
        self.tag_group_name.setText(f"@{self.tag_group_row['name']}")
        users = json.loads(self.tag_group_row['user_ids'])
        my_id = repository.get_user_row_by_name(environment.get_user(), 'id')
        if my_id in users:
            self.suscribe_button.setText("Unsuscribe")
        else:
            self.suscribe_button.setText("Suscribe")
        for user_id in users:
            if user_id not in self.suscribed_users:
                self.suscribed_users[user_id] = QtWidgets.QLabel()
                self.suscribed_users[user_id].setPixmap(self.users_ids[user_id]['pixmap'])
                self.users_layout.insertWidget(0, self.suscribed_users[user_id])
        ui_users = list(self.suscribed_users.keys())
        for user_id in ui_users:
            if user_id not in users:
                self.remove_user(user_id)

    def remove_user(self, user_id):
        if user_id in self.suscribed_users.keys():
            self.suscribed_users[user_id].setVisible(0)
            self.suscribed_users[user_id].setParent(None)
            self.suscribed_users[user_id].deleteLater()
            del self.suscribed_users[user_id]

    def delete_tag_group(self):
        project.delete_tag_group(self.tag_group_row['name'])
        gui_server.refresh_team_ui()

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

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.ignore_user_button = QtWidgets.QPushButton('Remove user')
        self.ignore_user_button.setStyleSheet('padding:2px;')
        self.header_layout.addWidget(self.ignore_user_button)

class tag_group_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(tag_group_creation_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.name_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#variant_creation_widget{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_layout.addWidget(QtWidgets.QLabel('New tag group'))
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Policy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.close_pushButton.clicked.connect(self.reject)