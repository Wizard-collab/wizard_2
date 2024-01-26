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
from wizard.core import project
from wizard.core.video_player import ffmpeg_utils

# Wizard gui modules
from wizard.gui import app_utils
from wizard.gui.video_manager import video_player_widget
from wizard.gui.video_manager import video_threads
from wizard.gui.video_manager import timeline_widget

logger = logging.getLogger(__name__)

class video_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_manager_widget, self).__init__(parent)
        self.load_video_threads = dict()
        self.player_id = str(uuid.uuid4())
        self.temp_dir = ffmpeg_utils.get_temp_dir()
        self.videos_dic = dict()
        self.load_threads = []
        self.frame_range = [0,1000]
        self.resolution = [1920,1080]
        self.concat_thread = video_threads.concat_thread(self.temp_dir, self.player_id, self)
        self.video_player = video_player_widget.video_player_widget(self)
        self.timeline_widget = timeline_widget.timeline_widget(self)
        self.first_load = True
        self.build_ui()
        self.connect_functions()
        #self.set_fps(project.get_frame_rate())
        #self.set_resolution(project.get_image_format())
        self.set_fps(24)
        self.set_resolution([1920,1080])

    def need_player(self):
        self.video_player.create_mpv_player()

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.video_player.quit()
        ffmpeg_utils.clear_player_files(self.temp_dir, self.player_id)
        for video_id in self.load_video_threads.keys():
            self.kill_and_delete_proxy_thread(video_id)
        self.concat_thread.quit()

    def kill_and_delete_proxy_thread(self, video_id):
        if video_id not in self.load_video_threads.keys():
            return
        self.load_video_threads[video_id].on_video_ready.disconnect()
        self.load_video_threads[video_id].kill()
        self.load_video_threads[video_id].wait()
        del self.load_video_threads[video_id]

    def set_fps(self, fps=24):
        self.fps=fps
        self.video_player.set_fps(fps)
        self.timeline_widget.set_fps(fps)
        self.concat_thread.set_fps(fps)

    def set_resolution(self, resolution=[1920,1080]):
        self.resolution = resolution

    def clear_all_proxys(self):
        for video_id in self.videos_dic.keys():
            self.clear_proxy(self.videos_dic[video_id]['original_file'])
            self.videos_dic[video_id]['proxy'] = False
            self.timeline_widget.update_videos_dic(self.videos_dic)

    def clear_proxy(self, original_file):
        ffmpeg_utils.delete_proxy(self.temp_dir, original_file)

    def hard_clear_proxys(self):
        ffmpeg_utils.hard_clear_proxys(self.temp_dir)

    def add_video(self, video_file):
        video_id = str(uuid.uuid4())
        self.videos_dic[video_id] = dict()
        self.videos_dic[video_id]['original_file'] = path_utils.abspath(video_file)
        self.videos_dic[video_id]['name'] = path_utils.basename(video_file)
        self.videos_dic[video_id]['frames_count'] = ffmpeg_utils.get_frames_count(video_file)
        self.videos_dic[video_id]['inpoint'] = 0
        self.videos_dic[video_id]['outpoint'] = self.videos_dic[video_id]['frames_count']/24
        self.videos_dic[video_id]['proxy'] = False
        self.videos_dic[video_id]['thumbnail'] = None

    def check_proxys_soft(self):
        for video_id in self.videos_dic.keys():
            self.videos_dic[video_id]['proxy'] = ffmpeg_utils.check_if_proxy_exists(self.temp_dir, self.videos_dic[video_id]['original_file'])
            self.videos_dic[video_id]['thumbnail'] = ffmpeg_utils.check_if_thumbnail_exists(self.temp_dir, self.videos_dic[video_id]['original_file'])

    def videos_dropped(self, videos_list):
        for video_path in videos_list:
            self.add_video(video_path)
        self.check_proxys_soft()
        self.concat_thread.give_job(self.videos_dic)
        self.load_next()

    def load_next(self):
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id]['proxy']:
                continue
            thread = video_threads.create_proxy_thread(video_id,
                                                        self.temp_dir,
                                                        self.videos_dic[video_id]['original_file'],
                                                        self.resolution,
                                                        self.fps,
                                                        self)
            thread.on_video_ready.connect(self.video_loaded)
            thread.start()
            self.load_video_threads[video_id] = thread
            break

    def video_loaded(self, video_id):
        for other_video_id in self.videos_dic.keys():
            if self.videos_dic[other_video_id]['original_file'] == self.videos_dic[video_id]['original_file']:
                self.videos_dic[other_video_id]['proxy'] = True
                self.videos_dic[other_video_id]['thumbnail'] = ffmpeg_utils.get_thumbnail_path(self.temp_dir, self.videos_dic[video_id]['original_file'])
        self.kill_and_delete_proxy_thread(video_id)
        self.timeline_widget.update_videos_dic(self.videos_dic)
        self.concat_thread.give_job(self.videos_dic)

    def update_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.timeline_widget.set_frame_range(frame_range)

    def update_concat(self, concat_video_file):
        self.timeline_widget.update_videos_dic(self.videos_dic)
        self.video_player.load_video(concat_video_file, self.first_load)
        if self.first_load:
            self.first_load = False
        self.load_next()

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background-color:black;")
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.container_layout = QtWidgets.QHBoxLayout()
        self.container_layout.setContentsMargins(0,0,0,0)
        self.container.setLayout(self.container_layout)
        self.main_layout.addWidget(self.container)

        self.container_layout.addWidget(self.video_player)
        self.main_layout.addWidget(self.timeline_widget)

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
        self.timeline_widget.on_videos_dropped.connect(self.videos_dropped)

    def order_changed(self, new_order):
        self.videos_dic = dict(sorted(self.videos_dic.items(), key=lambda x: new_order.index(x[0])))
        self.concat_thread.give_job(self.videos_dic)

    def in_out_modified(self, modification_dic):
        self.videos_dic[modification_dic['id']]['inpoint'] = modification_dic['inpoint']
        self.videos_dic[modification_dic['id']]['outpoint'] = modification_dic['outpoint']
        self.concat_thread.give_job(self.videos_dic)

    def update_frame(self, frame):
        self.timeline_widget.set_frame(frame)
'''

app = app_utils.get_app()
player = video_manager_widget()
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
player.hard_clear_proxys()
player.check_proxys_soft()
player.load_next()

sys.exit(app.exec_())
'''