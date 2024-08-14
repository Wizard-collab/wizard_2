# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import uuid

# Wizard core modules
from wizard.core import project

class timeline_widget(QtWidgets.QWidget):

	load_video = pyqtSignal(str)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.videos_dic = dict()
		self.build_ui()

	def build_ui(self):
		self.main_layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.main_layout)

	def add_videos(self, video_ids):
		for video_id in video_ids:
			self.add_video(video_id)

	def add_video(self, video_id):
		unique_id = uuid.uuid4()
		self.videos_dic[unique_id] = dict()
		self.videos_dic[unique_id]['video_id'] = video_id
		self.videos_dic[unique_id]['video_path'] = project.get_video_data(video_id, 'file_path')
		self.videos_dic[unique_id]['item'] = video_item()
		self.main_layout.addWidget(self.videos_dic[unique_id]['item'])

		if len(self.videos_dic.keys()) == 1:
			self.load_video.emit(self.videos_dic[unique_id]['video_path'])

class video_item(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.build_ui()

	def build_ui(self):
		self.main_layout = QtWidgets.QVBoxLayout()
		self.setLayout(self.main_layout)
		self.main_layout.addWidget(QtWidgets.QLabel("ergregerge"))
		self.setStyleSheet('background-color:red;')