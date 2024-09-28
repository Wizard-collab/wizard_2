# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import traceback
import sys
import uuid
import time
import logging
import json

# Wizard core modules
from wizard.core import path_utils
from wizard.core import project
from wizard.core import user
from wizard.core import assets
from wizard.core import ffmpeg_utils
from wizard.vars import ressources
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui.video_manager import mpv_widget
from wizard.gui.video_manager import timeline_widget
from wizard.gui.video_manager import create_playlist_widget
from wizard.gui import confirm_widget

logger = logging.getLogger(__name__)

class video_player_widget(QtWidgets.QFrame):

    current_stage = pyqtSignal(int)
    current_variant = pyqtSignal(int)
    current_video_row = pyqtSignal(object)

    def __init__(self, parent=None):
        super(video_player_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Video player")

        self.load_video_threads = []
        self.player_id = str(uuid.uuid4())
        self.temp_dir = ffmpeg_utils.get_temp_dir()
        self.videos_dic = dict()
        self.load_threads = []
        self.frame_range = [0,1000]
        self.resolution = [1920,1080]
        self.video_player = mpv_widget.mpv_widget(self)
        self.timeline_widget = timeline_widget.timeline_widget(self)
        self.first_load = True
        self.modified = False
        self.current_playlist = None
        self.current_playlist_name = ''
        self.build_ui()
        self.connect_functions()
        self.set_fps(24)
        self.set_resolution([1920,1080])

    def need_player(self):
        self.video_player.create_mpv_player()

    def set_context(self):
        context_dic = dict()
        context_dic['current_playlist'] = self.current_playlist
        user.user().add_context(user_vars._video_player_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._video_player_context_)
        if context_dic is None:
            return
        if 'current_playlist' in context_dic.keys():
            self.load_playlist(context_dic['current_playlist'])

    def closeEvent(self, event):
        self.quit()

    def refresh(self):
        self.timeline_widget.refresh()

    def quit(self):
        self.video_player.quit()
        ffmpeg_utils.clear_player_files(self.temp_dir, self.player_id)
        for thread in self.load_video_threads:
            try:
                thread.on_videos_ready.disconnect()
            except TypeError:
                pass
            thread.kill()
            thread.wait()
            del thread

    def set_fps(self, fps=24):
        self.fps=fps
        self.video_player.set_fps(fps)
        self.timeline_widget.set_fps(fps)

    def show_preferences(self):
        self.preferences_dialog = preferences_widget(self.fps, self.resolution, self)
        if self.preferences_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            fps = self.preferences_dialog.fps
            resolution = self.preferences_dialog.resolution
            if fps != self.fps or resolution != self.resolution:
                self.set_fps(fps)
                self.set_resolution(resolution)
                self.update_concat()

    def set_resolution(self, resolution=[1920,1080]):
        self.resolution = resolution
        self.timeline_widget.set_resolution(resolution)

    def add_video(self, video_file, project_video_id=None):
        video_id = str(uuid.uuid4())
        self.videos_dic[video_id] = dict()
        self.videos_dic[video_id]['original_file'] = path_utils.abspath(video_file)
        self.videos_dic[video_id]['name'] = path_utils.basename(video_file)
        self.videos_dic[video_id]['frames_count'] = ffmpeg_utils.get_frames_count(video_file)
        self.videos_dic[video_id]['inpoint'] = 0
        self.videos_dic[video_id]['outpoint'] = self.videos_dic[video_id]['frames_count']
        self.videos_dic[video_id]['thumbnail'] = ffmpeg_utils.extract_first_frame(video_file, self.temp_dir)
        self.videos_dic[video_id]['project_video_id'] = project_video_id
        self.set_modified(True)

    def add_videos(self, videos_list):
        for video_path in videos_list:
            self.add_video(video_path)
        self.update_concat()

    def videos_loaded(self):
        self.set_info("New videos loaded")
        self.update_concat()

    def update_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.timeline_widget.set_frame_range(frame_range)

    def update_concat(self):
        logger.debug("Updating player content")
        self.set_info("Updating player content", 2)
        self.timeline_widget.update_videos_dic(self.videos_dic)
        self.video_player.load_video(ffmpeg_utils.concatenate_videos(self.temp_dir, self.player_id, self.videos_dic, self.fps), self.first_load)
        if self.first_load:
            self.first_load = False
        self.set_info("Player updated")

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.menu_widget = QtWidgets.QFrame()
        self.menu_layout = QtWidgets.QHBoxLayout()
        self.menu_layout.setContentsMargins(6,6,6,6)
        self.menu_layout.setSpacing(6)
        self.menu_widget.setLayout(self.menu_layout)
        self.main_layout.addWidget(self.menu_widget)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.menu_layout.addWidget(self.menu_bar)
        
        self.menu_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.player_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Player')
        self.show_preferences_action = self.player_action.addAction(QtGui.QIcon(ressources._settings_icon_), "Preferences")
        self.playlist_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Playlist')
        self.save_playlist_action = self.playlist_action.addAction(QtGui.QIcon(ressources._tool_save_), "Save playlist")
        self.save_as_new_playlist_action = self.playlist_action.addAction(QtGui.QIcon(ressources._tool_save_), "Save as new playlist")
        self.clear_playlist_action = self.playlist_action.addAction(QtGui.QIcon(ressources._tool_add_), "New playlist")
        self.export_video_file_action = self.playlist_action.addAction(QtGui.QIcon(ressources._tool_batch_publish_), "Export video")

        self.playlist_widget = QtWidgets.QFrame()
        self.playlist_layout = QtWidgets.QHBoxLayout()
        self.playlist_layout.setContentsMargins(10,10,10,10)
        self.playlist_layout.setSpacing(6)
        self.playlist_widget.setLayout(self.playlist_layout)
        self.main_layout.addWidget(self.playlist_widget)

        self.playlist_icon_label = QtWidgets.QLabel()
        self.playlist_icon_label.setPixmap(QtGui.QIcon(ressources._playlist_icon_).pixmap(22))
        self.playlist_layout.addWidget(self.playlist_icon_label)

        self.playlist_info_label = QtWidgets.QLabel("Current playlist : ")
        self.playlist_info_label.setObjectName('gray_label')
        self.playlist_layout.addWidget(self.playlist_info_label)

        self.current_playlist_label = QtWidgets.QLabel()
        self.current_playlist_label.setObjectName('bold_label')
        self.playlist_layout.addWidget(self.current_playlist_label)

        self.playlist_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background-color:black;")
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.container_layout = QtWidgets.QHBoxLayout()
        self.container_layout.setContentsMargins(0,0,0,0)
        self.container.setLayout(self.container_layout)
        self.main_layout.addWidget(self.container)

        self.container_layout.addWidget(self.video_player)
        self.main_layout.addWidget(self.timeline_widget)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_label_1 = QtWidgets.QLabel()
        self.infos_label_1.setObjectName('gray_label')
        self.infos_layout.addWidget(self.infos_label_1)

    def set_info(self, info, color=1):
        if color == 1:
            color = '#90d1f0'
        elif color == 2:
            color = '#f79360'
        elif color == 3:
            color = '#f0605b'
        self.infos_label_1.setText(info)
        self.infos_label_1.setStyleSheet(f"color:{color}")
        QtWidgets.QApplication.processEvents()

    def connect_functions(self):
        self.video_player.on_progress.connect(self.update_frame)
        self.video_player.on_frame_range_modified.connect(self.update_frame_range)
        self.video_player.on_play_toggle.connect(self.timeline_widget.set_play_pause)
        self.timeline_widget.on_seek.connect(self.video_player.seek_frame)
        self.timeline_widget.on_play_pause.connect(self.video_player.play_pause_toggle)
        self.timeline_widget.on_prev_frame.connect(self.video_player.previous_frame)
        self.timeline_widget.on_next_frame.connect(self.video_player.next_frame)
        self.timeline_widget.on_loop_toggle.connect(self.video_player.toggle_loop)
        self.timeline_widget.on_bounds_change.connect(self.video_player.set_bounds_range)
        self.timeline_widget.on_end_requested.connect(self.video_player.seek_end)
        self.timeline_widget.on_beginning_requested.connect(self.video_player.seek_beginning)
        self.timeline_widget.on_order_changed.connect(self.order_changed)
        self.timeline_widget.on_video_in_out_modified.connect(self.in_out_modified)
        self.timeline_widget.on_delete.connect(self.delete_videos)
        self.timeline_widget.current_stage.connect(self.current_stage.emit)
        self.timeline_widget.current_variant.connect(self.current_variant.emit)
        self.timeline_widget.current_video_row.connect(self.current_video_row.emit)
        self.timeline_widget.replace_videos.connect(self.replace_videos)
        self.timeline_widget.clear_playlist.connect(self.clear)
        self.show_preferences_action.triggered.connect(self.show_preferences)
        self.clear_playlist_action.triggered.connect(self.clear)
        self.save_playlist_action.triggered.connect(self.save_playlist)
        self.save_as_new_playlist_action.triggered.connect(self.save_as_new_playlist)
        self.export_video_file_action.triggered.connect(self.export_video_file)

    def replace_current_video(self, project_video_id):
        self.timeline_widget.replace_current_video(project_video_id)
        self.update_concat()
        self.set_modified(True)

    def replace_videos(self, data_tuples_list):
        for data_tuple in data_tuples_list:
            video_id = data_tuple[0]
            video_file = data_tuple[1]
            project_video_id = data_tuple[2]
            if video_id not in self.videos_dic.keys():
                logger.error("Video not found")
                return
            self.videos_dic[video_id]['original_file'] = path_utils.abspath(video_file)
            self.videos_dic[video_id]['name'] = path_utils.basename(video_file)
            self.videos_dic[video_id]['frames_count'] = ffmpeg_utils.get_frames_count(video_file)

            if self.videos_dic[video_id]['inpoint'] >= self.videos_dic[video_id]['frames_count']:
                self.videos_dic[video_id]['inpoint'] = self.videos_dic[video_id]['frames_count']-1
            if self.videos_dic[video_id]['outpoint'] > self.videos_dic[video_id]['frames_count']:
                self.videos_dic[video_id]['outpoint'] = self.videos_dic[video_id]['frames_count']

            self.videos_dic[video_id]['proxy'] = False
            self.videos_dic[video_id]['thumbnail'] = None
            self.videos_dic[video_id]['project_video_id'] = project_video_id
        self.update_concat()
        self.set_modified(True)

    def order_changed(self, new_order):
        self.videos_dic = dict(sorted(self.videos_dic.items(), key=lambda x: new_order.index(x[0])))
        self.update_concat()
        self.set_modified(True)

    def in_out_modified(self, modification_dic):
        self.videos_dic[modification_dic['id']]['inpoint'] = modification_dic['inpoint']
        self.videos_dic[modification_dic['id']]['outpoint'] = modification_dic['outpoint']
        self.update_concat()
        self.set_modified(True)

    def set_modified(self, is_modified):
        self.modified = is_modified
        if self.modified:
            self.current_playlist_label.setText(f'{self.current_playlist_name} *')
        else:
            self.current_playlist_label.setText(self.current_playlist_name)

    def clear(self):
        self.delete_videos(list(self.videos_dic.keys()))
        self.current_playlist = None
        self.current_playlist_name = ''
        self.current_playlist_label.setText(self.current_playlist_name)
        self.update()
        self.update_concat()
        self.set_modified(False)
        return 1

    def delete_videos(self, video_ids):
        for video_id in video_ids:
            if video_id in self.videos_dic.keys():
                del self.videos_dic[video_id]
        self.update_concat()
        self.set_modified(True)

    def update_frame(self, frame):
        self.timeline_widget.set_frame(frame)

    def get_playlist_dic(self):
        return self.videos_dic

    def save_playlist(self):
        if self.current_playlist is not None:
            assets.save_playlist(self.current_playlist, self.videos_dic, thumbnail_temp_path=self.get_first_thumbnail())
            self.set_modified(False)
            gui_server.refresh_team_ui()
        else:
            self.save_as_new_playlist()

    def save_as_new_playlist(self):
        self.create_playlist_widget = create_playlist_widget.create_playlist_widget(data=json.dumps(self.videos_dic), thumbnail_temp_path=self.get_first_thumbnail())
        if self.create_playlist_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.current_playlist = self.create_playlist_widget.playlist_id
            self.current_playlist_name = self.create_playlist_widget.playlist_name
            self.set_modified(False)
            gui_server.refresh_team_ui()

    def get_first_thumbnail(self):
        video_ids = list(self.videos_dic.keys())
        if len(video_ids) == 0:
            return
        thumbnail_path = self.videos_dic[video_ids[0]]['thumbnail']
        return thumbnail_path

    def export_playlist_as_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Playlist File", "", "JSON Files (*.json)", options=options)
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(self.get_playlist_dic(), f, indent=4)
            logger.info("Playlist saved successfully")
            self.set_info("Playlist saved successfully")

    def export_video_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save video file", "", "Mp4 Files (*.mp4)", options=options)
        if file_name:
            concat_file = ffmpeg_utils.get_concat_video_file(self.temp_dir, self.player_id)
            if not path_utils.isfile(concat_file):
                logger.warning("Nothing to export")
                self.set_info("Nothing to export", 2)
                return
            path_utils.copyfile(concat_file, file_name)
            logger.info("Video exported successfully")
            self.set_info("Video exported successfully")

    def load_playlist_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Playlist File", "", "JSON Files (*.json)", options=options)
        if file_name:
            with open(file_name, 'r') as f:
                videos_dic = json.load(f)
                self.load_playlist_dic(videos_dic)
        self.update_concat()
        self.set_modified(False)

    def load_playlist(self, playlist_id):
        if not self.clear():
            return
        if playlist_id is None:
            return
        playlist_row = project.get_playlist_data(playlist_id)
        if playlist_row is None:
            return
        self.current_playlist = playlist_id
        self.current_playlist_name = playlist_row['name']
        self.current_playlist_label.setText(self.current_playlist_name)
        playlist_data = json.loads(playlist_row['data'])
        self.load_playlist_dic(playlist_data)
        self.update_concat()
        self.set_modified(False)

    def load_playlist_dic(self, videos_dic):
        for video_id in videos_dic:
            videos_dic[video_id]['thumbnail'] = None
        self.videos_dic = videos_dic
        logger.info("Loading playlist")
        self.set_info("Loading playlist")

class preferences_widget(QtWidgets.QDialog):
    def __init__(self, fps, resolution, parent=None):
        super(preferences_widget, self).__init__(parent)
        self.fps = fps
        self.resolution = resolution

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Preferences")

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def connect_functions(self):
        self.fps_spinbox.valueChanged.connect(self.update_values)
        self.width_spinbox.valueChanged.connect(self.update_values)
        self.height_spinbox.valueChanged.connect(self.update_values)
        self.accept_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def update_values(self):
        self.fps = self.fps_spinbox.value()
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()
        self.resolution = (width, height)

    def fill_ui(self):
        self.fps_spinbox.setValue(self.fps)
        self.width_spinbox.setValue(self.resolution[0])
        self.height_spinbox.setValue(self.resolution[1])

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.settings_layout = QtWidgets.QFormLayout()
        self.settings_layout.setContentsMargins(0,0,0,0)
        self.settings_layout.setSpacing(6)
        self.main_layout.addLayout(self.settings_layout)

        self.fps_spinbox = QtWidgets.QSpinBox()
        self.fps_spinbox.setRange(0, 120)
        self.fps_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.settings_layout.addRow(QtWidgets.QLabel('Fps'), self.fps_spinbox)

        self.width_spinbox = QtWidgets.QSpinBox()
        self.width_spinbox.setRange(1, 10000)
        self.width_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.height_spinbox = QtWidgets.QSpinBox()
        self.height_spinbox.setRange(1, 10000)
        self.height_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.resolutions_layout = QtWidgets.QHBoxLayout()
        self.resolutions_layout.addWidget(self.width_spinbox)
        self.resolutions_layout.addWidget(self.height_spinbox)
        self.settings_layout.addRow(QtWidgets.QLabel('Resolution'), self.resolutions_layout)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.main_layout.addLayout(self.buttons_layout)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.buttons_layout.addWidget(self.cancel_button)
        self.accept_button = QtWidgets.QPushButton('Accept')
        self.accept_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.accept_button)
