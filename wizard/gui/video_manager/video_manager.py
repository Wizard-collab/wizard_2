# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import pyqtSignal
import logging

# Wizard core modules
from wizard.core import project
from wizard.core import user
from wizard.vars import ressources
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui.video_manager import video_browser_widget
from wizard.gui.video_manager import playlist_browser_widget
from wizard.gui.video_manager import video_history_widget
from wizard.gui.video_manager import video_player
from wizard.gui.video_manager import timeline_widget
from wizard.gui import asset_tracking_widget

logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class video_manager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_manager, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Video manager")

        self.video_browser = video_browser_widget.video_browser_widget()
        self.video_player = video_player.video_player()
        self.playlist_browser = playlist_browser_widget.playlist_browser_widget()
        self.asset_tracking_widget = asset_tracking_widget.asset_tracking_widget()
        self.video_history_widget = video_history_widget.video_history_widget()
        self.timeline_widget = timeline_widget.timeline_widget()
        self.buttons_bar_widget = timeline_widget.buttons_bar_widget()
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.video_browser.add_videos.connect(self.timeline_widget.add_videos)
        self.video_browser.create_playlist_and_add_videos.connect(self.timeline_widget.create_playlist_and_add_videos)
        self.timeline_widget.load_video.connect(self.video_player.load_video)
        self.video_player.end_reached.connect(self.timeline_widget.play_next)
        self.video_player.playing_signal.connect(self.buttons_bar_widget.set_play_pause)
        self.buttons_bar_widget.on_play_pause.connect(self.video_player.toggle_play_pause)
        self.buttons_bar_widget.on_loop_toggle.connect(self.timeline_widget.set_loop)
        self.timeline_widget.current_stage.connect(self.asset_tracking_widget.change_stage)
        self.timeline_widget.current_video_row.connect(self.video_history_widget.change_video_row)
        self.video_history_widget.replace_current_video.connect(self.timeline_widget.replace_video)
        self.playlist_browser.load_playlist.connect(self.timeline_widget.load_playlist)

    def create_playlist_from_stages(self, stages_ids_list):
        videos = []
        for stage_id in stages_ids_list:
            variants_ids = project.get_stage_childs(stage_id, 'id')
            for variant_id in variants_ids:
                video_rows = project.get_videos(variant_id)
                if len(video_rows) == 0:
                    continue
                videos.append(video_rows[-1]['id'])
        self.timeline_widget.create_playlist_and_add_videos(videos)
        if len(videos) == 0:
            logger.warning("No videos found")
        self.show()
        self.raise_()

    def show_single_video(self, video_id):
        self.timeline_widget.create_playlist_and_add_videos([video_id])
        self.show()
        self.raise_()
        
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Space:
            self.video_player.toggle_play_pause()
        if event.key() == QtCore.Qt.Key.Key_C:
            self.video_player.previous_frame()
        if event.key() == QtCore.Qt.Key.Key_V:
            self.video_player.next_frame()

    def get_context(self):
        self.asset_tracking_widget.get_context()
        self.playlist_browser.get_context()
        self.timeline_widget.get_context()
        
        context_dic = user.user().get_context(user_vars._video_manager_context_)
        if context_dic is None:
            return
        if 'current_tab' in context_dic.keys():
            self.tabs_widget.setCurrentIndex(context_dic['current_tab'])

    def set_context(self):
        self.asset_tracking_widget.set_context()
        self.playlist_browser.set_context()
        self.timeline_widget.set_context()

        current_tab = self.tabs_widget.currentIndex()
        context_dic = dict()
        context_dic['current_tab'] = current_tab
        user.user().add_context(user_vars._video_manager_context_, context_dic)

    def refresh(self):
        self.video_browser.refresh()
        self.playlist_browser.refresh()
        self.asset_tracking_widget.refresh()
        self.video_history_widget.refresh()
        self.timeline_widget.refresh()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.refresh()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.refresh()
            self.raise_()

    def build_ui(self):
        self.resize(1280,720)
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.content_widget = gui_utils.QSplitter()
        self.main_layout.addWidget(self.content_widget)

        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setMaximumWidth(380)
        self.tabs_widget.setIconSize(QtCore.QSize(16,16))
        self.content_widget.addWidget(self.tabs_widget)

        self.tabs_widget.addTab(self.video_browser, QtGui.QIcon(ressources._videos_icon_), "Videos")
        self.tabs_widget.addTab(self.playlist_browser, QtGui.QIcon(ressources._playlist_icon_), "Playlists")

        self.content_3_widget = QtWidgets.QWidget()
        self.content_3_layout = QtWidgets.QVBoxLayout()
        self.content_3_layout.setContentsMargins(0,0,0,0)
        self.content_3_layout.setSpacing(0)
        self.content_3_widget.setLayout(self.content_3_layout)
        self.content_widget.addWidget(self.content_3_widget)

        self.content_3_layout.addWidget(self.video_player)
        self.content_3_layout.addWidget(self.buttons_bar_widget)
        self.content_3_layout.addWidget(self.timeline_widget)

        self.content_2_widget = gui_utils.QSplitter()
        self.content_2_widget.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.content_widget.addWidget(self.content_2_widget)

        self.content_2_widget.addWidget(self.asset_tracking_widget)
        self.content_2_widget.addWidget(self.video_history_widget)
