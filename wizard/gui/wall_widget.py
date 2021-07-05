# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import time

# Wizard modules
from wizard.core import site
from wizard.core import project
from wizard.core import image
from wizard.core import tools
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class wall_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(wall_widget, self).__init__(parent)
        self.last_time = 0
        self.ticket_ids = []
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def connect_functions(self):
        self.wall_scrollBar.rangeChanged.connect(lambda: self.wall_scrollBar.setValue(self.wall_scrollBar.maximum()))

    def build_ui(self):
        self.setMaximumWidth(300)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.wall_scrollArea = QtWidgets.QScrollArea()
        self.wall_scrollBar = self.wall_scrollArea.verticalScrollBar()

        self.wall_scrollArea_widget = QtWidgets.QWidget()
        self.wall_scrollArea_widget.setObjectName('wall_scroll_area')
        self.wall_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.wall_scrollArea_layout.setSpacing(6)
        self.wall_scrollArea_widget.setLayout(self.wall_scrollArea_layout)

        self.wall_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.wall_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.wall_scrollArea.setWidgetResizable(True)
        self.wall_scrollArea.setWidget(self.wall_scrollArea_widget)

        self.main_layout.addWidget(self.wall_scrollArea)

    def refresh(self):
        event_rows = project.get_all_events()
        if event_rows is not None:
            for event_row in event_rows[-10:]:
                if event_row['id'] not in self.ticket_ids:
                    if event_row['creation_time']-self.last_time > 350:
                        time_widget = wall_time_widget(event_row['creation_time'])
                        self.wall_scrollArea_layout.addWidget(time_widget)
                    event_widget = wall_event_widget(event_row)
                    self.wall_scrollArea_layout.addWidget(event_widget)
                    self.ticket_ids.append(event_row['id'])
                    self.last_time = event_row['creation_time']

class wall_time_widget(QtWidgets.QWidget):
    def __init__(self, time_float, parent = None):
        super(wall_time_widget, self).__init__(parent)
        self.time_float = time_float
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(4,4,4,4)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        day, hour = tools.convert_time(self.time_float)
        self.day_label = QtWidgets.QLabel(f"{day} - ")
        self.day_label.setObjectName('gray_label')
        self.hour_label = QtWidgets.QLabel(hour)
        self.hour_label.setObjectName('bold_label')

        current_day, current_hour = tools.convert_time(time.time())
        if current_day != day:
            self.main_layout.addWidget(self.day_label)
            
        self.main_layout.addWidget(self.hour_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

class wall_event_widget(QtWidgets.QFrame):
    def __init__(self, event_row, parent=None):
        super(wall_event_widget, self).__init__(parent)
        self.setObjectName('wall_event_frame')
        self.event_row = event_row
        self.build_ui()
        self.fill_ui()
    
    def fill_ui(self):
        profile_image = site.get_user_row_by_name(self.event_row['creation_user'], 'profile_picture')
        gui_utils.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(profile_image), 40)
        self.user_name_label.setText(self.event_row['creation_user'])
        self.event_title_label.setText(self.event_row['title'])
        self.event_content_label.setText(self.event_row['message'])
        self.action_button_button.setText('View')
        
        if self.event_row['type'] == 'creation':
            profile_color = '#77c5f2'
        elif self.event_row['type'] == 'export':
            profile_color = '#9cf277'
        elif 'ticket' in self.event_row['type']:
            profile_color = '#f79360'
        elif self.event_row['type'] == 'archive':
            profile_color = '#f0605b'

        self.profile_frame.setStyleSheet('#wall_profile_frame{background-color:%s;border-radius:22px;}'%profile_color)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(12)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.profile_frame = QtWidgets.QFrame()
        self.profile_frame.setObjectName('wall_profile_frame')
        self.profile_layout = QtWidgets.QHBoxLayout()
        self.profile_layout.setContentsMargins(0,0,0,0)
        self.profile_frame.setLayout(self.profile_layout)
        self.profile_frame.setFixedSize(44,44)
        self.header_layout.addWidget(self.profile_frame)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(40,40)
        self.profile_layout.addWidget(self.profile_picture)

        self.title_widget = QtWidgets.QWidget()
        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.title_widget.setLayout(self.title_layout)
        self.header_layout.addWidget(self.title_widget)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.user_name_label = QtWidgets.QLabel()
        self.user_name_label.setObjectName('title_label')
        self.title_layout.addWidget(self.user_name_label)

        self.event_title_label = QtWidgets.QLabel()
        self.event_title_label.setWordWrap(True)
        self.event_title_label.setObjectName('gray_label')
        self.title_layout.addWidget(self.event_title_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        
        self.event_content_label = QtWidgets.QLabel()
        self.event_content_label.setWordWrap(True)
        self.main_layout.addWidget(self.event_content_label)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.action_button_button = QtWidgets.QPushButton()
        self.action_button_button.setIcon(QtGui.QIcon(ressources._rigth_arrow_icon_))
        self.action_button_button.setIconSize(QtCore.QSize(14,14))
        self.action_button_button.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.action_button_button.setObjectName('blue_text_button')
        self.buttons_layout.addWidget(self.action_button_button)
