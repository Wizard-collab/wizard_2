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

logger = logging.getLogger(__name__)

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
        logger.debug(f"proxy creation {self.video_file} : {time.monotonic()-start_time}")

    def kill(self):
        if not self.create_proxy_object:
            return
        self.create_proxy_object.kill()
        self.quit()

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
        is_at_least_on_proxy = False
        for video_id in videos_dic.keys():
            if videos_dic[video_id]['proxy']:
                is_at_least_on_proxy = True
                break
        if not is_at_least_on_proxy:
            return
        self.to_concat.append(videos_dic)
        if not self.running:
            self.start()

    def run(self):
        self.running = True
        while self.to_concat != []:
            concat_video_file = ffmpeg_utils.concatenate_videos(self.temp_dir, self.player_id, self.to_concat[0], self.fps)
            self.on_concat_ready.emit(concat_video_file)
            self.to_concat.pop(0)
        self.running = False