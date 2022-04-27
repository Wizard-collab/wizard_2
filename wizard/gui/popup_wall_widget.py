# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import json
import traceback
import os
import time
import logging

# Wizard modules
from wizard.core import user
from wizard.core import site
from wizard.core import image
from wizard.core import game
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.core import path_utils
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class popup_wall_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(popup_wall_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.popup_ids = dict()
        self.popup_save_ids = dict()

        self.build_ui()
        self.move_ui()

    def build_ui(self):
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.popups_scrollArea = QtWidgets.QScrollArea()
        self.popups_scrollArea.setObjectName('transparent_widget')
        self.popup_scrollBar = self.popups_scrollArea.verticalScrollBar()

        self.popups_scrollArea_widget = QtWidgets.QWidget()
        self.popups_scrollArea_widget.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.popups_scrollArea_widget.setObjectName('transparent_widget')
        self.popups_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.popups_scrollArea_layout.setSpacing(6)
        self.popups_scrollArea_widget.setLayout(self.popups_scrollArea_layout)

        self.popups_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.popups_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.popups_scrollArea.setWidgetResizable(True)
        self.popups_scrollArea.setWidget(self.popups_scrollArea_widget)

        self.popups_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.popups_scrollArea)

    def move_ui(self):
        desktop = QtWidgets.QApplication.desktop()
        screenRect = desktop.screenGeometry()
        screen_minX = screenRect.topLeft().x()
        screen_minY = screenRect.topLeft().y()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.setMinimumHeight(screen_maxY-50)
        win_width = self.frameSize().width()
        win_heigth = self.frameSize().height()
        posx = screen_maxX - win_width
        posy = screen_minY
        self.move(posx, posy)

    def add_popup(self, event_row):
        if user.user().get_popups_enabled():
            widget = popup_event_widget(event_row)
            self.popup_ids[event_row['id']] = widget
            self.popups_scrollArea_layout.addWidget(widget)
            self.popup_ids[event_row['id']].time_out.connect(self.remove_popup)

    def add_custom_popup(self, data):
        if user.user().get_popups_enabled():
            popup_id = time.time()
            widget = popup_custom_widget(data[0], data[1], data[2], data[3], popup_id)
            self.popup_ids[popup_id] = widget
            self.popups_scrollArea_layout.addWidget(widget)
            self.popup_ids[popup_id].time_out.connect(self.remove_popup)

    def add_save_popup(self, version_id):
        if user.user().get_popups_enabled():
            widget = popup_save_widget(version_id)
            self.popup_save_ids[version_id] = widget
            self.popups_scrollArea_layout.addWidget(widget)
            self.popup_save_ids[version_id].time_out.connect(self.remove_save_popup)

    def remove_popup(self, popup_id):
        if popup_id in self.popup_ids.keys():
            widget = self.popup_ids[popup_id]
            del self.popup_ids[popup_id]

            if widget.is_comment:
                comment = widget.comment_textEdit.toPlainText()
                game.add_xps(3)
                game.analyse_comment(comment, 10)

            widget.setVisible(0)
            widget.setParent(None)
            widget.deleteLater()

    def remove_save_popup(self, popup_id):
        if popup_id in self.popup_save_ids.keys():
            widget = self.popup_save_ids[popup_id]
            del self.popup_save_ids[popup_id]

            comment = widget.comment_textEdit.toPlainText()
            game.add_xps(1)
            game.analyse_comment(comment, 2)

            widget.setVisible(0)
            widget.setParent(None)
            widget.deleteLater()

class popup_save_widget(QtWidgets.QFrame):

    time_out = pyqtSignal(int)

    def __init__(self, version_id, parent=None):
        super(popup_save_widget, self).__init__(parent)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.setObjectName('popup_event_frame')
        self.version_id = version_id
        self.build_ui()
        self.fill_ui()
        self.connect_functions()
        self.init_clock()
        self.start_clock()

    def enterEvent(self, event):
        self.timer.stop()

    def leaveEvent(self, event):
        self.start_clock()

    def init_clock(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.time_out.emit(self.version_id))
    
    def start_clock(self):
        keep_until_comment = user.user().get_keep_until_comment()
        if not keep_until_comment:
            duration = user.user().get_popups_duration()
            self.timer.start(duration*1000)

    def fill_ui(self):
        version_row = project.get_version_data(self.version_id)
        self.comment_textEdit.setText(version_row['comment'])
        self.version_name_label.setText(f"Version {version_row['name']}")

    def connect_functions(self):
        self.update_comment_button.clicked.connect(self.update_comment)
        self.quit_button.clicked.connect(lambda: self.time_out.emit(self.version_id))

    def update_comment(self):
        comment = self.comment_textEdit.toPlainText()
        assets.modify_version_comment(self.version_id, comment)
        gui_server.refresh_ui()
        self.time_out.emit(self.version_id)

    def build_ui(self):
        self.setMinimumWidth(320)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(17,17,17,17)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.save_image = QtWidgets.QLabel()
        self.save_image.setPixmap(QtGui.QIcon(ressources._save_icon_).pixmap(22))
        self.header_layout.addWidget(self.save_image)

        self.version_name_label = QtWidgets.QLabel()
        self.version_name_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.header_layout.addWidget(self.version_name_label)

        self.decoration_content = QtWidgets.QWidget()
        self.decoration_content.setObjectName('transparent_widget')
        self.decoration_content_layout = QtWidgets.QVBoxLayout()
        self.decoration_content_layout.setContentsMargins(0,0,0,0)
        self.decoration_content_layout.setSpacing(0)
        self.decoration_content.setLayout(self.decoration_content_layout)
        self.header_layout.addWidget(self.decoration_content)

        self.quit_button = gui_utils.close_button()
        self.quit_button.setIconSize(QtCore.QSize(12,12))
        self.quit_button.setObjectName('quit_button')
        self.quit_button.setFixedSize(16, 16)
        self.decoration_content_layout.addWidget(self.quit_button)
        
        self.decoration_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.comment_textEdit = QtWidgets.QTextEdit()
        self.comment_textEdit.setPlaceholderText('Your comment')
        self.comment_textEdit.setMaximumHeight(50)
        self.main_layout.addWidget(self.comment_textEdit)

        self.update_comment_button = QtWidgets.QPushButton('Comment')
        self.main_layout.addWidget(self.update_comment_button)

class popup_event_widget(QtWidgets.QFrame):

    time_out = pyqtSignal(int)

    def __init__(self, event_row, parent=None):
        super(popup_event_widget, self).__init__(parent)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.setObjectName('popup_event_frame')
        self.is_comment = False
        self.event_row = event_row
        self.build_ui()
        self.fill_ui()
        self.connect_functions()
        self.init_clock()
        self.start_clock()

    def enterEvent(self, event):
        self.timer.stop()

    def leaveEvent(self, event):
        self.start_clock()

    def init_clock(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.time_out.emit(self.event_row['id']))
    
    def start_clock(self):
        keep_until_comment = user.user().get_keep_until_comment()
        start_timer = True
        if self.is_comment and keep_until_comment:
            start_timer = False
        if start_timer:
            duration = user.user().get_popups_duration()
            self.timer.start(duration*1000)

    def fill_ui(self):
        profile_image = site.get_user_row_by_name(self.event_row['creation_user'], 'profile_picture')
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(profile_image), 'png', 30)
        self.profile_picture.setPixmap(pm)
        self.user_name_label.setText(self.event_row['creation_user'])
        self.event_title_label.setText(self.event_row['title'])
        if self.event_row['message'] is not None and self.event_row['message'] != '':
            self.event_content_label.setVisible(1)
            self.content_widget.setVisible(1)
            self.event_content_label.setText(self.event_row['message'])
        if self.event_row['additional_message'] is not None and self.event_row['additional_message'] != '':
            self.event_additional_content_label.setVisible(1)
            self.content_widget.setVisible(1)
            self.event_additional_content_label.setText(self.event_row['additional_message'])

        if self.event_row['type'] == 'creation':
            profile_color = '#77c5f2'
        elif self.event_row['type'] == 'export':
            profile_color = '#9cf277'

            # Show comment widget if user is current user
            if self.event_row['creation_user'] == environment.get_user():
                self.comment_widget.setVisible(True)
                self.is_comment = True

        elif self.event_row['type'] == 'archive':
            profile_color = '#f0605b'

        elif self.event_row['type'] == 'tag':
            profile_color = '#f0d969'

        self.profile_frame.setStyleSheet('#wall_profile_frame{background-color:%s;border-radius:17px;}'%profile_color)

    def connect_functions(self):
        self.comment_button.clicked.connect(self.update_comment)
        self.quit_button.clicked.connect(lambda: self.time_out.emit(self.event_row['id']))
        self.action_button.clicked.connect(self.action)

    def update_comment(self):
        comment = self.comment_textEdit.toPlainText()
        export_version_id = self.event_row['data']
        project.update_export_version_data(export_version_id, ('comment', comment))
        gui_server.refresh_ui()
        self.time_out.emit(self.event_row['id'])

    def action(self):
        if self.event_row['type'] == 'archive':
            path = path_utils.clean_path(json.loads(self.event_row['data']))
            if path_utils.isfile(path):
                path_utils.startfile(path)
        elif self.event_row['type'] == 'creation':
            data = json.loads(self.event_row['data'])
            gui_server.focus_instance(data)
        elif self.event_row['type'] == 'export':
            export_version_id = json.loads(self.event_row['data'])
            gui_server.focus_export_version(export_version_id)
        elif self.event_row['type'] == 'tag':
            data = json.loads(self.event_row['data'])
            instance_type = data['instance'][0]
            if instance_type == 'export_version':
                export_version_id = data['instance'][1]
                gui_server.focus_export_version(export_version_id)
            if instance_type == 'work_version':
                work_version_id = data['instance'][1]
                gui_server.focus_work_version(work_version_id)
            else:
                gui_server.focus_instance(data['instance'])

    def build_ui(self):
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setMinimumWidth(320)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(12)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.profile_frame = QtWidgets.QFrame()
        self.profile_frame.setObjectName('transparent_widget')
        self.profile_frame.setObjectName('wall_profile_frame')
        self.profile_layout = QtWidgets.QHBoxLayout()
        self.profile_layout.setContentsMargins(0,0,0,0)
        self.profile_frame.setLayout(self.profile_layout)
        self.profile_frame.setFixedSize(34,34)
        self.header_layout.addWidget(self.profile_frame)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(30,30)
        self.profile_layout.addWidget(self.profile_picture)

        self.title_widget = QtWidgets.QWidget()
        self.title_widget.setObjectName('transparent_widget')
        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.title_widget.setLayout(self.title_layout)
        self.header_layout.addWidget(self.title_widget)

        self.event_title_label = QtWidgets.QLabel()
        self.event_title_label.setWordWrap(True)
        self.event_title_label.setObjectName('bold_label')
        self.title_layout.addWidget(self.event_title_label)

        self.user_name_label = QtWidgets.QLabel()
        self.user_name_label.setObjectName('gray_label')
        self.title_layout.addWidget(self.user_name_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.decoration_content = QtWidgets.QWidget()
        self.decoration_content.setObjectName('transparent_widget')
        self.decoration_content_layout = QtWidgets.QVBoxLayout()
        self.decoration_content_layout.setContentsMargins(0,0,0,0)
        self.decoration_content_layout.setSpacing(0)
        self.decoration_content.setLayout(self.decoration_content_layout)
        self.header_layout.addWidget(self.decoration_content)

        self.decoration_content_2 = QtWidgets.QWidget()
        self.decoration_content_2.setObjectName('transparent_widget')
        self.decoration_content_layout_2 = QtWidgets.QHBoxLayout()
        self.decoration_content_layout_2.setContentsMargins(0,0,0,0)
        self.decoration_content_layout_2.setSpacing(0)
        self.decoration_content_2.setLayout(self.decoration_content_layout_2)
        self.decoration_content_layout.addWidget(self.decoration_content_2)

        self.action_button = gui_utils.transparent_button(ressources._rigth_arrow_transparent_icon_, 
                                                            ressources._rigth_arrow_icon_)
        self.action_button.setIconSize(QtCore.QSize(18,18))
        self.action_button.setFixedSize(16, 16)
        self.decoration_content_layout_2.addWidget(self.action_button)

        self.quit_button = gui_utils.close_button()
        self.quit_button.setIconSize(QtCore.QSize(12,12))
        self.quit_button.setObjectName('quit_button')
        self.quit_button.setFixedSize(16, 16)
        self.decoration_content_layout_2.addWidget(self.quit_button)
        
        self.decoration_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setVisible(0)
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(56,0,11,11)
        self.content_layout.setSpacing(12)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.event_content_label = QtWidgets.QLabel()
        self.event_content_label.setVisible(0)
        self.event_content_label.setWordWrap(True)
        self.content_layout.addWidget(self.event_content_label)

        self.event_additional_content_label = QtWidgets.QLabel()
        self.event_additional_content_label.setVisible(0)
        self.event_additional_content_label.setObjectName('gray_label')
        self.event_additional_content_label.setWordWrap(True)
        self.content_layout.addWidget(self.event_additional_content_label)

        self.comment_widget = QtWidgets.QWidget()
        self.comment_widget.setObjectName('transparent_widget')
        self.comment_widget_layout = QtWidgets.QVBoxLayout()
        self.comment_widget_layout.setContentsMargins(56,0,11,11)
        self.comment_widget_layout.setSpacing(4)
        self.comment_widget.setLayout(self.comment_widget_layout)
        self.main_layout.addWidget(self.comment_widget)
        self.comment_widget.setVisible(False)

        self.comment_textEdit = QtWidgets.QTextEdit()
        self.comment_textEdit.setMaximumHeight(50)
        self.comment_textEdit.setPlaceholderText('Your comment')
        self.comment_widget_layout.addWidget(self.comment_textEdit)

        self.comment_button = QtWidgets.QPushButton('Comment')
        self.comment_widget_layout.addWidget(self.comment_button)

class popup_custom_widget(QtWidgets.QFrame):

    time_out = pyqtSignal(float)

    def __init__(self, title, msg, icon, profile_picture, popup_id, parent=None):
        super(popup_custom_widget, self).__init__(parent)

        self.title = title
        self.msg = msg
        self.icon = icon
        self.profile_picture = profile_picture
        self.popup_id = popup_id
        
        self.is_comment = False

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.setObjectName('popup_event_frame')
        self.build_ui()
        self.fill_ui()
        self.connect_functions()
        self.init_clock()
        self.start_clock()

    def enterEvent(self, event):
        self.timer.stop()

    def leaveEvent(self, event):
        self.start_clock()

    def init_clock(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.time_out.emit(self.popup_id))
    
    def start_clock(self):
        duration = user.user().get_popups_duration()
        self.timer.start(duration*1000)

    def fill_ui(self):
        if self.icon:
            self.icon_picture.setPixmap(QtGui.QIcon(self.icon).pixmap(30))
        if self.profile_picture:
            profile_image = site.get_user_row_by_name(self.profile_picture, 'profile_picture')
            pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(profile_image), 'png', 30)
            self.icon_picture.setPixmap(pm)
        self.event_title_label.setText(self.title)
        self.msg_label.setText(self.msg)

    def connect_functions(self):
        self.quit_button.clicked.connect(lambda: self.time_out.emit(self.popup_id))

    def build_ui(self):
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setMinimumWidth(320)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(12)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.icon_picture = QtWidgets.QLabel()
        self.icon_picture.setFixedSize(30,30)
        self.header_layout.addWidget(self.icon_picture)

        self.title_widget = QtWidgets.QWidget()
        self.title_widget.setObjectName('transparent_widget')
        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.title_widget.setLayout(self.title_layout)
        self.header_layout.addWidget(self.title_widget)

        self.event_title_label = QtWidgets.QLabel()
        self.event_title_label.setWordWrap(True)
        self.event_title_label.setObjectName('bold_label')
        self.title_layout.addWidget(self.event_title_label)

        self.msg_label = QtWidgets.QLabel()
        self.msg_label.setObjectName('gray_label')
        self.title_layout.addWidget(self.msg_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.decoration_content = QtWidgets.QWidget()
        self.decoration_content.setObjectName('transparent_widget')
        self.decoration_content_layout = QtWidgets.QVBoxLayout()
        self.decoration_content_layout.setContentsMargins(0,0,0,0)
        self.decoration_content_layout.setSpacing(0)
        self.decoration_content.setLayout(self.decoration_content_layout)
        self.header_layout.addWidget(self.decoration_content)

        self.quit_button = gui_utils.close_button()
        self.quit_button.setIconSize(QtCore.QSize(12,12))
        self.quit_button.setObjectName('quit_button')
        self.quit_button.setFixedSize(16, 16)
        self.decoration_content_layout.addWidget(self.quit_button)
        
        self.decoration_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))
