# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import uuid

# Wizard core modules
from wizard.core import project
from wizard.core import image

# Wizard gui modules
from wizard.gui import gui_utils

class timeline_widget(QtWidgets.QFrame):

    load_video = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.videos_dic = dict()
        self.current_index = 0
        self.build_ui()

    def build_ui(self):
        self.setMaximumHeight(80)
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.video_items_scrollArea = QtWidgets.QScrollArea()
        self.video_items_scrollArea.setObjectName('transparent_widget')
        self.video_items_scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.video_items_scrollBar = self.video_items_scrollArea.horizontalScrollBar()

        self.video_items_scrollArea_widget = QtWidgets.QWidget()
        self.video_items_scrollArea_widget.setObjectName('transparent_widget')
        self.video_items_scrollArea_layout = QtWidgets.QHBoxLayout()
        self.video_items_scrollArea_layout.setContentsMargins(4,4,4,4)
        self.video_items_scrollArea_layout.setSpacing(0)
        self.video_items_scrollArea_widget.setLayout(self.video_items_scrollArea_layout)
        self.video_items_scrollArea.setWidgetResizable(True)
        self.video_items_scrollArea.setWidget(self.video_items_scrollArea_widget)
        self.main_layout.addWidget(self.video_items_scrollArea)

        self.video_items_content_widget = QtWidgets.QWidget()
        self.video_items_content_widget.setObjectName('transparent_widget')
        self.video_items_content_layout = QtWidgets.QHBoxLayout()
        self.video_items_content_layout.setContentsMargins(0,0,0,0)
        self.video_items_content_layout.setSpacing(2)
        self.video_items_content_widget.setLayout(self.video_items_content_layout)
        self.video_items_scrollArea_layout.addWidget(self.video_items_content_widget)

        self.video_items_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def add_videos(self, video_ids):
        for video_id in video_ids:
            self.add_video(video_id)

    def add_video(self, video_id):
        unique_id = uuid.uuid4()
        video_row = project.get_video_data(video_id)
        self.videos_dic[unique_id] = dict()
        self.videos_dic[unique_id]['video_id'] = video_id
        self.videos_dic[unique_id]['video_row'] = video_row
        self.videos_dic[unique_id]['item'] = video_item(video_row, unique_id)
        self.videos_dic[unique_id]['item'].double_click.connect(self.view_video)
        self.video_items_content_layout.addWidget(self.videos_dic[unique_id]['item'])

        if len(self.videos_dic.keys()) == 1:
            self.load_video.emit(self.videos_dic[unique_id]['video_row']['file_path'])
            self.update_timeline()

    def view_video(self, unique_id):
        if unique_id not in self.videos_dic.keys():
            return
        self.load_video.emit(self.videos_dic[unique_id]['video_row']['file_path'])
        self.current_index = list(self.videos_dic.keys()).index(unique_id)
        self.update_timeline()

    def play_next(self):
        if self.current_index+1 > len(self.videos_dic.keys())-1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.load_video.emit(self.videos_dic[list(self.videos_dic.keys())[self.current_index]]['video_row']['file_path'])
        self.update_timeline()

    def update_timeline(self):
        for unique_id in self.videos_dic.keys():
            index = list(self.videos_dic.keys()).index(unique_id)
            if index == self.current_index:
                self.videos_dic[unique_id]['item'].set_current(True)
            else:
                self.videos_dic[unique_id]['item'].set_current(False)

class video_item(QtWidgets.QFrame):

    double_click = pyqtSignal(object)

    def __init__(self, video_row, unique_id, parent=None):
        super().__init__(parent)
        self.unique_id = unique_id
        self.video_row = video_row
        self.hover = False
        self.current = False
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setFixedSize(100,60)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.main_layout)
        self.image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.image_label)

    def enterEvent(self, event):
        self.hover = True
        self.update_state()

    def leaveEvent(self, event):
        self.hover = False
        self.update_state()

    def update_state(self):
        stylesheet = '#round_frame{'
        if self.current:
            stylesheet += 'background-color:rgba(255,255,255,160)'
        if self.hover and not self.current:
            stylesheet += 'background-color:rgba(255,255,255,80)'
        stylesheet += '}'
        self.setStyleSheet(stylesheet)

    def fill_ui(self):
        image_path = self.video_row['thumbnail_path']
        image_bytes = image.convert_image_to_bytes(image_path)
        pm = gui_utils.round_corners_image_button(image_bytes, (96, 56), 5)

        self.image_label.setPixmap(pm)

    def set_current(self, current):
        if current:
            self.current = True
        else:
            self.current = False
        self.update_state()

    def mouseDoubleClickEvent(self, event):
        self.double_click.emit(self.unique_id)

