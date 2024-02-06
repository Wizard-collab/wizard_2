from PyQt5.QtCore import pyqtSignal
import traceback
import sys
import uuid
import time
import logging

# Wizard core modules
from wizard.core import project

# Wizard gui modules
from wizard.gui.video_manager import video_player_widget

logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class video_manager(metaclass=Singleton):
	def __init__(self, parent=None):
		self.players_dic = dict()

	def get_instance(self):
		instance = video_player_widget.video_player_widget()
		instance.set_fps(project.get_frame_rate())
		instance.set_resolution(project.get_image_format())
		instance_id = instance.player_id
		self.players_dic[instance_id] = instance
		return instance
