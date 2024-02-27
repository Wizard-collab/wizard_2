# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import time
import logging
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard core modules
from wizard.core import path_utils
from wizard.core import project
from wizard.core import tools
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class video_history_widget(QtWidgets.QFrame):

    replace_current_video = pyqtSignal(int)

    def __init__(self, parent=None):
        super(video_history_widget, self).__init__(parent)
        self.variant_id = None
        self.video_ids = dict()
        self.build_ui()
        self.connect_functions()

    def change_video_row(self, video_row):
        if video_row is None:
            self.change_variant(None)
            return
        self.change_variant(video_row['variant_id'])
        self.select_video(video_row['id'])

    def change_variant(self, variant_id):
        self.variant_id = variant_id
        self.refresh()

    def refresh(self):
        start_time = time.perf_counter()
        video_rows = project.get_videos(self.variant_id)
        project_videos_ids = []
        for video_row in video_rows:
            project_videos_ids.append(video_row['id'])
            if video_row['id'] not in self.video_ids.keys():
                item = video_item(video_row, self.list_view.invisibleRootItem())
                self.video_ids[video_row['id']] = item
                self.video_ids[video_row['id']].refresh()
            else:
                self.video_ids[video_row['id']].update_row(video_row)
        existing_video_ids = list(self.video_ids.keys())
        for video_id in existing_video_ids:
            if video_id not in project_videos_ids:
                self.remove_video(video_id)
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def remove_video(self, video_id):
        if video_id in self.video_ids.keys():
            item = self.video_ids[video_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.video_ids[video_id]

    def select_video(self, video_id):
        self.clear_selection()
        if video_id not in self.video_ids.keys():
            return
        self.video_ids[video_id].setSelected(True)

    def clear_selection(self):
        for video_id in self.video_ids.keys():
            self.video_ids[video_id].setSelected(False)

    def connect_functions(self):
        self.list_view.itemDoubleClicked.connect(self.switch_video)

    def switch_video(self, item):
        self.replace_current_video.emit(item.video_row['id'])

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(6,6,6,6)
        self.main_layout.addLayout(self.header_layout)

        self.header_label = QtWidgets.QLabel("Video history")
        self.header_label.setObjectName("title_label_2")
        self.header_layout.addWidget(self.header_label)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setHeaderHidden(True)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet("#tree_as_list_widget::item{padding:0px;}")
        self.list_view.setColumnCount(1)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_layout.addWidget(self.list_view)

        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(6,6,6,6)
        self.main_layout.addLayout(self.infos_layout)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

class video_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, video_row, parent=None):
        super(video_item, self).__init__(parent)
        self.video_row = video_row
        self.widget = video_item_widget()
        self.treeWidget().setItemWidget(self, 0, self.widget)

    def update_row(self, video_row):
        self.video_row = video_row
        self.refresh()

    def refresh(self):
        thumbnail_pixmap = QtGui.QIcon(self.video_row['thumbnail_path']).pixmap(100)
        self.widget.thumbnail_label.setPixmap(thumbnail_pixmap)
        self.widget.video_version_label.setText(self.video_row['name'])
        self.widget.user_label.setText(self.video_row['creation_user'])
        self.widget.time_label.setText(tools.time_ago_from_timestamp(self.video_row['creation_time']))
        self.widget.comment_label.setText(self.video_row['comment'])
        self.setSizeHint(0, self.widget.sizeHint())

class video_item_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_item_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(3,3,3,3)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.thumbnail_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.thumbnail_label)

        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.infos_layout)

        self.header_infos_layout = QtWidgets.QHBoxLayout()
        self.header_infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.addLayout(self.header_infos_layout)

        self.video_version_label = QtWidgets.QLabel()
        self.video_version_label.setObjectName('bold_label')
        self.header_infos_layout.addWidget(self.video_version_label)

        self.user_label = QtWidgets.QLabel()
        self.user_label.setObjectName("gray_label")
        self.header_infos_layout.addWidget(self.user_label)

        self.time_label = QtWidgets.QLabel()
        self.time_label.setObjectName("gray_label")
        self.header_infos_layout.addWidget(self.time_label)

        self.header_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.comment_label = QtWidgets.QLabel()
        self.comment_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.infos_layout.addWidget(self.comment_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))