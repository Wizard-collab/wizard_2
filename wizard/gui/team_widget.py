# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal

# Wizard modules
from wizard.core import site
from wizard.core import image
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import custom_window

class team_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(team_widget, self).__init__(parent)
        self.user_ids = dict()

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.build_ui()

    def leaveEvent(self, event):
        self.hide()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.info_widget = gui_utils.info_widget(transparent=1)
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.users_scrollArea = QtWidgets.QScrollArea()
        self.users_scrollBar = self.users_scrollArea.verticalScrollBar()

        self.users_scrollArea_widget = QtWidgets.QWidget()
        self.users_scrollArea_widget.setObjectName('transparent_widget')
        self.users_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.users_scrollArea_layout.setContentsMargins(3,3,3,3)
        self.users_scrollArea_layout.setSpacing(3)
        self.users_scrollArea_widget.setLayout(self.users_scrollArea_layout)

        #self.users_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.users_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.users_scrollArea.setWidgetResizable(True)
        self.users_scrollArea.setWidget(self.users_scrollArea_widget)

        self.users_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.users_scrollArea)

    def add_user(self, user_name):
        if user_name not in self.user_ids.keys():
            widget = user_widget(user_name)
            self.users_scrollArea_layout.addWidget(widget)
            self.user_ids[user_name] = widget
            self.refresh()

    def remove_user(self, user_name):
        if user_name in self.user_ids.keys():
            widget = self.user_ids[user_name]
            widget.setVisible(0)
            widget.setParent(None)
            widget.deleteLater()
            del self.user_ids[user_name]
            self.refresh()

    def set_team_connection(self, connection_status):
        self.connection_status = connection_status
        if not connection_status:
            self.remove_all_users()
        self.refresh()

    def refresh(self):
        if self.connection_status:
            if len(self.user_ids) == 0:
                self.users_scrollArea.setVisible(0)
                self.info_widget.setVisible(1)
                self.info_widget.setText("You're alone\nYou're on your own...")
                self.info_widget.setImage(ressources._alone_info_)
            else:
                self.info_widget.setVisible(0)
                self.users_scrollArea.setVisible(1)
        else:
            self.users_scrollArea.setVisible(0)
            self.info_widget.setVisible(1)
            self.info_widget.setText("Not connected to any server...")
            self.info_widget.setImage(ressources._no_connection_info_)

    def remove_all_users(self):
        users_list = list(self.user_ids.keys())
        for user_name in users_list:
            self.remove_user(user_name)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                gui_utils.move_ui(self)
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            gui_utils.move_ui(self)

class user_widget(QtWidgets.QFrame):
    def __init__(self, user_name, parent=None):
        super(user_widget, self).__init__(parent)
        self.user_name = user_name
        self.build_ui()
        self.fill_ui()

    def fill_ui(self):
        profile_image = site.get_user_row_by_name(self.user_name, 'profile_picture')
        gui_utils.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(profile_image), 26)
        self.user_name_label.setText(self.user_name)

    def build_ui(self):
        self.setObjectName('item_widget_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.profile_frame = QtWidgets.QFrame()
        self.profile_frame.setObjectName('user_profile_frame')
        self.profile_frame.setStyleSheet('#user_profile_frame{background-color:#9cf277;border-radius:15px;}')
        self.profile_layout = QtWidgets.QHBoxLayout()
        self.profile_layout.setContentsMargins(0,0,0,0)
        self.profile_frame.setLayout(self.profile_layout)
        self.profile_frame.setFixedSize(30,30)
        self.main_layout.addWidget(self.profile_frame)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(26,26)
        self.profile_layout.addWidget(self.profile_picture)

        self.user_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.user_name_label)