# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import uuid
import json

# Wizard core modules
from wizard.core import assets
from wizard.core import project
from wizard.core import image
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui.video_manager import create_playlist_widget

class buttons_bar_widget(QtWidgets.QWidget):

    on_play_pause = pyqtSignal(int)
    on_loop_toggle = pyqtSignal(int)

    def __init__(self, parent=None):
        super(buttons_bar_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.content_1_layout = QtWidgets.QHBoxLayout()
        self.content_1_layout.setContentsMargins(6,6,6,6)
        self.main_layout.addLayout(self.content_1_layout)

        self.play_pause_button = gui_utils.transparent_button(ressources._player_play_icon_, ressources._player_play_icon_hover_)
        self.play_pause_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.play_pause_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.play_pause_button)

        self.loop_button = gui_utils.transparent_button(ressources._player_loop_icon_,
                                                        ressources._player_loop_icon_hover_,
                                                        checked_icon=ressources._player_loop_icon_checked_)
        self.loop_button.setCheckable(True)
        self.loop_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.loop_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.loop_button)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def connect_functions(self):
        self.play_pause_button.clicked.connect(self.on_play_pause.emit)
        self.loop_button.toggled.connect(self.on_loop_toggle.emit)

    def set_play_pause(self, playing):
        if playing:
            self.play_pause_button.icon = ressources._player_pause_icon_
            self.play_pause_button.hover_icon = ressources._player_pause_icon_hover_
            self.play_pause_button.update_icon()
        else:
            self.play_pause_button.icon = ressources._player_play_icon_
            self.play_pause_button.hover_icon = ressources._player_play_icon_hover_
            self.play_pause_button.update_icon()

class timeline_widget(QtWidgets.QFrame):

    load_video = pyqtSignal(str)
    current_video_row = pyqtSignal(object)
    current_stage = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.videos_dic = dict()
        self.current_index = 0
        self.current_playlist = None
        self.current_playlist_id = None
        self.modified = False
        self.loop = False
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.save_as_playlist_button.clicked.connect(self.save_as_playlist)
        self.save_playlist_button.clicked.connect(self.save_playlist)
        self.new_playlist_button.clicked.connect(self.clear_playlist)

    def load_playlist(self, playlist_id):
        playlist_row = project.get_playlist_data(playlist_id)
        if not playlist_row:
            return
        self.clear_playlist()
        self.current_playlist = playlist_row['name']
        self.current_playlist_id = playlist_id
        playlist_dic = json.loads(playlist_row['data'])
        for unique_id in playlist_dic.keys():
            self.add_video(playlist_dic[unique_id], unique_id, modification=False)
        self.refresh()

    def create_playlist_and_add_videos(self, video_ids):
        self.clear_playlist()
        self.add_videos(video_ids)

    def clear_playlist(self):
        self.current_playlist = None
        self.current_playlist_id = None

        for unique_id in self.videos_dic.keys():
            item = self.videos_dic[unique_id]['item']
            item.setVisible(False)
            item.setParent(None)
            item.deleteLater()

        self.videos_dic = dict()
        self.current_index = 0
        self.modified = False
        self.load_video.emit('')
        self.current_stage.emit(None)
        self.current_video_row.emit(None)
        self.refresh()

    def save_as_playlist(self):
        thumbnail_path = None
        if self.videos_dic:
            thumbnail_path = self.videos_dic[list(self.videos_dic.keys())[0]]['video_row']['thumbnail_path']
        self.create_playlist_widget = create_playlist_widget.create_playlist_widget(data=json.dumps(self.get_playlist_dic()), thumbnail_temp_path=thumbnail_path)
        if self.create_playlist_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            playlist_id = self.create_playlist_widget.playlist_id
            self.load_playlist(playlist_id)

    def save_playlist(self):
        if not self.current_playlist:
            return self.save_as_playlist()
        thumbnail_path = None
        if self.videos_dic:
            thumbnail_path = self.videos_dic[list(self.videos_dic.keys())[0]]['video_row']['thumbnail_path']
        assets.save_playlist(self.current_playlist_id, data=self.get_playlist_dic(), thumbnail_temp_path=thumbnail_path)
        self.modified=False
        self.refresh()

    def get_playlist_dic(self):
        playlist_dic = dict()
        for unique_id in self.videos_dic.keys():
            playlist_dic[unique_id] = self.videos_dic[unique_id]['video_id']
        return playlist_dic

    def set_loop(self, loop):
        self.loop = loop

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.video_items_scrollArea = QtWidgets.QScrollArea()
        self.video_items_scrollArea.setMaximumHeight(110)
        self.video_items_scrollArea.setMinimumHeight(110)
        self.video_items_scrollArea.setObjectName('main_widget')
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

        self.playlist_widget = QtWidgets.QWidget()
        self.playlist_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.playlist_layout = QtWidgets.QHBoxLayout()
        self.playlist_widget.setLayout(self.playlist_layout)
        self.main_layout.addWidget(self.playlist_widget)

        self.current_playlist_label = QtWidgets.QLabel()
        self.current_playlist_label.setObjectName('bold_label')
        self.playlist_layout.addWidget(self.current_playlist_label)

        self.save_playlist_button = QtWidgets.QPushButton('Save playlist')
        self.save_playlist_button.setFixedSize(110, 40)
        self.save_playlist_button.setIcon(QtGui.QIcon(ressources._save_icon_))
        self.playlist_layout.addWidget(self.save_playlist_button)

        self.save_as_playlist_button = QtWidgets.QPushButton('Save as new playlist')
        self.save_as_playlist_button.setFixedSize(150, 40)
        self.save_as_playlist_button.setIcon(QtGui.QIcon(ressources._save_icon_))
        self.playlist_layout.addWidget(self.save_as_playlist_button)

        self.new_playlist_button = QtWidgets.QPushButton('New playlist')
        self.new_playlist_button.setFixedSize(100, 40)
        self.playlist_layout.addWidget(self.new_playlist_button)

    def add_videos(self, video_ids):
        for video_id in video_ids:
            self.add_video(video_id)

    def refresh(self):
        category_rows = project.get_all_categories()
        categories = dict()
        for category_row in category_rows:
            categories[category_row['id']] = category_row
        asset_rows = project.get_all_assets()
        assets = dict()
        for asset_row in asset_rows:
            assets[asset_row['id']] = asset_row
        stage_rows = project.get_all_stages()
        stages = dict()
        for stage_row in stage_rows:
            stages[stage_row['id']] = stage_row
        variant_rows = project.get_all_variants()
        variants = dict()
        for variant_row in variant_rows:
            variants[variant_row['id']] = variant_row
        video_rows = project.get_all_videos()
        videos = dict()
        variant_videos = dict()
        for video_row in video_rows:
            videos[video_row['id']] = video_row
            if video_row['variant_id'] not in variant_videos.keys():
                variant_videos[video_row['variant_id']] = video_row['id']
            if video_row['id'] > variant_videos[video_row['variant_id']]:
                variant_videos[video_row['variant_id']] = video_row['id']

        for unique_id in self.videos_dic.keys():
            video_item = self.videos_dic[unique_id]['item']
            video_row = videos[self.videos_dic[unique_id]['video_id']]
            self.videos_dic[unique_id]['video_row'] = video_row
            video_item.set_video_row(video_row)
            variant_row = variants[video_row['variant_id']]
            self.videos_dic[unique_id]['variant_row'] = variant_row
            video_item.set_variant_row(variant_row)
            stage_row = stages[variant_row['stage_id']]
            self.videos_dic[unique_id]['stage_row'] = stage_row
            video_item.set_stage_row(stage_row)
            asset_row = assets[stage_row['asset_id']]
            video_item.set_asset_row(asset_row)
            category_row = categories[asset_row['category_id']]
            video_item.set_category_row(category_row)
            last_variant_video_id = variant_videos[video_row['variant_id']]
            video_item.set_is_last(video_row['id'] == last_variant_video_id)
            video_item.fill_ui()

        text = ''
        if self.current_playlist:
            text += self.current_playlist
        else:
            text += 'Untitled'
        if self.modified:
            text+= ' *'
        self.current_playlist_label.setText(text)

        self.update_timeline()

    def add_video(self, video_id, unique_id = None, modification=True):
        if unique_id is None:
            unique_id = str(uuid.uuid4())
        video_row = project.get_video_data(video_id)
        variant_row = project.get_variant_data(video_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        self.videos_dic[unique_id] = dict()
        self.videos_dic[unique_id]['video_id'] = video_id
        self.videos_dic[unique_id]['video_row'] = video_row
        self.videos_dic[unique_id]['item'] = video_item(unique_id)
        self.videos_dic[unique_id]['item'].double_click.connect(self.view_video)
        self.video_items_content_layout.addWidget(self.videos_dic[unique_id]['item'])

        if len(self.videos_dic.keys()) == 1:
            self.load_video.emit(self.videos_dic[unique_id]['video_row']['file_path'])
        self.modified = modification
        self.refresh()

    def replace_current_video(self, video_id):
        video_path = project.get_video_data(video_id, 'file_path')

        try:
            current_unique_id = list(self.videos_dic.keys())[self.current_index]
        except IndexError:
            return
        video_row = project.get_video_data(video_id)

        self.videos_dic[current_unique_id]['video_id'] = video_id
        self.videos_dic[current_unique_id]['video_row'] = video_row
        self.load_video.emit(self.videos_dic[current_unique_id]['video_row']['file_path'])
        self.modified = 1
        self.refresh()

    def view_video(self, unique_id):
        if unique_id not in self.videos_dic.keys():
            return
        self.load_video.emit(self.videos_dic[unique_id]['video_row']['file_path'])
        self.current_index = list(self.videos_dic.keys()).index(unique_id)
        self.refresh()

    def play_next(self):
        if not self.loop:
            if self.current_index+1 > len(self.videos_dic.keys())-1:
                self.current_index = 0
            else:
                self.current_index += 1
        self.load_video.emit(self.videos_dic[list(self.videos_dic.keys())[self.current_index]]['video_row']['file_path'])
        self.refresh()

    def update_timeline(self):
        for unique_id in self.videos_dic.keys():
            index = list(self.videos_dic.keys()).index(unique_id)
            if index == self.current_index:
                self.videos_dic[unique_id]['item'].set_current(True)
                self.current_video_row.emit(self.videos_dic[unique_id]['video_row'])
                self.current_stage.emit(self.videos_dic[unique_id]['stage_row']['id'])
            else:
                self.videos_dic[unique_id]['item'].set_current(False)

class video_item(QtWidgets.QFrame):

    double_click = pyqtSignal(object)

    def __init__(self, unique_id, parent=None):
        super().__init__(parent)
        self.unique_id = unique_id
        self.video_row = None
        self.stage_row = None
        self.asset_row = None
        self.category_row = None
        self.variant_row = None
        self.hover = False
        self.current = False
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setMaximumHeight(90)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(4,4,4,4)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.asset_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.asset_label)

        self.content_1_layout = QtWidgets.QHBoxLayout()
        self.content_1_layout.setContentsMargins(0,0,0,0)
        self.content_1_layout.setSpacing(0)
        self.main_layout.addLayout(self.content_1_layout)
        
        self.image_label = QtWidgets.QLabel()
        self.content_1_layout.addWidget(self.image_label)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.content_2_layout = QtWidgets.QVBoxLayout()
        self.content_2_layout.setContentsMargins(0,0,0,0)
        self.content_2_layout.setSpacing(4)
        self.content_1_layout.addLayout(self.content_2_layout)

        self.state_label = QtWidgets.QLabel()
        self.content_2_layout.addWidget(self.state_label)

        self.content_2_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.is_last_indicator = QtWidgets.QWidget(self)
        self.is_last_indicator.setFixedSize(10,10)
        self.is_last_indicator.move(10,30)
        self.is_last_indicator.setStyleSheet('background-color:#b6864e;border-radius:5px;')

    def set_video_row(self, video_row):
        self.video_row = video_row

    def set_variant_row(self, variant_row):
        self.variant_row = variant_row

    def set_stage_row(self, stage_row):
        self.stage_row = stage_row

    def set_asset_row(self, asset_row):
        self.asset_row = asset_row

    def set_category_row(self, category_row):
        self.category_row = category_row

    def enterEvent(self, event):
        self.hover = True
        self.update_state()

    def leaveEvent(self, event):
        self.hover = False
        self.update_state()

    def update_state(self):
        stylesheet = '#round_frame{'
        if self.current:
            stylesheet += 'border:2px solid rgba(160,160,170,255)'
        if self.hover and not self.current:
            stylesheet += 'border: 2px solid rgba(80,80,90,255)'
        if (not self.hover) and (not self.current):
            stylesheet += 'border: 2px solid rgba(255,255,255,0)'
        stylesheet += '}'
        self.setStyleSheet(stylesheet)

    def fill_ui(self):
        self.asset_label.setText(f"{self.category_row['name']} - {self.asset_row['name']} - {self.stage_row['name']}")
        image_path = self.video_row['thumbnail_path']
        image_bytes = image.convert_image_to_bytes(image_path)
        pm = gui_utils.round_corners_image_button(image_bytes, (96, 56), 5)
        self.image_label.setPixmap(pm)
        self.state_label.setText(self.stage_row['state'])
        self.state_label.setStyleSheet('background-color:%s;border-radius:4px;padding:4px;'%ressources._states_colors_[self.stage_row['state']])

    def set_current(self, current):
        if current:
            self.current = True
        else:
            self.current = False
        self.update_state()

    def mouseDoubleClickEvent(self, event):
        self.double_click.emit(self.unique_id)


    def set_is_last(self, is_last):
        if is_last:
            self.is_last_indicator.setStyleSheet('background-color:#7ca657;border-radius:5px;')
        else:
            self.is_last_indicator.setStyleSheet('background-color:#b6864e;border-radius:5px;')
