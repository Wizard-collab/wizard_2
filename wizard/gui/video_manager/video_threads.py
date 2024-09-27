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

# Wizard core modules
from wizard.core import path_utils
from wizard.core import ffmpeg_utils

logger = logging.getLogger(__name__)

class concat_thread(QtCore.QThread):

    on_concat_ready = pyqtSignal(str)

    def __init__(self, temp_dir, player_id, parent=None):
        super(concat_thread, self).__init__(parent)
        self.temp_dir = temp_dir
        self.player_id = player_id
        self.fps = 24
        self.to_concat = []
        self.running = False

    def set_fps(self, fps):
        self.fps = fps

    def set_temp_dir(self, temp_dir):
        self.temp_dir = temp_dir

    def give_job(self, videos_dic):
        self.to_concat.append(videos_dic)
        if not self.running:
            self.start()

    def run(self):
        try:
            self.running = True
            while self.to_concat != []:
                logger.debug(f"Creating concat file")
                concat_video_file = ffmpeg_utils.concatenate_videos(self.temp_dir, self.player_id, self.to_concat[0], self.fps)
                self.on_concat_ready.emit(concat_video_file)
                self.to_concat.pop(0)
            self.running = False
        except:
            logger.error(str(traceback.format_exc()))