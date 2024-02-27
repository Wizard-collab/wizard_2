# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging
import time
import traceback
import copy
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

class video_browser_widget(QtWidgets.QWidget):

    add_videos = pyqtSignal(object)
    create_playlist_and_add_videos = pyqtSignal(object)

    def __init__(self, parent=None):
        super(video_browser_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Video browser")

        self.variants_ids = dict()
        self.comb_rows_for_search = []

        self.old_thread_id = None
        self.search_threads = dict()

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.icon_view.itemDoubleClicked.connect(lambda:self.create_playlist(add=False))
        self.icon_view.customContextMenuRequested.connect(self.context_menu_requested)
        self.search_bar.textChanged.connect(self.update_search)

    def update_search(self):
        search_data = self.search_bar.text()
        self.search_start_time = time.perf_counter()
        self.accept_item_from_thread = False
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
            self.search_threads[self.old_thread_id].show_variant_signal.disconnect()
            self.search_threads[self.old_thread_id].hide_variant_signal.disconnect()
        thread_id = time.time()
        self.search_threads[thread_id] = search_thread()
        self.search_threads[thread_id].show_variant_signal.connect(self.show_variant)
        self.search_threads[thread_id].hide_variant_signal.connect(self.hide_variant)
        self.old_thread_id = thread_id
        if len(search_data) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(self.comb_rows_for_search, search_data)
        else:
            self.search_threads[thread_id].running=False
            self.show_all_variants()
        self.clean_threads()

    def clean_threads(self):
        ids = list(self.search_threads.keys())
        for thread_id in ids:
            if not self.search_threads[thread_id].running:
                self.search_threads[thread_id].terminate()
                del self.search_threads[thread_id]

    def show_variant(self, variant_id):
        if variant_id in self.variants_ids.keys():
            self.variants_ids[variant_id]['video_item'].setHidden(False)

    def hide_variant(self, variant_id):
        if variant_id in self.variants_ids.keys():
            self.variants_ids[variant_id]['video_item'].setHidden(True)

    def show_all_variants(self):
        for variant_id in self.variants_ids.keys():
            self.show_variant(variant_id)

    def context_menu_requested(self):
        selection = self.icon_view.selectedItems()
        menu = gui_utils.QMenu(self)
        folder_action = menu.addAction(QtGui.QIcon(ressources._tool_folder_), 'Open folder')
        archive_action = None
        comment_action = None
        create_playlist_action = None
        if len(selection)>=1:
            archive_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Archive video(s)')
            comment_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Modify comment')
            create_playlist_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Create playlist')
            add_to_playlist_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Add to playlist')

        pos = QtGui.QCursor().pos()
        action = menu.exec_(pos)
        if action is not None:
            if action == folder_action:
                self.open_folder()
            elif action == archive_action:
                self.archive()
            elif action == comment_action:
                self.modify_comment(pos)
            elif action == create_playlist_action:
                self.create_playlist()
            elif action == add_to_playlist_action:
                self.add_to_playlist()

    def create_playlist(self, add=False):
        items = self.icon_view.selectedItems()
        if items is None:
            return
        if len(items) == 0:
            return
        videos = []
        for item in items:
            videos.append((item.video_row['file_path'], item.video_row['id']))
        if not add:
            self.create_playlist_and_add_videos.emit(videos)
        else:
            self.add_videos.emit(videos)

    def add_to_playlist(self):
        self.create_playlist(add=True)

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.setMinimumWidth(380)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('dark_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.search_bar = gui_utils.search_bar()
        self.header_layout.addWidget(self.search_bar)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_widget.setObjectName('dark_widget')
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_widget.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_widget)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.icon_view.setObjectName('icon_view')
        self.icon_view.setSpacing(4)
        self.icon_view.setContentsMargins(4,4,4,4)
        self.icon_view.setIconSize(QtCore.QSize(200,200))
        self.icon_view.setMovement(QtWidgets.QListView.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.IconMode)
        self.icon_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.content_layout.addWidget(self.icon_view)

    def refresh(self):
        stage_rows = project.get_all_stages()
        self.comb_rows_for_search = []
        stages = dict()
        for stage_row in stage_rows:
            stages[stage_row['id']] = stage_row
        variant_rows = project.get_all_variants()
        variants = dict()
        for variant_row in variant_rows:
            variants[variant_row['id']] = variant_row
        for video_row in project.get_all_videos():
            if video_row['variant_id'] not in self.variants_ids.keys():
                self.variants_ids[video_row['variant_id']] = dict()
                self.variants_ids[video_row['variant_id']]['last_video'] = video_row
                self.variants_ids[video_row['variant_id']]['asset_name'] = variants[video_row['variant_id']]['string']
                self.variants_ids[video_row['variant_id']]['variant_row'] = variants[video_row['variant_id']]
                self.variants_ids[video_row['variant_id']]['stage_row'] = stages[self.variants_ids[video_row['variant_id']]['variant_row']['stage_id']]
                comb_row = stages[self.variants_ids[video_row['variant_id']]['variant_row']['stage_id']]
                comb_row['variant'] = variants[video_row['variant_id']]['name']
                comb_row['variant_id'] = variants[video_row['variant_id']]['id']
                self.comb_rows_for_search.append(comb_row)
                video_item = custom_video_icon_item(video_row,
                                                self.variants_ids[video_row['variant_id']]['asset_name'],
                                                self.variants_ids[video_row['variant_id']]['stage_row'],
                                                self.icon_view)
                self.variants_ids[video_row['variant_id']]['video_item'] = video_item
            else:
                if int(video_row['name']) > int(self.variants_ids[video_row['variant_id']]['last_video']['name']):
                    self.variants_ids[video_row['variant_id']]['last_video'] = video_row
                    self.variants_ids[video_row['variant_id']]['video_item'].update_row(video_row)

class custom_video_icon_item(QtWidgets.QListWidgetItem):
    def __init__(self, video_row, asset_name, stage_row, parent=None):
        super(custom_video_icon_item, self).__init__(parent)
        self.video_row = video_row
        self.asset_name = asset_name
        self.stage_row = stage_row
        self.widget = video_item_widget()
        self.listWidget().setItemWidget(self, self.widget)
        self.fill_ui()

    def update_row(self, video_row):
        self.video_row = video_row
        self.fill_ui()

    def fill_ui(self):
        pixmap = QtGui.QPixmap(self.video_row['thumbnail_path'])
        if not path_utils.isfile(self.video_row['thumbnail_path']):
            pixmap = QtGui.QPixmap(ressources._no_screenshot_small_)

        self.widget.image_label.setPixmap(pixmap)
        self.widget.stage_label.setText(f"{self.stage_row['name']}")
        self.widget.asset_name_label.setText(f"{self.asset_name}")
        self.widget.infos_label.setText(f"{self.video_row['name']} - {self.video_row['creation_user']} - {tools.time_ago_from_timestamp(self.video_row['creation_time'])}")
        self.widget.set_background(ressources._stages_colors_[self.stage_row['name']])
        self.widget.set_state(self.stage_row['state'])
        self.setSizeHint(self.widget.sizeHint())

class video_item_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(video_item_widget, self).__init__(parent)
        self.build_ui()

    def set_background(self, color):
        self.stage_label.setStyleSheet("color: %s"%color)

    def set_state(self, state):
        self.state_label.setText(state)
        self.state_label.setStyleSheet("background-color:%s;font: bold;border-radius:4px;padding:3px"%ressources._states_colors_[state])

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(3,3,3,3)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.asset_name_label = QtWidgets.QLabel()
        self.asset_name_label.setObjectName('bold_label')
        self.asset_name_label.setWordWrap(True)
        self.main_layout.addWidget(self.asset_name_label)

        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.infos_layout)
        
        self.stage_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.stage_label)

        self.state_label = QtWidgets.QLabel()
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.infos_layout.addWidget(self.state_label)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedWidth(160)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.image_label)

        self.infos_label = QtWidgets.QLabel()
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

class search_thread(QtCore.QThread):

    show_variant_signal = pyqtSignal(int)
    hide_variant_signal = pyqtSignal(int)
    search_ended = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, comb_rows, search_data):
        self.search_data = search_data
        self.comb_rows = copy.deepcopy(comb_rows)
        self.start()

    def run(self):
        try:
            variants_to_show = []
            variants_to_hide = []

            keywords_sets = self.search_data.split('+')
            for comb_row in self.comb_rows:

                variant_id = comb_row['variant_id']
                values = []
                for key in comb_row:
                    if key in ['variant_id', 'id', 'creation_time', 'creation_user']:
                        continue
                    values.append(comb_row[key])

                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                for keywords_set in keywords_sets:
                    if keywords_set == '':
                        continue
                    keywords = keywords_set.split('&')
                    if all(keyword.upper() in data.upper() for keyword in keywords):
                        variants_to_show.append(variant_id)

            QtWidgets.QApplication.processEvents()
            time.sleep(0.01)
            for comb_row in self.comb_rows:
                if comb_row['id'] in variants_to_show:
                    self.show_variant_signal.emit(comb_row['id'])
                else:
                    self.hide_variant_signal.emit(comb_row['id'])
            self.search_ended.emit(1)

        except:
            logger.info(str(traceback.format_exc()))
        self.running = False