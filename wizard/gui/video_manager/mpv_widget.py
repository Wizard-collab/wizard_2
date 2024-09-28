
# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import traceback
import time
import os
os.environ["PATH"] = os.path.abspath('') + os.pathsep + os.environ["PATH"]
import mpv
import logging

logger = logging.getLogger(__name__)

class mpv_widget(QtWidgets.QWidget):

    on_progress = pyqtSignal(int)
    on_frame_range_modified = pyqtSignal(list)
    on_play_toggle = pyqtSignal(int)

    def __init__(self, parent=None):
        super(mpv_widget, self).__init__(parent)

        self.update_ui_progress = True
        self.apply_seek = True
        self.frame = 0
        self.fps = 24
        self.playing = False
        self.loop = False
        self.mouse_pos = None
        self.bounds_range = [0,1000]

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NativeWindow)

        self.player = None
        self.create_mpv_player()

        self.timer = QtCore.QTimer(self)
        self.timer.start(int(1/self.fps*500))
        self.timer.timeout.connect(self.listen_progress)

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range

    def toggle_loop(self, loop):
        self.loop = loop

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None

    def create_mpv_player(self):
        if self.player:
            del self.player
        self.player = mpv.MPV(wid=str(int(self.winId())), keep_open='always')

    def quit(self):
        self.timer.stop()
        self.player.terminate()

    def load_video(self, video_file, first_load=False):
        if video_file is None or not os.path.isfile(video_file):
            self.player.stop()
            return
        self.force_pause()
        pos = self.player.time_pos
        if first_load:
            pos = 0
            pause = True
        self.player.play(video_file)
        MPV_EVENT_FILE_LOADED = 8
        self.player.wait_for_event(MPV_EVENT_FILE_LOADED)
        
        if pos is not None:
            self.seek(pos, force=True)
        
        self.update_frame_range()

    def update_frame_range(self):
        self.on_frame_range_modified.emit([0, round(self.player.duration*self.fps)-1])

    def force_pause(self):
        if not self.player.pause:
            self.player.command('cycle', 'pause')
            self.pause = self.player.pause
            self.on_play_toggle.emit(not self.pause)

    def force_play(self):
        if self.player.pause:
            self.player.command('cycle', 'pause')
            self.pause = self.player.pause
            self.on_play_toggle.emit(not self.pause)

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

            time_pos = self.player.time_pos
            if time_pos is None:
                return

            frame = round(time_pos*self.fps)

            if frame == self.frame:
                return

            self.frame = frame
            self.apply_seek = False
            self.on_progress.emit(frame)
            self.apply_seek = True

            if frame >= self.bounds_range[1] and not self.player.pause:
                self.force_pause()
                QtWidgets.QApplication.processEvents()
                time.sleep(1/self.fps)
                QtWidgets.QApplication.processEvents()
                if self.loop:
                    self.seek_frame(self.bounds_range[0])
                    self.force_play()

        except mpv.ShutdownError:
            self.timer.stop()

    def play_pause_toggle(self):
        if not self.player.duration:
            return

        if self.frame >= self.bounds_range[1] and self.player.pause:
            self.seek_frame(self.bounds_range[0])

        self.player.command('cycle', 'pause')
        self.pause = self.player.pause
        self.on_play_toggle.emit(not self.pause)

    def seek(self, value, force=False):
        if not self.apply_seek:
            return

        if not self.player.duration:
            return

        frame = round(value * self.fps)
        if frame > self.bounds_range[1]:
            self.seek_frame(self.bounds_range[0])
            return
        if frame < self.bounds_range[0]:
            self.seek_frame(self.bounds_range[1])
            return
        if frame == self.frame and not force:
            return

        self.update_ui_progress = False
        self.player.seek(value, reference="absolute", precision="exact")
        self.update_ui_progress = True

    def seek_frame(self, frame):
        if not self.apply_seek:
            return

        if not self.player.duration:
            return

        t_value = frame/self.fps
        if frame > self.bounds_range[1]:
            self.seek_frame(self.bounds_range[0])
            return
        if frame < self.bounds_range[0]:
            self.seek_frame(self.bounds_range[1])
            return

        self.update_ui_progress = False
        self.player.seek(t_value, reference="absolute", precision="exact")
        self.update_ui_progress = True

    def seek_relative(self, value):
        if not self.apply_seek:
            return

        if not self.player.duration:
            return

        t_value = self.player.time_pos + value
        frame = t_value*self.fps
        if frame > self.bounds_range[1]:
            self.seek_frame(self.bounds_range[0])
            return
        if frame < self.bounds_range[0]:
            self.seek_frame(self.bounds_range[1])
            return

        self.update_ui_progress = False
        self.player.seek(value, reference="relative", precision="exact")
        self.update_ui_progress = True

    def seek_relative_percent(self, value):
        if not self.apply_seek:
            return

        if not self.player.duration:
            return

        t_value = self.player.duration*value
        abs_percent = (self.player.time_pos + t_value)/self.player.duration
        frame = round(abs_percent * self.get_total_frames())
        if frame == self.frame:
            return
        if frame < 0:
            return
        if frame >= self.bounds_range[1]:
            self.seek_frame(self.bounds_range[0])
            return
        if frame < self.bounds_range[0]:
            self.seek_frame(self.bounds_range[1])
            return

        self.update_ui_progress = False
        self.player.seek(t_value, reference="relative", precision="exact")
        self.update_ui_progress = True

    def seek_end(self):
        if not self.player.duration:
            return
        self.seek_frame(self.bounds_range[1])

    def seek_beginning(self):
        if not self.player.duration:
            return
        self.seek_frame(self.bounds_range[0])

    def next_frame(self):
        if self.frame + 1 > self.bounds_range[1]:
            self.seek_frame(self.bounds_range[0])
            return
        self.seek_frame(self.frame + 1)

    def previous_frame(self):
        if self.frame - 1 < self.bounds_range[0]:
            self.seek_frame(self.bounds_range[1])
            return
        self.seek_frame(self.frame - 1)
