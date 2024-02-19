# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os
import time
import logging
import traceback
import copy

# Wizard modules
from wizard.core import launch
from wizard.core import assets
from wizard.core import user
from wizard.core import project
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import subtasks_library
from wizard.vars import ressources
from wizard.vars import user_vars
from wizard.vars import assets_vars

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import confirm_widget
from wizard.gui import drop_files_widget
from wizard.gui import comment_widget
from wizard.gui import batch_settings_widget
from wizard.gui import tag_label
from wizard.gui import current_asset_viewer
from wizard.gui.video_manager import video_manager

logger = logging.getLogger(__name__)

class videos_widget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(videos_widget, self).__init__(parent)

        self.variant_id = None
        self.videos_rows = None
        self.video_list_ids = dict()
        self.video_icon_ids = dict()
        self.check_existence_thread = check_existence_thread()
        self.search_thread = search_thread()
        self.video_manager_widget = None

        self.view_comment_widget = tag_label.view_comment_widget(self)

        self.icon_mode = 0
        self.list_mode = 1

        self.build_ui()
        self.start_timer()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def start_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.start(10000)

    def update_times_ago(self):
        if self.icon_mode:
            return
        for video_id in self.video_list_ids.keys():
            self.video_list_ids[video_id].update_time_ago()

    def dragEnterEvent(self, event):
        self.drop_widget.setVisible(1)
        event.accept()

    def dragLeaveEvent(self, event):
        self.drop_widget.setVisible(0)
        event.accept()

    def dropEvent(self, event):
        self.drop_widget.setVisible(0)
        data = event.mimeData()
        urls = data.urls()
        files = []
        for url in urls:
            if url and url.scheme() == 'file':
                path = str(url.path())[1:]
                files.append(path)
        if len(files) != 0:
            self.merge_files(files)

    def focus_video(self, video_id):
        if self.icon_mode:
            ids = self.video_icon_ids
            view = self.icon_view
        else:
            ids = self.video_list_ids
            view = self.list_view
        if video_id in ids.keys():
            item = ids[video_id]
            view.scrollToItem(item)
            view.setCurrentItem(item)

    def change_variant(self, variant_id):
        self.check_existence_thread.running = False
        self.video_list_ids = dict()
        self.video_icon_ids = dict()
        self.list_view.clear()
        self.icon_view.clear()
        self.variant_id = variant_id
        self.current_asset_viewer.refresh('variant', variant_id)
        self.refresh()

    def show_info_mode(self, text, image):
        self.views_widget.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)
        self.setAcceptDrops(False)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.views_widget.setVisible(1)
        self.setAcceptDrops(True)

    def refresh(self):
        QtWidgets.QApplication.processEvents()
        start_time = time.perf_counter()
        if self.isVisible():
            self.refresh_list_view()
            self.refresh_icons_view()
            self.update_search()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def refresh_list_view(self):
        if self.list_mode:
            if self.variant_id is not None and self.variant_id != 0:
                self.videos_rows = project.get_videos(self.variant_id)
                project_videos_id = []
                if self.videos_rows is not None:
                    self.hide_info_mode()
                    for video_row in self.videos_rows:
                        project_videos_id.append(video_row['id'])
                        if video_row['id'] not in self.video_list_ids.keys():
                            video_item = custom_video_tree_item(video_row, self.list_view.invisibleRootItem())
                            video_item.signal_handler.enter.connect(self.view_comment_widget.show_comment)
                            video_item.signal_handler.leave.connect(self.view_comment_widget.close)
                            video_item.signal_handler.move_event.connect(self.view_comment_widget.move_ui)
                            self.video_list_ids[video_row['id']] = video_item
                        else:
                            self.video_list_ids[video_row['id']].refresh(video_row)

                video_list_ids = list(self.video_list_ids.keys())
                for video_id in video_list_ids:
                    if video_id not in project_videos_id:
                        self.remove_tree_video(video_id)
                if len(self.video_list_ids.keys()) == 0:
                    self.show_info_mode("No video found\nCreate videos within softwares !", ressources._no_video_info_image_)
                self.check_existence_thread.update_videos_rows(self.videos_rows)
            elif self.variant_id is None:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()

    def refresh_icons_view(self):
        if self.icon_mode:
            if self.variant_id is not None and self.variant_id != 0:
                self.videos_rows = project.get_videos(self.variant_id)
                project_videos_id = []
                if self.videos_rows is not None:
                    self.hide_info_mode()
                    for video_row in self.videos_rows:
                        project_videos_id.append(video_row['id'])
                        if video_row['id'] not in self.video_icon_ids.keys():
                            video_item = custom_video_icon_item(video_row)
                            self.icon_view.addItem(video_item)
                            self.video_icon_ids[video_row['id']] = video_item
                video_icon_ids = list(self.video_icon_ids.keys())
                for video_id in video_icon_ids:
                    if video_id not in project_videos_id:
                        self.remove_icon_video(video_id)
                if len(self.video_icon_ids.keys()) == 0:
                    self.show_info_mode("No video found\nCreate videos within softwares !", ressources._no_video_info_image_)
                self.check_existence_thread.update_videos_rows(self.videos_rows)
            elif self.variant_id is None:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()

    def missing_file(self, video_id):
        if self.list_mode:
            if video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].set_missing()
        elif self.icon_mode:
            if video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].set_missing()

    def not_missing_file(self, video_id):
        if self.list_mode:
            if video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].set_not_missing()
        elif self.icon_mode:
            if video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].set_not_missing()

    def hide_all(self):
        if self.list_mode:
            for video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].setHidden(True)
        elif self.icon_mode:
            for video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].setHidden(True)

    def show_all(self):
        if self.list_mode:
            for video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].setHidden(False)
        elif self.icon_mode:
            for video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].setHidden(False)

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.search_thread.update_search(self.videos_rows, search_data)
        else:
            self.show_all()

    def show_search_version(self, video_id):
        if self.list_mode:
            if video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].setHidden(False)
        elif self.icon_mode:
            if video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].setHidden(False)

    def hide_search_version(self, video_id):
        if self.list_mode:
            if video_id in self.video_list_ids.keys():
                self.video_list_ids[video_id].setHidden(True)
        elif self.icon_mode:
            if video_id in self.video_icon_ids.keys():
                self.video_icon_ids[video_id].setHidden(True)


    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))
        self.icon_view_scrollBar.rangeChanged.connect(lambda: self.icon_view_scrollBar.setValue(self.icon_view_scrollBar.maximum()))

        self.list_view.itemSelectionChanged.connect(self.refresh_infos)
        self.list_view.itemDoubleClicked.connect(self.open_video)
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.icon_view.itemSelectionChanged.connect(self.refresh_infos)
        self.icon_view.itemDoubleClicked.connect(self.open_video)
        self.icon_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.archive_button.clicked.connect(self.archive)
        self.folder_button.clicked.connect(self.open_folder)
        self.toggle_view_button.clicked.connect(self.toggle_view)
        self.comment_button.clicked.connect(lambda:self.modify_comment(pos=None))

        self.check_existence_thread.missing_file_signal.connect(self.missing_file)
        self.check_existence_thread.not_missing_file_signal.connect(self.not_missing_file)

        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.show_id_signal.connect(self.show_search_version)
        self.search_thread.hide_id_signal.connect(self.hide_search_version)

        self.timer.timeout.connect(self.update_times_ago)

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.current_asset_viewer = current_asset_viewer.current_asset_viewer()
        self.main_layout.addWidget(self.current_asset_viewer)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.views_widget = QtWidgets.QWidget()
        self.views_layout = QtWidgets.QHBoxLayout()
        self.views_layout.setContentsMargins(0,0,0,0)
        self.views_layout.setSpacing(0)
        self.views_widget.setLayout(self.views_layout)
        self.main_layout.addWidget(self.views_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(6)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.list_view.setHeaderLabels(['Version', 'User', 'Date', 'Comment', 'File', 'ID'])
        self.list_view.header().resizeSection(2, 150)
        self.list_view.header().resizeSection(3, 250)
        self.list_view.header().resizeSection(4, 400)
        self.list_view.header().resizeSection(5, 50)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.views_layout.addWidget(self.list_view)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.icon_view.setObjectName('icon_view')
        self.icon_view.setSpacing(4)
        self.icon_view.setIconSize(QtCore.QSize(200,200))
        self.icon_view.setMovement(QtWidgets.QListView.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.IconMode)
        self.icon_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.views_layout.addWidget(self.icon_view)
        self.icon_view.setVisible(0)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.videos_count_label = QtWidgets.QLabel()
        self.videos_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.videos_count_label)

        self.selection_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selection_count_label)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,8)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "j.smith&maya", "retake eye"')
        self.buttons_layout.addWidget(self.search_bar)

        self.toggle_view_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.toggle_view_button, "Switch to list view")
        self.toggle_view_button.setFixedSize(35,35)
        self.toggle_view_button.setIconSize(QtCore.QSize(25,25))
        self.toggle_view_button.setIcon(QtGui.QIcon(ressources._tool_icon_view_))
        self.buttons_layout.addWidget(self.toggle_view_button)

        self.comment_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.comment_button, "Modify comment")
        self.comment_button.setFixedSize(35,35)
        self.comment_button.setIconSize(QtCore.QSize(25,25))
        self.comment_button.setIcon(QtGui.QIcon(ressources._tool_comment_))
        self.buttons_layout.addWidget(self.comment_button)

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open versions folder")
        self.folder_button.setFixedSize(35,35)
        self.folder_button.setIconSize(QtCore.QSize(25,25))
        self.folder_button.setIcon(QtGui.QIcon(ressources._tool_folder_))
        self.buttons_layout.addWidget(self.folder_button)

        self.archive_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.archive_button, "Archive selection")
        self.archive_button.setFixedSize(35,35)
        self.archive_button.setIconSize(QtCore.QSize(25,25))
        self.archive_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.archive_button)

        self.drop_widget = drop_files_widget.drop_widget(self)
        self.drop_widget.setText('Merge file as new version')
        self.drop_widget.setVisible(0)

    def context_menu_requested(self):
        selection = self.get_selection()
        menu = gui_utils.QMenu(self)
        folder_action = menu.addAction(QtGui.QIcon(ressources._tool_folder_), 'Open folder')
        archive_action = None
        comment_action = None
        if len(selection)>=1:
            archive_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Archive video(s)')
            comment_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Modify comment')

        pos = QtGui.QCursor().pos()
        action = menu.exec_(pos)
        if action is not None:
            if action == folder_action:
                self.open_folder()
            elif action == archive_action:
                self.archive()
            elif action == comment_action:
                self.modify_comment(pos)

    def modify_comment(self, pos=None):
        items = self.get_selection()
        if items is not None:
            if len(items) > 0:
                old_comment = ''
                if len(items) == 1:
                    old_comment = items[0].video_row['comment']
                self.comment_widget = comment_widget.comment_widget(old_comment=old_comment, pos=pos)
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    comment = self.comment_widget.comment
                    for item in items:
                        assets.modify_video_comment(item.video_row['id'], comment)
                    gui_server.refresh_team_ui()

    def toggle_view(self):
        selection = self.get_selection()
        if self.icon_mode:
            self.icon_view.setVisible(0)
            self.list_view.setVisible(1)
            self.list_mode = 1
            self.icon_mode = 0
        elif self.list_mode:
            self.icon_view.setVisible(1)
            self.list_view.setVisible(0)
            self.list_mode = 0
            self.icon_mode = 1
        if self.icon_mode:
            self.toggle_view_button.setIcon(QtGui.QIcon(ressources._tool_list_view_))
            gui_utils.modify_application_tooltip(self.toggle_view_button, "Switch to list view")
        elif self.list_mode:
            self.toggle_view_button.setIcon(QtGui.QIcon(ressources._tool_icon_view_))
            gui_utils.modify_application_tooltip(self.toggle_view_button, "Switch to icon view")
        self.refresh()
        self.set_selection(selection)

    def set_view_as_icon_mode(self):
        if self.icon_mode == 1:
            pass
        else:
            self.toggle_view()

    def set_view_as_list_mode(self):
        if self.list_mode == 1:
            pass
        else:
            self.toggle_view()

    def set_context(self):
        if self.icon_mode == 1:
            current_mode = 'icon'
        else:
            current_mode = 'list'
        context_dic = dict()
        context_dic['view_mode'] = current_mode
        user.user().add_context(user_vars._videos_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._videos_context_)
        if context_dic is not None and context_dic != dict():
            if context_dic['view_mode'] == 'icon':
                self.set_view_as_icon_mode()
            elif context_dic['view_mode'] == 'list':
                self.set_view_as_list_mode()

    def get_number(self):
        number = 0
        if self.icon_mode:
            number = len(self.video_icon_ids)
        elif self.list_mode:
            number = len(self.video_list_ids)
        return number

    def get_selection(self):
        selection = None
        if self.icon_mode:
            selection = self.icon_view.selectedItems()
        elif self.list_mode:
            selection = self.list_view.selectedItems()
        return selection

    def set_selection(self, selection):
        self.clear_selection()
        if selection is not None:
            for item in selection:
                if self.icon_mode:
                    self.video_icon_ids[item.video_row['id']].setSelected(True)
                elif self.list_mode:
                    self.video_list_ids[item.video_row['id']].setSelected(True)

    def clear_selection(self):
        for video_id in self.video_icon_ids.keys():
            self.video_icon_ids[video_id].setSelected(False)
        for video_id in self.video_list_ids.keys():
            self.video_list_ids[video_id].setSelected(False)

    def refresh_infos(self):
        self.videos_count_label.setText(f"{self.get_number()} videos -")
        selection = self.get_selection()
        if selection is not None:
            number = len(selection)
        else:
            number = 0
        self.selection_count_label.setText(f"{number} selected")

    def remove_tree_video(self, video_id):
        if video_id in self.video_list_ids.keys():
            item = self.video_list_ids[video_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.video_list_ids[video_id]

    def remove_icon_video(self, video_id):
        if video_id in self.video_icon_ids.keys():
            item = self.video_icon_ids[video_id]
            self.icon_view.takeItem(self.icon_view.row(item))
            del self.video_icon_ids[video_id]

    def open_video(self):
        items = self.get_selection()
        if items is not None:
            if len(items) == 1:
                instance = video_manager.video_player_instances().get_instance()
                instance.add_video(items[0].video_row['file_path'], items[0].video_row['id'])
                instance.load_nexts()
                instance.show()

    def open_folder(self):
        if self.variant_id is not None:
            path_utils.startfile(assets.get_video_path(self.variant_id))

    def archive(self):
        items = self.get_selection()
        if items is not None:
            if items!=[]:
                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                    videos_ids = []
                    for item in items:
                        videos_ids.append(item.video_row['id'])
                    subtasks_library.archive_videos(videos_ids)

class custom_video_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, video_row, parent=None):
        super(custom_video_tree_item, self).__init__(parent)
        self.video_row = video_row
        self.comment_label = tag_label.tag_label()
        self.comment_label.setNoMultipleLines()
        self.treeWidget().setItemWidget(self, 3, self.comment_label)
        self.fill_ui()
        self.update_time_ago()
        self.signal_handler = signal_handler()
        self.connect_functions()

    def show_comment(self):
        if self.comment_label.isActiveWindow():
            self.signal_handler.enter.emit(self.video_row['comment'], self.video_row['creation_user'])

    def connect_functions(self):
        self.comment_label.enter.connect(self.show_comment)
        self.comment_label.leave.connect(self.signal_handler.leave.emit)
        self.comment_label.move_event.connect(self.signal_handler.move_event.emit)

    def update_time_ago(self):
        self.setText(2, tools.time_ago_from_timestamp(self.video_row['creation_time']))

    def fill_ui(self):
        self.setText(0, self.video_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setIcon(0, QtGui.QIcon(ressources._file_icon_))
        self.setText(1, self.video_row['creation_user'])
        self.setForeground(2, QtGui.QBrush(QtGui.QColor('gray')))
        self.comment_label.setText( self.video_row['comment'])
        self.setText(4, os.path.basename(self.video_row['file_path']))
        self.setText(5, str(self.video_row['id']))
        self.setForeground(5, QtGui.QBrush(QtGui.QColor('gray')))

    def set_missing(self):
        self.setForeground(4, QtGui.QBrush(QtGui.QColor('#f79360')))

    def set_not_missing(self):
        self.setForeground(4, QtGui.QBrush(QtGui.QColor('#9ce87b')))

    def refresh(self, video_row):
        self.video_row = video_row
        self.fill_ui()

class signal_handler(QtCore.QObject):

    enter = pyqtSignal(str, str)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_handler, self).__init__(parent)

class custom_video_icon_item(QtWidgets.QListWidgetItem):
    def __init__(self, video_row, parent=None):
        super(custom_video_icon_item, self).__init__(parent)
        self.video_row = video_row
        self.fill_ui()

    def fill_ui(self):
        icon = QtGui.QIcon()
        
        pixmap = QtGui.QPixmap(self.video_row['thumbnail_path'])
        icon.addPixmap(pixmap, QtGui.QIcon.Normal)
        icon.addPixmap(pixmap, QtGui.QIcon.Selected)
        if not path_utils.isfile(self.video_row['thumbnail_path']):
            default_icon = QtGui.QIcon(ressources._no_screenshot_small_)
            icon.addPixmap(default_icon.pixmap(200), QtGui.QIcon.Normal)
            icon.addPixmap(default_icon.pixmap(200), QtGui.QIcon.Selected)

        self.setIcon(icon)
        self.setText(f"{self.video_row['name']} - {self.video_row['creation_user']}")
        self.setTextAlignment(QtCore.Qt.AlignLeft)

    def set_missing(self):
        self.setForeground(QtGui.QColor('#f79360'))

    def set_not_missing(self):
        self.setForeground(QtGui.QColor('#9ce87b'))

class check_existence_thread(QtCore.QThread):

    missing_file_signal = pyqtSignal(int)
    not_missing_file_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(check_existence_thread, self).__init__(parent)
        self.videos_rows = None
        self.running = True

    def run(self):
        if self.videos_rows is not None:
            for video_row in self.videos_rows:
                if not path_utils.isfile(video_row['file_path']):
                    self.missing_file_signal.emit(video_row['id'])
                else:
                    self.not_missing_file_signal.emit(video_row['id'])
                if not self.running:
                    break

    def update_videos_rows(self, videos_rows):
        self.running = False
        self.videos_rows = videos_rows
        self.running = True
        self.start()

class search_thread(QtCore.QThread):

    show_id_signal = pyqtSignal(int)
    hide_id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, videos_rows, search_data):
        self.running = False
        self.search_data = search_data
        self.videos_rows = copy.deepcopy(videos_rows)
        self.running = True
        self.start()

    def run(self):
        try:
            keywords = self.search_data.split('&')
            for video_row in self.videos_rows:

                video_id = video_row['id']
                del video_row['id']
                del video_row['creation_time']
                del video_row['file_path']
                del video_row['screenshot_path']
                del video_row['thumbnail_path']
                del video_row['variant_id']

                values = list(video_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_id_signal.emit(video_id)
                else:
                    self.hide_id_signal.emit(video_id)
        except:
            logger.debug(str(traceback.format_exc()))
