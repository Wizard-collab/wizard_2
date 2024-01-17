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
import os
os.environ["PATH"] = os.path.abspath('') + os.pathsep + os.environ["PATH"]
import mpv
import logging

# Wizard core modules
from wizard.core import path_utils
from wizard.core.video_player import ffmpeg_utils

# Wizard gui modules
from wizard.gui import app_utils

logger = logging.getLogger(__name__)

class video_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_manager_widget, self).__init__(parent)
        self.load_video_threads = []
        self.temp_dir = 'temp'
        self.videos_dic = dict()
        self.load_threads = []
        self.playing_infos_widget = playing_infos_widget(self)
        self.video_player = video_player(self)
        self.first_load = True
        self.build_ui()
        self.connect_functions()
        self.set_fps()

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.video_player.quit()
        for thread in self.load_video_threads:
            thread.on_video_ready.disconnect()
            thread.kill()
            thread.wait()

    def set_fps(self, fps=24):
        self.fps=fps
        self.video_player.set_fps(fps)
        self.playing_infos_widget.update_fps(self.fps)

    def clear_proxys(self):
        ffmpeg_utils.clear_proxys(self.temp_dir)

    def add_video(self, video_file):
        video_id = str(uuid.uuid4())
        self.videos_dic[video_id] = dict()
        self.videos_dic[video_id]['original_file'] = video_file
        self.videos_dic[video_id]['name'] = path_utils.basename(video_file)
        self.videos_dic[video_id]['frames_count'] = ffmpeg_utils.get_frames_count(video_file)
        self.videos_dic[video_id]['proxy'] = False
        thread = create_proxy_thread(video_id, self.temp_dir, video_file, self.fps, self)
        thread.on_video_ready.connect(self.video_loaded)
        thread.start()
        self.load_video_threads.append(thread)

    def video_loaded(self, video_file):
        self.videos_dic[video_file]['proxy'] = True
        self.concat_videos()

    def concat_videos(self):
        start_time = time.monotonic()
        concat_video_file = ffmpeg_utils.concatenate_videos(self.temp_dir, self.videos_dic, self.fps)
        self.update_concat(concat_video_file)
        print(f"concat creation and update : {time.monotonic()-start_time}")

    def update_concat(self, concat_video_file):
        self.video_player.load_video(concat_video_file, self.first_load)
        if self.first_load:
            self.first_load = False

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.playing_infos_widget)

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background-color:black;")
        self.container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.container_layout = QtWidgets.QHBoxLayout()
        self.container_layout.setContentsMargins(0,0,0,0)
        self.container.setLayout(self.container_layout)
        self.main_layout.addWidget(self.container)

        self.container_layout.addWidget(self.video_player)

    def connect_functions(self):
        self.video_player.on_progress.connect(self.playing_infos_widget.update_frame)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.video_player.play_pause_toggle()
        if event.key() == QtCore.Qt.Key_Left:
            self.video_player.previous_frame()
        if event.key() == QtCore.Qt.Key_Right:
            self.video_player.next_frame()

class create_proxy_thread(QtCore.QThread):

    on_video_ready = pyqtSignal(str)

    def __init__(self, video_id, temp_dir, video_file, output_frame_rate=24, parent=None):
        super(create_proxy_thread, self).__init__(parent)
        self.video_id = video_id
        self.temp_dir = temp_dir
        self.video_file = video_file
        self.output_frame_rate = output_frame_rate
        self.create_proxy_object = None

    def run(self):
        start_time = time.monotonic()
        self.create_proxy_object = ffmpeg_utils.create_proxy(self.temp_dir, self.video_file, self.output_frame_rate)
        self.create_proxy_object.wait_for_process()
        self.on_video_ready.emit(self.video_id)
        print(f"proxy creation {self.video_file} : {time.monotonic()-start_time}")

    def kill(self):
        if not self.create_proxy_object:
            return
        self.create_proxy_object.kill()
        self.quit()

class playing_infos_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(playing_infos_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(3,3,3,3)
        self.setLayout(self.main_layout)

        self.frame_info_label = QtWidgets.QLabel("Frame :")
        self.frame_info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.frame_info_label)

        self.frame_label = QtWidgets.QLabel('0')
        self.main_layout.addWidget(self.frame_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.fps_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.fps_label)

    def update_frame(self, frame):
        self.frame_label.setText(f"{frame}")

    def update_fps(self, fps):
        self.fps_label.setText(f"{fps} fps")

class video_player(QtWidgets.QWidget):

    on_progress = pyqtSignal(int)
    on_play_toggle = pyqtSignal(int)

    def __init__(self, parent=None):
        super(video_player, self).__init__(parent)

        self.update_ui_progress = True
        self.apply_seek = True
        self.frame = 0
        self.fps = 24
        self.playing = False
        self.loop = False

        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(QtCore.Qt.WA_NativeWindow)
        self.player = mpv.MPV(wid=str(int(self.winId())), keep_open='always')

        self.timer = QtCore.QTimer(self)
        self.timer.start(int(1/self.fps*1000))
        self.timer.timeout.connect(self.listen_progress)

    def quit(self):
        self.player.terminate()
        self.timer.stop()

    def load_video(self, video_file, first_load=False):
        pos = self.player.time_pos
        pause = self.player.pause
        if first_load:
            pos = 0
            pause = True
        self.player.loadfile(video_file)
        MPV_EVENT_FILE_LOADED = 8
        self.player.wait_for_event(MPV_EVENT_FILE_LOADED)
        if pos is not None:
            self.seek(pos)
        if self.player.pause != pause:
            self.player.command('cycle', 'pause')

    def force_pause(self):
        if not self.player.pause:
            self.player.command('cycle', 'pause')

    def set_fps(self, fps):
        self.fps = fps

    def get_total_frames(self):
        duration = self.player.duration
        if not duration:
            return
        return round(duration*self.fps)

    def listen_progress(self):
        try:
            if not self.update_ui_progress:
                return
            
            duration = self.player.duration
            time_pos = self.player.time_pos

            if (duration is None) or (time_pos is None):
                return

            current_position = time_pos / duration
            frame = round(current_position*self.get_total_frames())

            if frame == self.get_total_frames()-1:
                if self.loop:
                    self.seek(0)

            if frame == self.frame:
                return

            self.frame = frame
            self.apply_seek = False
            self.on_progress.emit(frame)
            self.apply_seek = True
        except mpv.ShutdownError:
            self.timer.stop()

    def play_pause_toggle(self):
        total_frames = self.get_total_frames()
        if not total_frames:
            return
        if self.frame == self.get_total_frames()-1 and self.player.pause:
            self.seek(0)

        self.player.command('cycle', 'pause')
        self.playing = self.player.pause
        self.on_play_toggle.emit(self.playing)

    def seek(self, value):
        if not self.apply_seek:
            return

        frame = round(value * self.get_total_frames())
        if frame == self.frame:
            return

        self.update_ui_progress = False
        self.player.seek(value, reference="absolute", precision="exact")
        self.frame = frame
        self.update_ui_progress = True

    def next_frame(self):
        self.player.frame_step()

    def previous_frame(self):
        self.player.frame_back_step()
'''

app = app_utils.get_app()
player = video_manager_widget()
#player.clear_proxys()
player.set_fps(24)
player.show()
QtWidgets.QApplication.processEvents()

temp_dir = 'temp'
videos = ["video_1.mp4",
            "video_5.mp4"]
            #"video_4.mp4",
            #"video_2.mp4",
            #"video_3.mp4"]
            #"video_4.mp4",
            #"video_5.mp4"]


for video in videos:
    player.add_video(video)

sys.exit(app.exec_())
'''