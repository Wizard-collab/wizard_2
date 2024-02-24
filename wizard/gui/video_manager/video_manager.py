# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard core modules
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui.video_manager import video_player_widget
from wizard.gui.video_manager import video_browser_widget
from wizard.gui.video_manager import video_history_widget
from wizard.gui import asset_tracking_widget

logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class video_player_instances(metaclass=Singleton):
    def __init__(self, parent=None):
        self.players_dic = dict()

    def get_instance(self, parent=None):
        instance = video_player_widget.video_player_widget(parent)
        instance.set_fps(project.get_frame_rate())
        instance.set_resolution(project.get_image_format())
        instance_id = instance.player_id
        self.players_dic[instance_id] = instance
        return instance

class video_manager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_manager, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Video manager")

        self.video_browser = video_browser_widget.video_browser_widget()
        self.asset_tracking_widget = asset_tracking_widget.asset_tracking_widget()
        self.video_history_widget = video_history_widget.video_history_widget()
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.video_browser.add_videos.connect(self.add_videos)
        self.video_browser.clear_playlist.connect(self.video_player.clear)
        self.video_player.current_stage.connect(self.asset_tracking_widget.change_stage)
        self.video_player.current_variant.connect(self.video_history_widget.change_variant)

    def add_videos(self, video_tuples):
        for video_tuple in video_tuples:
            self.video_player.add_video(video_file=video_tuple[0], project_video_id=video_tuple[1])
        self.video_player.check_proxys_soft()
        self.video_player.give_concat_job()
        self.video_player.load_nexts()

    #def closeEvent(self, event):
    #    self.hide()
    #    event.ignore()

    def refresh(self):
        self.video_browser.refresh()
        self.asset_tracking_widget.refresh()
        self.video_player.refresh()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.content_widget = gui_utils.QSplitter()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_widget.setObjectName('main_widget')
        self.main_layout.addWidget(self.content_widget)

        self.content_widget.addWidget(self.video_browser)
        self.video_player = video_player_instances().get_instance(self)
        self.content_widget.addWidget(self.video_player)

        self.content_2_widget = gui_utils.QSplitter()
        self.content_2_widget.setOrientation(QtCore.Qt.Vertical)
        self.content_widget.addWidget(self.content_2_widget)

        self.content_2_widget.addWidget(self.asset_tracking_widget)
        self.content_2_widget.addWidget(self.video_history_widget)
