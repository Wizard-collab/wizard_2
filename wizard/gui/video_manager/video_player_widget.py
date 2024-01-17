# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import traceback
import time
import os
os.environ["PATH"] = os.path.abspath('') + os.pathsep + os.environ["PATH"]
import mpv
import logging

logger = logging.getLogger(__name__)

class video_player_widget(QtWidgets.QWidget):

    on_progress = pyqtSignal(int)
    on_play_toggle = pyqtSignal(int)

    def __init__(self, parent=None):
        super(video_player_widget, self).__init__(parent)

        self.update_ui_progress = True
        self.apply_seek = True
        self.frame = 0
        self.fps = 24
        self.playing = False
        self.loop = False
        self.mouse_pos = None

        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(QtCore.Qt.WA_NativeWindow)

        self.create_mpv_player()

        self.timer = QtCore.QTimer(self)
        self.timer.start(int(1/self.fps*1000))
        self.timer.timeout.connect(self.listen_progress)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            x_delta = event.pos().x() - self.mouse_pos.x()
            percent = x_delta/self.width()
            self.seek_relative_percent(percent)
            self.mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None

    def create_mpv_player(self):
        self.player = mpv.MPV(wid=str(int(self.winId())), keep_open='always')

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
        self.update_ui_progress = True

    def seek_relative(self, value):
        if not self.apply_seek:
            return

        self.update_ui_progress = False
        self.player.seek(value, reference="relative", precision="exact")
        self.update_ui_progress = True

    def seek_relative_percent(self, value):
        if not self.apply_seek:
            return

        t_value = self.player.duration*value
        abs_percent = (self.player.time_pos + t_value)/self.player.duration
        frame = round(abs_percent * self.get_total_frames())
        if frame == self.frame:
            return
        if frame < 0:
            return
        if frame > self.get_total_frames():
            return

        self.update_ui_progress = False
        self.player.seek(t_value, reference="relative", precision="exact")
        self.update_ui_progress = True

    def next_frame(self):
        self.player.frame_step()

    def previous_frame(self):
        self.player.frame_back_step()
