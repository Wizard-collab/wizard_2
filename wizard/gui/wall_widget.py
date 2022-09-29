# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import os
import json
import copy
import traceback

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import user
from wizard.core import project
from wizard.core import image
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import ressources
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

class wall_widget(QtWidgets.QWidget):

    notification = pyqtSignal(int)
    popup = pyqtSignal(object)

    def __init__(self, parent=None):
        super(wall_widget, self).__init__(parent)

        self.last_time = 0
        self.event_rows = None
        self.event_ids = dict()
        self.time_widgets = []
        self.first_refresh = 1
        self.search_thread = search_thread()
        self.build_ui()
        self.init_users_images()
        self.connect_functions()
        self.get_context()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 30)
            self.users_images_dic[user_row['user_name']] = pixmap

    def connect_functions(self):
        self.wall_scrollBar.rangeChanged.connect(lambda: self.wall_scrollBar.setValue(self.wall_scrollBar.maximum()))
        self.search_bar.textChanged.connect(self.update_search)
        self.event_count_spinBox.valueChanged.connect(self.change_events_count)

        self.search_thread.show_id_signal.connect(self.show_search_event)
        self.search_thread.hide_id_signal.connect(self.hide_search_event)

    def build_ui(self):
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.header_frame = QtWidgets.QFrame()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_frame.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_frame)

        self.search_bar = gui_utils.search_bar()
        self.search_bar.setPlaceholderText('"tag", "@j.smith&export", "shot_0021", "creation"')
        self.header_layout.addWidget(self.search_bar)

        self.wall_scrollArea = QtWidgets.QScrollArea()
        self.wall_scrollBar = self.wall_scrollArea.verticalScrollBar()

        self.wall_scrollArea_widget = QtWidgets.QWidget()
        self.wall_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.wall_scrollArea_layout.setContentsMargins(0,0,0,8)
        self.wall_scrollArea_layout.setSpacing(0)
        self.wall_scrollArea_widget.setLayout(self.wall_scrollArea_layout)

        self.wall_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.wall_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.wall_scrollArea.setWidgetResizable(True)
        self.wall_scrollArea.setWidget(self.wall_scrollArea_widget)

        self.wall_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.wall_scrollArea)

        self.infos_frame = QtWidgets.QFrame()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(4,4,4,4)
        self.infos_frame.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_frame)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('tree_datas_label')
        self.infos_layout.addWidget(self.refresh_label)
        
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.infos_layout.addWidget(QtWidgets.QLabel('Show'))
        self.event_count_spinBox = QtWidgets.QSpinBox()
        self.event_count_spinBox.setButtonSymbols(2)
        self.event_count_spinBox.setRange(1, 10000000)
        self.event_count_spinBox.setFixedWidth(50)
        self.infos_layout.addWidget(self.event_count_spinBox)
        self.infos_layout.addWidget(QtWidgets.QLabel('events'))

    def set_context(self):
        if self.isVisible():
            visible = 1
        else:
            visible = 0
        context_dic = dict()
        context_dic['visibility'] = visible
        context_dic['events_count'] = self.event_count_spinBox.value()
        user.user().add_context(user_vars._wall_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._wall_context_)
        if context_dic is not None and context_dic != dict():
            if context_dic['visibility'] == 1:
                self.set_visible()
            elif context_dic['visibility'] == 0:
                self.set_hidden()
            self.event_count_spinBox.setValue(context_dic['events_count'])
        else:
            self.event_count_spinBox.setValue(10)

    def set_visible(self):
        if not self.isVisible():
            self.toggle()

    def set_hidden(self):
        if self.isVisible():
            self.toggle()

    def toggle(self):
        if self.isVisible():
            self.animate_hide()
        else:
            self.setVisible(1)
            self.notification.emit(0)
            self.animate_show()

    def animate_show(self):
        self.setMaximumWidth(300)
        self.setMinimumWidth(0)
        self.anim = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(100)
        self.anim.setStartValue(0)
        self.anim.setEndValue(300)
        self.anim.start()

    def animate_hide(self):
        self.setMaximumWidth(300)
        self.setMinimumWidth(0)
        self.anim = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(100)
        self.anim.setStartValue(300)
        self.anim.setEndValue(0)
        self.anim.finished.connect(lambda:self.setVisible(0))
        self.anim.start()

    def hide_all(self):
        for event_id in self.event_ids.keys():
            self.event_ids[event_id].setVisible(0)

    def show_all(self):
        for event_id in self.event_ids.keys():
            self.event_ids[event_id].setVisible(1)

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.search_thread.update_search(search_data, self.event_rows)
        else:
            self.show_all()

    def show_search_event(self, event_id):
        if event_id in self.event_ids.keys():
            self.event_ids[event_id].setVisible(True)

    def hide_search_event(self, event_id):
        if event_id in self.event_ids.keys():
            self.event_ids[event_id].setVisible(False)

    def refresh(self):
        start_time = time.time()
        self.event_rows = project.get_all_events()
        if self.event_rows is not None:

            event_number = self.event_count_spinBox.value()

            for event_row in self.event_rows[-event_number:]:
                if event_row['id'] not in self.event_ids.keys():
                    event_widget = wall_event_widget(event_row, self.users_images_dic)
                    if event_row['creation_time']-self.last_time > 350:
                        event_widget.add_time()
                    self.wall_scrollArea_layout.addWidget(event_widget)
                    self.event_ids[event_row['id']] = event_widget
                    self.last_time = event_row['creation_time']
                    if not self.isVisible() and self.first_refresh != 1:
                        self.notification.emit(1)
                    if self.first_refresh != 1:
                        if event_row['type'] == 'tag':
                            if (environment.get_user() in event_row['title']) or ('all' in event_row['title']):
                                self.popup.emit(event_row)
                        else:
                            self.popup.emit(event_row)
                            
            self.remove_useless_events(event_number)

        self.update_search()
        self.update_refresh_time(start_time)
        self.first_refresh = 0

    def change_events_count(self):
        self.last_time = 0
        event_ids_list = list(self.event_ids.keys())
        for event_id in event_ids_list:
            self.remove_event(event_id)
        self.first_refresh = 1
        self.refresh()

    def remove_useless_events(self, event_number):
        event_ids_list_to_remove = list(self.event_ids.keys())[:-event_number]
        for event_id in event_ids_list_to_remove:
            self.remove_event(event_id)
        self.event_ids[list(self.event_ids.keys())[0]].add_time()

    def remove_event(self, event_id):
        if event_id in self.event_ids.keys():
            self.event_ids[event_id].setParent(None)
            self.event_ids[event_id].deleteLater()
            del self.event_ids[event_id]

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

class wall_time_widget(QtWidgets.QWidget):
    def __init__(self, time_float, parent = None):
        super(wall_time_widget, self).__init__(parent)
        self.time_float = time_float
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(12,12,12,12)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.setSpacing(0)
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

    time_out = pyqtSignal(int)

    def __init__(self, event_row, users_images_dic, parent=None):
        super(wall_event_widget, self).__init__(parent)

        self.setObjectName('transparent_widget')
        self.event_row = event_row
        self.users_images_dic = users_images_dic
        self.time_widget = None
        self.build_ui()
        self.fill_ui()
        self.connect_functions()
    
    def fill_ui(self):
        self.profile_picture.setPixmap(self.users_images_dic[self.event_row['creation_user']])
        self.user_name_label.setText(self.event_row['creation_user'])
        self.event_title_label.setText(self.event_row['title'])
        if self.event_row['message'] is not None and self.event_row['message'] != '':
            self.event_content_label.setText(self.event_row['message'])
        else:
            self.event_content_label.setVisible(0)
        if self.event_row['additional_message'] is not None and self.event_row['additional_message'] != '':
            self.event_additional_content_label.setText(self.event_row['additional_message'])
        else:
            self.event_additional_content_label.setVisible(0)
        if self.event_row['image_path'] is not None:
            self.image_label.setPixmap(QtGui.QIcon(self.event_row['image_path']).pixmap(300))
        else:
            self.image_label.setVisible(0)
        self.action_button_button.setText('View')
        
        if self.event_row['type'] == 'creation':
            profile_color = '#77c5f2'
            gui_utils.application_tooltip(self.action_button_button, "Focus on instance")
        elif self.event_row['type'] == 'export':
            profile_color = '#9cf277'
            gui_utils.application_tooltip(self.action_button_button, "Focus on export version")
        elif self.event_row['type'] == 'archive':
            profile_color = '#f0605b'
            gui_utils.application_tooltip(self.action_button_button, "Open .zip file")
        elif self.event_row['type'] == 'video':
            profile_color = '#cb5cf0'
            gui_utils.application_tooltip(self.action_button_button, "Focus on video")
        elif self.event_row['type'] == 'tag':
            profile_color = '#f0d969'

        day, hour = tools.convert_time(self.event_row['creation_time'])
        self.time_label.setText(f"{day} - {hour}")

        if self.event_row['creation_user'] == environment.get_user():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.content_layout.setContentsMargins(0,0,41,0)
            self.event_title_label.setAlignment(QtCore.Qt.AlignRight)
            self.user_name_label.setAlignment(QtCore.Qt.AlignRight)
            self.event_content_label.setAlignment(QtCore.Qt.AlignRight)
            self.event_additional_content_label.setAlignment(QtCore.Qt.AlignRight)
            self.profile_frame.setStyleSheet('#wall_profile_frame{background-color:%s;border-radius:17px;border-bottom-left-radius:6px;}'%profile_color)
        else:
            self.profile_frame.setStyleSheet('#wall_profile_frame{background-color:%s;border-radius:17px;border-bottom-right-radius:6px;}'%profile_color)

    def connect_functions(self):
        self.action_button_button.clicked.connect(self.action)

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
        #elif self.event_row['type'] == 'video':
        #    export_version_id = json.loads(self.event_row['data'])
        #    gui_server.focus_video(video_id)
        elif self.event_row['type'] == 'tag':
            data = json.loads(self.event_row['data'])
            instance_type = data['instance'][0]
            if instance_type == 'export_version':
                export_version_id = data['instance'][1]
                gui_server.focus_export_version(export_version_id)
            if instance_type == 'work_version':
                work_version_id = data['instance'][1]
                gui_server.focus_work_version(work_version_id)
            #if instance_type == 'video':
            #    video_id = data['instance'][1]
            #    gui_server.focus_video(video_id)
            else:
                gui_server.focus_instance(data['instance'])

    def add_time(self):
        if self.time_widget == None:
            self.time_widget = wall_time_widget(self.event_row['creation_time'])
            self.widget_layout.insertWidget(0, self.time_widget)
            if self.event_row['creation_user'] == environment.get_user():
                self.time_widget.setLayoutDirection(QtCore.Qt.LeftToRight)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.widget_layout.setContentsMargins(8,1,8,1)
        self.widget_layout.setSpacing(1)
        self.setLayout(self.widget_layout)

        self.event_frame = QtWidgets.QFrame()
        self.event_frame.setObjectName('wall_event_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(9,9,9,9)
        self.main_layout.setSpacing(6)
        self.event_frame.setLayout(self.main_layout)
        self.widget_layout.addWidget(self.event_frame)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.main_layout.addLayout(self.header_layout)

        self.profile_subwidget_layout = QtWidgets.QVBoxLayout()
        self.profile_subwidget_layout.setContentsMargins(0,0,0,0)
        self.profile_subwidget_layout.setSpacing(0)
        self.header_layout.addLayout(self.profile_subwidget_layout)

        self.profile_frame = QtWidgets.QFrame()
        self.profile_frame.setObjectName('wall_profile_frame')
        self.profile_layout = QtWidgets.QHBoxLayout()
        self.profile_layout.setContentsMargins(0,0,0,0)
        self.profile_frame.setLayout(self.profile_layout)
        self.profile_frame.setFixedSize(34,34)
        self.profile_subwidget_layout.addWidget(self.profile_frame)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(30,30)
        self.profile_layout.addWidget(self.profile_picture)

        self.profile_subwidget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.header_layout.addLayout(self.title_layout)

        self.event_title_label = QtWidgets.QLabel()
        self.event_title_label.setWordWrap(True)
        self.event_title_label.setObjectName('bold_label')
        self.title_layout.addWidget(self.event_title_label)

        self.user_name_label = QtWidgets.QLabel()
        self.user_name_label.setObjectName('gray_label')
        self.title_layout.addWidget(self.user_name_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(41,0,0,0)
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.event_content_label = QtWidgets.QLabel()
        self.event_content_label.setWordWrap(True)
        self.content_layout.addWidget(self.event_content_label)

        self.event_additional_content_label = QtWidgets.QLabel()
        self.event_additional_content_label.setObjectName('gray_label')
        self.event_additional_content_label.setWordWrap(True)
        self.content_layout.addWidget(self.event_additional_content_label)

        self.image_label = QtWidgets.QLabel()
        self.content_layout.addWidget(self.image_label)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(2)
        self.content_layout.addLayout(self.buttons_layout)

        self.time_label = QtWidgets.QLabel()
        self.time_label.setObjectName('gray_label')
        self.buttons_layout.addWidget(self.time_label)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.action_button_button = QtWidgets.QPushButton()
        self.action_button_button.setIcon(QtGui.QIcon(ressources._rigth_arrow_icon_))
        self.action_button_button.setIconSize(QtCore.QSize(14,14))
        self.action_button_button.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.action_button_button.setObjectName('blue_text_button')
        self.buttons_layout.addWidget(self.action_button_button)

class search_thread(QtCore.QThread):

    show_id_signal = pyqtSignal(int)
    hide_id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, search_data, event_rows):
        self.running = False
        self.search_data = search_data
        self.event_rows = copy.deepcopy(event_rows)
        self.running = True
        self.start()

    def run(self):
        try:
            keywords = self.search_data.split('&')
            for event_row in self.event_rows:

                event_id = event_row['id']
                del event_row['id']
                del event_row['creation_time']
                del event_row['data']
                del event_row['image_path']

                values = list(event_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_id_signal.emit(event_id)
                else:
                    self.hide_id_signal.emit(event_id)
        except:
            logger.debug(str(traceback.format_exc()))