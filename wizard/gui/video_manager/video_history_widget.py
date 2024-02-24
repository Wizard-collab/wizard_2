# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
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

class video_history_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_history_widget, self).__init__(parent)
        self.variant_id = None
        self.video_ids = dict()
        self.build_ui()

    def change_variant(self, variant_id):
        self.variant_id = variant_id
        self.refresh()

    def refresh(self):
        video_rows = project.get_videos(self.variant_id)
        project_videos_ids = []
        for video_row in video_rows:
            project_videos_ids.append(video_row['id'])
            if video_row['id'] not in self.video_ids.keys():
                item = video_item(video_row, self.list_view.invisibleRootItem())
                self.video_ids[video_row['id']] = item
            else:
                self.video_ids[video_row['id']].update_row(video_row)
        existing_video_ids = list(self.video_ids.keys())
        for video_id in existing_video_ids:
            if video_id not in project_videos_ids:
                self.remove_video(video_id)

    def remove_video(self, video_id):
        if video_id in self.video_ids.keys():
            item = self.video_ids[video_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.video_ids[video_id]

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(1)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_layout.addWidget(self.list_view)

class video_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, video_row, parent=None):
        super(video_item, self).__init__(parent)
        self.video_row = video_row
        self.widget = video_item_widget()
        self.treeWidget().setItemWidget(self, 0, self.widget)
        self.refresh()

    def update_row(self, video_row):
        self.video_row = video_row
        self.refresh()

    def refresh(self):
        thumbnail_pixmap = QtGui.QIcon(self.video_row['thumbnail_path']).pixmap(100)
        self.widget.thumbnail_label.setPixmap(thumbnail_pixmap)
        self.widget.video_version_label.setText(self.video_row['name'])
        self.widget.comment_label.setText(self.video_row['comment'])

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

        self.video_version_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.video_version_label)

        self.comment_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.comment_label)