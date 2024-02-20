# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import traceback
import sys
import uuid
import time
import logging

# Wizard core modules
from wizard.core import path_utils
from wizard.core.video_player import ffmpeg_utils
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui import gui_utils
from wizard.gui.video_manager import mpv_widget
from wizard.gui.video_manager import video_threads
from wizard.gui.video_manager import timeline_widget

logger = logging.getLogger(__name__)

class video_player_widget(QtWidgets.QWidget):

    current_stage = pyqtSignal(int)

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
        self.concat_thread = video_threads.concat_thread(self.temp_dir, self.player_id, self)
        self.video_player = mpv_widget.mpv_widget(self)
        self.timeline_widget = timeline_widget.timeline_widget(self)
        self.first_load = True
        self.build_ui()
        self.connect_functions()
        self.set_fps(24)
        self.set_resolution([1920,1080])

    def need_player(self):
        self.video_player.create_mpv_player()

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
        self.concat_thread.quit()

    def set_fps(self, fps=24):
        self.fps=fps
        self.video_player.set_fps(fps)
        self.timeline_widget.set_fps(fps)
        self.concat_thread.set_fps(fps)

    def show_preferences(self):
        self.preferences_dialog = preferences_widget(self.fps, self.resolution, self)
        if self.preferences_dialog.exec_() == QtWidgets.QDialog.Accepted:
            fps = self.preferences_dialog.fps
            resolution = self.preferences_dialog.resolution
            if fps != self.fps or resolution != self.resolution:
                self.clear_all_proxys()
                self.set_fps(fps)
                self.set_resolution(resolution)
                self.load_nexts()

    def set_resolution(self, resolution=[1920,1080]):
        self.resolution = resolution
        self.timeline_widget.set_resolution(resolution)

    def clear_all_proxys(self):
        for video_id in self.videos_dic.keys():
            self.clear_proxy(self.videos_dic[video_id]['original_file'])
            self.videos_dic[video_id]['proxy'] = False
            self.timeline_widget.update_videos_dic(self.videos_dic)

    def clear_proxy(self, original_file):
        ffmpeg_utils.delete_proxy(self.temp_dir, original_file)

    def hard_clear_proxys(self):
        ffmpeg_utils.hard_clear_proxys(self.temp_dir)

    def clear_cache_and_reload(self):
        self.set_info("Clearing cache", 2)
        self.clear_all_proxys()
        self.check_proxys_soft()
        self.load_nexts()

    def clear_all_cache_and_reload(self):
        self.set_info("Clearing all cache", 2)
        self.hard_clear_proxys()
        self.check_proxys_soft()
        self.load_nexts()

    def add_video(self, video_file, project_video_id=None):
        video_id = str(uuid.uuid4())
        self.videos_dic[video_id] = dict()
        self.videos_dic[video_id]['original_file'] = path_utils.abspath(video_file)
        self.videos_dic[video_id]['name'] = path_utils.basename(video_file)
        self.videos_dic[video_id]['frames_count'] = ffmpeg_utils.get_frames_count(video_file)
        self.videos_dic[video_id]['inpoint'] = 0
        self.videos_dic[video_id]['outpoint'] = self.videos_dic[video_id]['frames_count']
        self.videos_dic[video_id]['proxy'] = False
        self.videos_dic[video_id]['thumbnail'] = None
        self.videos_dic[video_id]['project_video_id'] = project_video_id

    def check_proxys_soft(self):
        for video_id in self.videos_dic.keys():
            self.videos_dic[video_id]['proxy'] = ffmpeg_utils.check_if_proxy_exists(self.temp_dir, self.videos_dic[video_id]['original_file'])
            self.videos_dic[video_id]['thumbnail'] = ffmpeg_utils.check_if_thumbnail_exists(self.temp_dir, self.videos_dic[video_id]['original_file'])

    def add_videos(self, videos_list):
        for video_path in videos_list:
            self.add_video(video_path)
        self.check_proxys_soft()
        self.give_concat_job()
        self.load_nexts()

    def give_concat_job(self):
        self.set_info("Creating concat stream", 2)
        self.concat_thread.give_job(self.videos_dic)

    def load_nexts(self, number=3):
        need_proxies = False
        for video_id in self.videos_dic.keys():
            if not self.videos_dic[video_id]['proxy']:
                need_proxies = True
        if not need_proxies:
            return
        self.set_info("Loading videos", 2)
        thread = video_threads.create_multiple_proxies(self.videos_dic,
                                                        self.temp_dir,
                                                        number,
                                                        self.resolution,
                                                        self.fps)
        thread.on_videos_ready.connect(self.videos_loaded)
        thread.start()
        self.load_video_threads.append(thread)

    def videos_loaded(self):
        self.set_info("New videos loaded")
        self.check_proxys_soft()
        self.timeline_widget.update_videos_dic(self.videos_dic)
        self.give_concat_job()

    def update_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.timeline_widget.set_frame_range(frame_range)

    def update_concat(self, concat_video_file):
        logger.debug("Updating player content")
        self.set_info("Updating player content", 2)
        self.timeline_widget.update_videos_dic(self.videos_dic)
        self.video_player.load_video(concat_video_file, self.first_load)
        if self.first_load:
            self.first_load = False
        self.set_info("Player updated")
        self.load_nexts()

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.main_layout.addWidget(self.menu_bar)
        
        self.player_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Player')
        self.clear_cache_and_reload_action = self.player_action.addAction(QtGui.QIcon(''), "Clear cache")
        self.clear_all_cache_and_reload_action = self.player_action.addAction(QtGui.QIcon(''), "Clear all cache")
        self.show_preferences_action = self.player_action.addAction(QtGui.QIcon(ressources._settings_icon_), "Preferences")
        self.playlist_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, title='Playlist')
        self.clear_playlist_action = self.playlist_action.addAction(QtGui.QIcon(''), "Clear playlist")

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background-color:black;")
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        self.concat_thread.on_concat_ready.connect(self.update_concat)
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
        self.timeline_widget.on_videos_dropped.connect(self.add_videos)
        self.timeline_widget.on_delete.connect(self.delete_videos)
        self.timeline_widget.current_stage.connect(self.current_stage.emit)
        self.clear_cache_and_reload_action.triggered.connect(self.clear_cache_and_reload)
        self.clear_all_cache_and_reload_action.triggered.connect(self.clear_all_cache_and_reload)
        self.show_preferences_action.triggered.connect(self.show_preferences)
        self.clear_playlist_action.triggered.connect(self.clear)

    def order_changed(self, new_order):
        self.videos_dic = dict(sorted(self.videos_dic.items(), key=lambda x: new_order.index(x[0])))
        self.give_concat_job()

    def in_out_modified(self, modification_dic):
        self.videos_dic[modification_dic['id']]['inpoint'] = modification_dic['inpoint']
        self.videos_dic[modification_dic['id']]['outpoint'] = modification_dic['outpoint']
        self.give_concat_job()

    def clear(self):
        self.delete_videos(list(self.videos_dic.keys()))

    def delete_videos(self, video_ids):
        for video_id in video_ids:
            if video_id in self.videos_dic.keys():
                del self.videos_dic[video_id]
        self.give_concat_job()

    def update_frame(self, frame):
        self.timeline_widget.set_frame(frame)

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
        self.fps_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.settings_layout.addRow(QtWidgets.QLabel('Fps'), self.fps_spinbox)

        self.width_spinbox = QtWidgets.QSpinBox()
        self.width_spinbox.setRange(1, 10000)
        self.width_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.height_spinbox = QtWidgets.QSpinBox()
        self.height_spinbox.setRange(1, 10000)
        self.height_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutions_layout = QtWidgets.QHBoxLayout()
        self.resolutions_layout.addWidget(self.width_spinbox)
        self.resolutions_layout.addWidget(self.height_spinbox)
        self.settings_layout.addRow(QtWidgets.QLabel('Resolution'), self.resolutions_layout)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.main_layout.addLayout(self.buttons_layout)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.buttons_layout.addWidget(self.cancel_button)
        self.accept_button = QtWidgets.QPushButton('Accept')
        self.accept_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.accept_button)
'''
app = app_utils.get_app()
player = video_player_widget()
player.set_fps(24)
player.show()
QtWidgets.QApplication.processEvents()

videos = ["D:/SBOX/video_1.mp4",
            "D:/SBOX/video_6.mp4",
            "D:/SBOX/video_1.mp4",
            "D:/SBOX/video_6.mp4",
            "D:/SBOX/video_1.mp4",
            "D:/SBOX/video_6.mp4",
            "D:/SBOX/video_1.mp4",
            "D:/SBOX/video_6.mp4",
            "D:/SBOX/video_1.mp4",
            "D:/SBOX/video_6.mp4",
            "D:/SBOX/video_3.mp4",
            "D:/SBOX/video_4.mp4",
            "D:/SBOX/video_5.mp4",
            "D:/SBOX/video_3.mp4",
            "D:/SBOX/video_4.mp4",
            "D:/SBOX/video_5.mp4"]
#videos=[]
#for a in range(0,100):
#    videos.append(f"videos/{a}.mp4")

#for video in videos:
#    player.add_video(video)
#player.clear_all_proxys()
#player.hard_clear_proxys()
player.check_proxys_soft()
player.give_concat_job()
player.load_nexts()

sys.exit(app.exec_())
'''