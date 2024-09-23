# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
import uuid
import ffmpeg
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import logging
import time

# Wizard gui modules
from wizard.gui.video_manager import slider_view

logger = logging.getLogger(__name__)

def get_video_length(video_path):
    probe = ffmpeg.probe(video_path)
    duration = round(float(probe['format']['duration'])*1000)
    return duration

def get_video_fps(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    frame_rate = video_stream['r_frame_rate']
    if '/' in frame_rate:
        numerator, denominator = map(int, frame_rate.split('/'))
        fps = numerator / denominator
    else:
        fps = float(frame_rate)
    return fps

class infos_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.setObjectName('video_info_widget')
        self.setStyleSheet("#video_info_widget{background-color:transparent;}")

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('video_info_widget_content')
        self.content_widget.setStyleSheet("#video_info_widget_content{background-color:rgba(10,10,20,100);}")
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.frame_label = QtWidgets.QLabel('')
        self.frame_label.setFixedWidth(50)
        self.content_layout.addWidget(self.frame_label)

        self.time_label = QtWidgets.QLabel('')
        self.time_label.setFixedWidth(50)
        self.content_layout.addWidget(self.time_label)

        self.fps_label = QtWidgets.QLabel('')
        self.fps_label.setFixedWidth(50)
        self.content_layout.addWidget(self.fps_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.current_video_label = QtWidgets.QLabel('')
        self.content_layout.addWidget(self.current_video_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

    def set_frame(self, frame):
        self.frame_label.setText(f"F{frame}")

    def set_time(self, position):
        self.time_label.setText(f"{round(position/1000, 2)}s")

    def set_fps(self, fps):
        self.fps_label.setText(f"{fps} Fps")

    def set_current_video(self, video):
        self.current_video_label.setText(f"{video}")

class video_output(QtWidgets.QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.video_item = QtMultimediaWidgets.QGraphicsVideoItem()
        self.view = QtWidgets.QGraphicsView()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QColor("black"))
        self.view.setScene(self.scene)
        self.scene.addItem(self.video_item)

        self.media_player = media_player
        self.media_player.setVideoOutput(self.video_item)

        self.main_layout.addWidget(self.view)

    def resizeEvent(self, event):
        rect = QtCore.QRectF(self.view.contentsRect())
        self.scene.setSceneRect(rect)
        self.video_item.setSize(rect.size())

class video_player(QtWidgets.QWidget):

    end_reached = pyqtSignal(int)
    playing_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.media_player = QtMultimedia.QMediaPlayer()

        self.video_output = video_output(self.media_player)
        self.timeline_widget = timeline_widget()

        self.video = None
        self.duration = 0
        self.fps = 24.0
        self.total_frames = 0
        self.is_video_loaded = False
        self.next_index = 0
        self.frame = 0
        self.playing = False

        self.build_ui()
        self.connect_functions()

    def resizeEvent(self, event):
        self.infos_widget.resize(self.video_surface.size())
        super().resizeEvent(event)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.video_surface = QtWidgets.QWidget()
        self.video_surface.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.video_surface_layout = QtWidgets.QVBoxLayout()
        self.video_surface_layout.setContentsMargins(0,0,0,0)
        self.video_surface.setLayout(self.video_surface_layout)
        self.main_layout.addWidget(self.video_surface)
        self.video_surface_layout.addWidget(self.video_output)

        self.infos_widget = infos_widget(self.video_surface)

        self.main_layout.addWidget(self.timeline_widget)
        
    def connect_functions(self):
        self.media_player.positionChanged.connect(self.position_changed)
        self.timeline_widget.seek.connect(self.seek)

    def seek(self, frame):
        if self.media_player.duration() == 0:
            return
        if frame > self.total_frames:
            return
        if frame < 0:
            return
        time = round(((frame+0.2)/self.fps)*1000)
        self.media_player.setPosition(time)

    def load_video(self, video):
        if video == '':
            self.video = None
            self.media_player.setSource(QtCore.QUrl.fromLocalFile(''))
            self.infos_widget.set_current_video('')
            return
        if self.video != video:
            self.video = video
            self.duration = get_video_length(video)
            self.fps = get_video_fps(video)
            self.total_frames = round(self.fps * (self.duration/1000))-1
            self.media_player.setSource(QtCore.QUrl.fromLocalFile(video))
            self.timeline_widget.set_range(0, self.total_frames)
            self.infos_widget.set_fps(self.fps)
            self.infos_widget.set_current_video(self.video)
            self.media_player.play()
            self.media_player.pause()
        self.media_player.setPosition(0)
        self.position_changed(0)
        if self.playing is True:
            self.media_player.play()
        else:
            self.media_player.pause()

    def ensure_frame(self):
        frame = round(((self.media_player.position() - (0.2*(1/self.fps*1000))) / 1000) * self.fps)
        self.seek(frame)

    def toggle_play_pause(self):
        if self.playing == True:
            self.media_player.pause()
            self.ensure_frame()
            self.playing = False
            self.playing_signal.emit(self.playing)
        else:
            if not self.video:
                return
            self.media_player.play()
            self.playing = True
            self.playing_signal.emit(self.playing)

    def next_frame(self):
        frame = round(((self.media_player.position() - (0.2*(1/self.fps*1000))) / 1000) * self.fps)
        self.seek(frame+1)  
    
    def previous_frame(self):
        frame = round(((self.media_player.position() - (0.2*(1/self.fps*1000))) / 1000) * self.fps)
        self.seek(frame-1)  

    def position_changed(self, position):
        if (position >= self.duration-int(1/self.fps*1000)) and self.playing:
            self.media_player.pause()
            self.end_reached.emit(1)
        frame = round(((position - (0.2*(1/self.fps*1000))) / 1000) * self.fps)
        self.frame = frame
        self.timeline_widget.set_frame(frame)
        self.infos_widget.set_frame(frame)
        self.infos_widget.set_time(position)

class timeline_widget(QtWidgets.QWidget):

    seek = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.ignore_seek = False
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.slider_view = slider_view.timeline_viewport()
        self.main_layout.addWidget(self.slider_view)

    def connect_functions(self):
        self.slider_view.signal_manager.on_seek.connect(self.send_seek)

    def send_seek(self, value):
        self.seek.emit(value)

    def set_frame(self, frame):
        self.slider_view.set_frame(frame)

    def set_range(self, start, end):
        self.slider_view.set_frame_range([start, end])
