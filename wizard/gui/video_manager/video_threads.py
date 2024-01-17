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

class create_proxy_thread(QtCore.QThread):

    on_video_ready = pyqtSignal(str)

    def __init__(self, video_id, temp_dir, video_file, resolution=[1920,1080], fps=24, parent=None):
        super(create_proxy_thread, self).__init__(parent)
        self.video_id = video_id
        self.temp_dir = temp_dir
        self.video_file = video_file
        self.resolution = resolution
        self.fps = fps
        self.create_proxy_object = None

    def run(self):
        start_time = time.monotonic()
        self.create_proxy_object = ffmpeg_utils.create_proxy(self.temp_dir, self.video_file, self.resolution, self.fps)
        self.create_proxy_object.wait_for_process()
        self.create_proxy_object.process_finished()
        self.on_video_ready.emit(self.video_id)
        print(f"proxy creation {self.video_file} : {time.monotonic()-start_time}")

    def kill(self):
        if not self.create_proxy_object:
            return
        self.create_proxy_object.kill()
        self.quit()