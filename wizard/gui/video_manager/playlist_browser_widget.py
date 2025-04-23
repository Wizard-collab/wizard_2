# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging
import time
import traceback
import copy
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import confirm_widget
from wizard.gui.video_manager import create_playlist_widget

# Wizard core modules
from wizard.core import user
from wizard.core import project
from wizard.core import tools
from wizard.vars import ressources
from wizard.vars import user_vars

logger = logging.getLogger(__name__)


class playlist_browser_widget(QtWidgets.QWidget):

    load_playlist = pyqtSignal(int)

    def __init__(self, parent=None):
        super(playlist_browser_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Playlist browser")

        self.playlist_ids = dict()
        self.playlist_rows = []

        self.old_thread_id = None
        self.search_threads = dict()

        self.build_ui()
        self.connect_functions()

    def set_context(self):
        context_dic = dict()
        context_dic['search_text'] = self.search_bar.text()
        user.user().add_context(user_vars._playlist_browser_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._playlist_browser_context_)
        if context_dic is None:
            return
        if 'search_text' in context_dic.keys():
            self.search_bar.setText(context_dic['search_text'])

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.update_search)
        self.list_view.itemDoubleClicked.connect(self.open_selected_playlist)
        self.create_playlist_button.clicked.connect(self.create_playlist)
        self.list_view.customContextMenuRequested.connect(
            self.context_menu_requested)

    def open_selected_playlist(self, item):
        self.load_playlist.emit(item.playlist_row['id'])

    def create_playlist(self):
        self.create_playlist_widget = create_playlist_widget.create_playlist_widget()
        self.create_playlist_widget.exec()

    def update_search(self):
        search_data = self.search_bar.text()
        self.search_start_time = time.perf_counter()
        self.accept_item_from_thread = False
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
            self.search_threads[self.old_thread_id].show_playlist_signal.disconnect(
            )
            self.search_threads[self.old_thread_id].hide_playlist_signal.disconnect(
            )
        thread_id = time.time()
        self.search_threads[thread_id] = search_thread()
        self.search_threads[thread_id].show_playlist_signal.connect(
            self.show_playlist)
        self.search_threads[thread_id].hide_playlist_signal.connect(
            self.hide_playlist)
        self.old_thread_id = thread_id
        if len(search_data) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(
                self.playlist_rows, search_data)
        else:
            self.search_threads[thread_id].running = False
            self.show_all_playlists()
        self.clean_threads()

    def clean_threads(self):
        ids = list(self.search_threads.keys())
        for thread_id in ids:
            if not self.search_threads[thread_id].running:
                self.search_threads[thread_id].terminate()
                del self.search_threads[thread_id]

    def show_playlist(self, playlist_id):
        if playlist_id in self.playlist_ids.keys():
            self.playlist_ids[playlist_id].setHidden(False)

    def hide_playlist(self, playlist_id):
        if playlist_id in self.playlist_ids.keys():
            self.playlist_ids[playlist_id].setHidden(True)

    def show_all_playlists(self):
        for playlist_id in self.playlist_ids.keys():
            self.show_playlist(playlist_id)

    def context_menu_requested(self):
        selection = self.list_view.selectedItems()
        menu = gui_utils.QMenu(self)
        if len(selection) >= 1:
            delete_playlist_action = menu.addAction(QtGui.QIcon(
                ressources._tool_archive_), 'Delete selected playlist(s)')
        else:
            return

        pos = QtGui.QCursor().pos()
        action = menu.exec(pos)
        if action is not None:
            if action == delete_playlist_action:
                self.delete_selected_playlists()

    def delete_selected_playlists(self):
        selection = self.list_view.selectedItems()
        if len(selection) == 0:
            return
        self.confirm_widget = confirm_widget.confirm_widget(
            f"Delete selected playlist(s) ?", parent=self)
        if not self.confirm_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            return
        for item in selection:
            playlist_id = item.playlist_row['id']
            project.remove_playlist(playlist_id)
        gui_server.refresh_team_ui()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.setMinimumWidth(380)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('dark_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.search_bar = gui_utils.search_bar()
        self.header_layout.addWidget(self.search_bar)

        self.create_playlist_button = QtWidgets.QPushButton()
        self.create_playlist_button.setFixedSize(32, 32)
        self.create_playlist_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.header_layout.addWidget(self.create_playlist_button)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.content_widget.setObjectName('dark_widget')
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setHeaderHidden(True)
        self.list_view.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet(
            "#tree_as_list_widget::item{padding:0px;}")
        self.list_view.setColumnCount(1)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.content_layout.addWidget(self.list_view)

    def refresh(self):
        playlist_rows = project.get_all_playlists()
        project_playlists_ids = []
        self.playlist_rows = playlist_rows
        for playlist_row in playlist_rows:
            project_playlists_ids.append(playlist_row['id'])
            if playlist_row['id'] not in self.playlist_ids.keys():
                item = playlist_item(
                    playlist_row, self.list_view.invisibleRootItem())
                self.playlist_ids[playlist_row['id']] = item
            self.playlist_ids[playlist_row['id']].update_row(playlist_row)
        existing_playlists_ids = list(self.playlist_ids.keys())
        for playlist_id in existing_playlists_ids:
            if playlist_id not in project_playlists_ids:
                self.remove_playlist(playlist_id)
        self.list_view.updateGeometry()

    def remove_playlist(self, playlist_id):
        if playlist_id in self.playlist_ids.keys():
            item = self.playlist_ids[playlist_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.playlist_ids[playlist_id]


class playlist_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, playlist_row, parent=None):
        super(playlist_item, self).__init__(parent)
        self.playlist_row = playlist_row
        self.widget = playlist_item_widget()
        self.treeWidget().setItemWidget(self, 0, self.widget)

    def update_row(self, playlist_row):
        self.playlist_row = playlist_row
        self.refresh()

    def refresh(self):
        self.widget.playlist_name_label.setText(self.playlist_row['name'])
        self.widget.user_label.setText(self.playlist_row['last_save_user'])
        self.widget.time_label.setText(
            tools.time_ago_from_timestamp(self.playlist_row['last_save_time']))
        thumbnail_pixmap = QtGui.QIcon(
            self.playlist_row['thumbnail_path']).pixmap(100)
        self.widget.thumbnail_label.setPixmap(thumbnail_pixmap)
        self.widget.adjustSize()
        self.setSizeHint(0, self.widget.sizeHint())


class playlist_item_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(playlist_item_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.thumbnail_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.thumbnail_label)

        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.infos_layout)

        self.header_infos_layout = QtWidgets.QHBoxLayout()
        self.header_infos_layout.setContentsMargins(0, 0, 0, 0)
        self.infos_layout.addLayout(self.header_infos_layout)

        self.playlist_name_label = QtWidgets.QLabel()
        self.playlist_name_label.setObjectName('bold_label')
        self.header_infos_layout.addWidget(self.playlist_name_label)

        self.user_label = QtWidgets.QLabel()
        self.user_label.setObjectName("gray_label")
        self.header_infos_layout.addWidget(self.user_label)

        self.time_label = QtWidgets.QLabel()
        self.time_label.setObjectName("gray_label")
        self.header_infos_layout.addWidget(self.time_label)

        self.header_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))


class search_thread(QtCore.QThread):

    show_playlist_signal = pyqtSignal(int)
    hide_playlist_signal = pyqtSignal(int)
    search_ended = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, playlist_rows, search_data):
        self.search_data = search_data
        self.playlist_rows = copy.deepcopy(playlist_rows)
        self.start()

    def run(self):
        try:
            playlists_to_show = []
            playlists_to_hide = []

            keywords_sets = self.search_data.split('+')
            for playlist_row in self.playlist_rows:

                playlist_id = playlist_row['id']
                values = []
                for key in playlist_row:
                    if key in ['id', 'creation_time']:
                        continue
                    values.append(playlist_row[key])

                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                for keywords_set in keywords_sets:
                    if keywords_set == '':
                        continue
                    keywords = keywords_set.split('&')
                    if all(keyword.upper() in data.upper() for keyword in keywords):
                        playlists_to_show.append(playlist_id)

            QtWidgets.QApplication.processEvents()
            time.sleep(0.01)
            for playlist_row in self.playlist_rows:
                if playlist_row['id'] in playlists_to_show:
                    self.show_playlist_signal.emit(playlist_row['id'])
                else:
                    self.hide_playlist_signal.emit(playlist_row['id'])
            self.search_ended.emit(1)

        except:
            logger.info(str(traceback.format_exc()))
        self.running = False
