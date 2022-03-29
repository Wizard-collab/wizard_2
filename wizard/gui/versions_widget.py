# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os
import time
import logging

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

logger = logging.getLogger(__name__)

class versions_widget(QtWidgets.QWidget):

    version_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(versions_widget, self).__init__(parent)

        self.work_env_id = None
        self.version_list_ids = dict()
        self.version_icon_ids = dict()
        self.check_existence_thread = check_existence_thread()
        self.search_thread = search_thread()

        self.icon_mode = 0
        self.list_mode = 1

        self.build_ui()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

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

    def open_files(self):
        options = QtWidgets.QFileDialog.Options()
        fileList, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select files", "",
                                                  "All Files (*);", options=options)
        if fileList:
            self.merge_files(fileList)

    def merge_files(self, files=[]):
        for file in files:
            assets.merge_file(file, self.work_env_id, "Manually merged file", 0)
        gui_server.refresh_ui()

    def change_work_env(self, work_env_id):
        self.check_existence_thread.running = False
        self.version_list_ids = dict()
        self.version_icon_ids = dict()
        self.list_view.clear()
        self.icon_view.clear()
        self.work_env_id = work_env_id
        self.refresh_camera_button()
        self.refresh()

    def refresh_camera_button(self):
        if self.work_env_id:
            stage = assets.get_stage_data_from_work_env_id(self.work_env_id, 'name')
            if stage in assets_vars._camera_export_stages_:
                self.batch_camera_button.setVisible(True)
            else:
                self.batch_camera_button.setVisible(False)
        else:
            self.batch_camera_button.setVisible(False)

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
        start_time = time.time()
        if self.isVisible():
            self.refresh_list_view()
            self.refresh_icons_view()
            self.update_search()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def refresh_list_view(self):
        if self.list_mode:
            if self.work_env_id is not None and self.work_env_id != 0:
                software_name = project.get_work_env_data(self.work_env_id, 'name')
                software_icon = QtGui.QIcon(ressources._sofwares_icons_dic_[software_name])

                versions_rows = project.get_work_versions(self.work_env_id)
                project_versions_id = []
                if versions_rows is not None:
                    self.hide_info_mode()
                    for version_row in versions_rows:
                        project_versions_id.append(version_row['id'])
                        if version_row['id'] not in self.version_list_ids.keys():
                            version_item = custom_version_tree_item(version_row, software_icon, self.list_view.invisibleRootItem())
                            self.version_list_ids[version_row['id']] = version_item
                        else:
                            self.version_list_ids[version_row['id']].refresh(version_row)

                version_list_ids = list(self.version_list_ids.keys())
                for version_id in version_list_ids:
                    if version_id not in project_versions_id:
                        self.remove_tree_version(version_id)
                self.check_existence_thread.update_versions_rows(versions_rows)
            elif self.work_env_id is None:
                self.show_info_mode("Init the work environment\nto create the first version !", ressources._init_work_env_info_image_)
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()

    def refresh_icons_view(self):
        if self.icon_mode:
            if self.work_env_id is not None and self.work_env_id != 0:
                versions_rows = project.get_work_versions(self.work_env_id)
                project_versions_id = []
                if versions_rows is not None:
                    self.hide_info_mode()
                    for version_row in versions_rows:
                        project_versions_id.append(version_row['id'])
                        if version_row['id'] not in self.version_icon_ids.keys():
                            version_item = custom_version_icon_item(version_row)
                            self.icon_view.addItem(version_item)
                            self.version_icon_ids[version_row['id']] = version_item
                version_icon_ids = list(self.version_icon_ids.keys())
                for version_id in version_icon_ids:
                    if version_id not in project_versions_id:
                        self.remove_icon_version(version_id)
                self.check_existence_thread.update_versions_rows(versions_rows)
            elif self.work_env_id is None:
                self.show_info_mode("Init the work environment\nto create the first version !", ressources._init_work_env_info_image_)
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()

    def missing_file(self, version_id):
        if self.list_mode:
            if version_id in self.version_list_ids.keys():
                self.version_list_ids[version_id].set_missing()
        elif self.icon_mode:
            if version_id in self.version_icon_ids.keys():
                self.version_icon_ids[version_id].set_missing()

    def not_missing_file(self, version_id):
        if self.list_mode:
            if version_id in self.version_list_ids.keys():
                self.version_list_ids[version_id].set_not_missing()
        elif self.icon_mode:
            if version_id in self.version_icon_ids.keys():
                self.version_icon_ids[version_id].set_not_missing()

    def hide_all(self):
        if self.list_mode:
            for version_id in self.version_list_ids.keys():
                self.version_list_ids[version_id].setHidden(True)
        elif self.icon_mode:
            for version_id in self.version_icon_ids.keys():
                self.version_icon_ids[version_id].setHidden(True)

    def show_all(self):
        if self.list_mode:
            for version_id in self.version_list_ids.keys():
                self.version_list_ids[version_id].setHidden(False)
        elif self.icon_mode:
            for version_id in self.version_icon_ids.keys():
                self.version_icon_ids[version_id].setHidden(False)

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.hide_all()
            search_column = 'name'
            if ':' in search_data:
                if search_data.split(':')[0] == 'comment':
                    search_column = 'comment'
                    search_data = search_data.split(':')[-1]
                elif search_data.split(':')[0] == 'user':
                    search_column = 'creation_user'
                    search_data = search_data.split(':')[-1]
            self.search_thread.update_search(self.work_env_id, search_data, search_column)
        else:
            self.show_all()

    def add_search_version(self, version_id):
        if self.list_mode:
            if version_id in self.version_list_ids.keys():
                self.version_list_ids[version_id].setHidden(False)
        elif self.icon_mode:
            if version_id in self.version_icon_ids.keys():
                self.version_icon_ids[version_id].setHidden(False)

    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))
        self.icon_view_scrollBar.rangeChanged.connect(lambda: self.icon_view_scrollBar.setValue(self.icon_view_scrollBar.maximum()))

        self.list_view.itemSelectionChanged.connect(self.version_changed)
        self.list_view.itemDoubleClicked.connect(self.launch)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.icon_view.itemSelectionChanged.connect(self.version_changed)
        self.icon_view.itemDoubleClicked.connect(self.launch)
        self.icon_view.itemSelectionChanged.connect(self.refresh_infos)
        self.icon_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.archive_button.clicked.connect(self.archive)
        self.manual_merge_button.clicked.connect(self.open_files)
        self.batch_button.clicked.connect(self.batch_export)
        self.batch_camera_button.clicked.connect(self.batch_export_camera)
        self.duplicate_button.clicked.connect(self.duplicate_version)
        self.new_version_button.clicked.connect(self.add_empty_version)
        self.folder_button.clicked.connect(self.open_folder)
        self.toggle_view_button.clicked.connect(self.toggle_view)
        self.launch_button.clicked.connect(self.launch)
        self.comment_button.clicked.connect(self.modify_comment)

        self.check_existence_thread.missing_file_signal.connect(self.missing_file)
        self.check_existence_thread.not_missing_file_signal.connect(self.not_missing_file)

        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.id_signal.connect(self.add_search_version)

    def batch_export(self):
        selection = self.get_selection()
        version_id = None
        if len(selection) == 1:
            version_id = selection[0].version_row['id']
        elif len(selection) == 0:
            last_version_id = project.get_last_work_version(self.work_env_id, 'id')
            if last_version_id:
                version_id = last_version_id[0]
        if version_id:
            domain = assets.get_domain_data_from_work_env_id(self.work_env_id, 'name')
            stage = assets.get_stage_data_from_work_env_id(self.work_env_id, 'name')
            self.batch_settings_widget = batch_settings_widget.batch_settings_widget(self.work_env_id, stage)
            if self.batch_settings_widget.exec_() == QtWidgets.QDialog.Accepted:
                settings_dic = dict()
                settings_dic['frange'] = self.batch_settings_widget.frange
                settings_dic['refresh_assets'] = self.batch_settings_widget.refresh_assets
                settings_dic['nspace_list'] = self.batch_settings_widget.nspace_list
                subtasks_library.batch_export(version_id, settings_dic)

    def batch_export_camera(self):
        selection = self.get_selection()
        version_id = None
        if len(selection) == 1:
            version_id = selection[0].version_row['id']
        elif len(selection) == 0:
            last_version_id = project.get_last_work_version(self.work_env_id, 'id')
            if last_version_id:
                version_id = last_version_id[0]
        if version_id:
            domain = assets.get_domain_data_from_work_env_id(self.work_env_id, 'name')
            stage = assets.get_stage_data_from_work_env_id(self.work_env_id, 'name')
            self.batch_settings_widget = batch_settings_widget.batch_settings_widget(self.work_env_id, 'camera')
            if self.batch_settings_widget.exec_() == QtWidgets.QDialog.Accepted:
                settings_dic = dict()
                settings_dic['frange'] = self.batch_settings_widget.frange
                settings_dic['refresh_assets'] = self.batch_settings_widget.refresh_assets
                settings_dic['nspace_list'] = self.batch_settings_widget.nspace_list
                settings_dic['camera'] = True
                subtasks_library.batch_export(version_id, settings_dic)

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

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

        self.list_view.setHeaderLabels(['Version', 'Software', 'User', 'Date', 'Comment', 'File'])
        self.list_view.header().resizeSection(3, 150)
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

        self.versions_count_label = QtWidgets.QLabel()
        self.versions_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.versions_count_label)

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
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye"')
        self.buttons_layout.addWidget(self.search_bar)

        self.toggle_view_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.toggle_view_button, "Switch to list view")
        self.toggle_view_button.setFixedSize(35,35)
        self.toggle_view_button.setIconSize(QtCore.QSize(25,25))
        self.toggle_view_button.setIcon(QtGui.QIcon(ressources._tool_icon_view_))
        self.buttons_layout.addWidget(self.toggle_view_button)

        self.manual_merge_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.manual_merge_button, "Manually merge a file")
        self.manual_merge_button.setFixedSize(35,35)
        self.manual_merge_button.setIconSize(QtCore.QSize(25,25))
        self.manual_merge_button.setIcon(QtGui.QIcon(ressources._tool_manually_publish_))
        self.buttons_layout.addWidget(self.manual_merge_button)

        self.batch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.batch_button, "Batch export")
        self.batch_button.setFixedSize(35,35)
        self.batch_button.setIconSize(QtCore.QSize(25,25))
        self.batch_button.setIcon(QtGui.QIcon(ressources._tool_batch_publish_))
        self.buttons_layout.addWidget(self.batch_button)

        self.batch_camera_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.batch_camera_button, "Batch export cameras")
        self.batch_camera_button.setFixedSize(35,35)
        self.batch_camera_button.setIconSize(QtCore.QSize(25,25))
        self.batch_camera_button.setIcon(QtGui.QIcon(ressources._tool_batch_camera_))
        self.buttons_layout.addWidget(self.batch_camera_button)

        self.comment_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.comment_button, "Modify comment")
        self.comment_button.setFixedSize(35,35)
        self.comment_button.setIconSize(QtCore.QSize(25,25))
        self.comment_button.setIcon(QtGui.QIcon(ressources._tool_comment_))
        self.buttons_layout.addWidget(self.comment_button)

        self.launch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.launch_button, "Launch selection")
        self.launch_button.setFixedSize(35,35)
        self.launch_button.setIconSize(QtCore.QSize(25,25))
        self.launch_button.setIcon(QtGui.QIcon(ressources._launch_icon_))
        self.buttons_layout.addWidget(self.launch_button)

        self.duplicate_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.duplicate_button, "Duplicate selection")
        self.duplicate_button.setFixedSize(35,35)
        self.duplicate_button.setIconSize(QtCore.QSize(25,25))
        self.duplicate_button.setIcon(QtGui.QIcon(ressources._tool_duplicate_))
        self.buttons_layout.addWidget(self.duplicate_button)

        self.new_version_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.new_version_button, "Create empty version")
        self.new_version_button.setFixedSize(35,35)
        self.new_version_button.setIconSize(QtCore.QSize(25,25))
        self.new_version_button.setIcon(QtGui.QIcon(ressources._tool_add_))
        self.buttons_layout.addWidget(self.new_version_button)

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
        empty_version_action = menu.addAction(QtGui.QIcon(ressources._tool_add_), 'Create new empty version')
        merge_action = menu.addAction(QtGui.QIcon(ressources._tool_manually_publish_), 'Manually merge a file')
        duplicate_action = None
        archive_action = None
        comment_action = None
        batch_action = None
        if len(selection)>=1:
            duplicate_action = menu.addAction(QtGui.QIcon(ressources._tool_duplicate_), 'Duplicate version(s)')
            archive_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Archive version(s)')
            comment_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Modify comment')
        launch_action = None
        if len(selection)==1:
            launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), 'Launch version')
            batch_action = menu.addAction(QtGui.QIcon(ressources._tool_batch_publish_), 'Batch export version')

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == folder_action:
                self.open_folder()
            elif action == empty_version_action:
                self.add_empty_version()
            elif action == duplicate_action:
                self.duplicate_version()
            elif action == archive_action:
                self.archive()
            elif action == launch_action:
                self.launch()
            elif action == comment_action:
                self.modify_comment()
            elif action == merge_action:
                self.open_files()
            elif action == batch_action:
                self.batch_export()

    def modify_comment(self):
        items = self.get_selection()
        if items is not None:
            if len(items) > 0:
                self.comment_widget = comment_widget.comment_widget()
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    comment = self.comment_widget.comment
                    for item in items:
                        project.modify_version_comment(item.version_row['id'], comment)
                    gui_server.refresh_ui()

    def version_changed(self):
        selection = self.get_selection()
        if len(selection) == 1:
            if selection[0] is not None:
                self.version_changed_signal.emit(selection[0].version_row['name'])

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
        user.user().add_context(user_vars._versions_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._versions_context_)
        if context_dic is not None and context_dic != dict():
            if context_dic['view_mode'] == 'icon':
                self.set_view_as_icon_mode()
            elif context_dic['view_mode'] == 'list':
                self.set_view_as_list_mode()

    def get_number(self):
        number = 0
        if self.icon_mode:
            number = len(self.version_icon_ids)
        elif self.list_mode:
            number = len(self.version_list_ids)
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
                    self.version_icon_ids[item.version_row['id']].setSelected(True)
                elif self.list_mode:
                    self.version_list_ids[item.version_row['id']].setSelected(True)

    def clear_selection(self):
        for version_id in self.version_icon_ids.keys():
            self.version_icon_ids[version_id].setSelected(False)
        for version_id in self.version_list_ids.keys():
            self.version_list_ids[version_id].setSelected(False)

    def duplicate_version(self):
        selection = self.get_selection()
        if selection is not None:
            for item in selection:
                assets.duplicate_version(item.version_row['id'], f"Duplicate from version {item.version_row['name']}")
            gui_server.refresh_ui()

    def launch(self):
        items = self.get_selection()
        if items is not None:
            if len(items) == 1:
                launch.launch_work_version(items[0].version_row['id'])
                gui_server.refresh_ui()

    def archive(self):
        items = self.get_selection()
        if items is not None:
            if items!=[]:
                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                    version_ids = []
                    for item in items:
                        version_ids.append(item.version_row['id'])
                    subtasks_library.archive_versions(version_ids)

    def refresh_infos(self):
        self.versions_count_label.setText(f"{self.get_number()} versions -")
        selection = self.get_selection()
        if selection is not None:
            number = len(selection)
        else:
            number = 0
        self.selection_count_label.setText(f"{number} selected")

    def remove_tree_version(self, version_id):
        if version_id in self.version_list_ids.keys():
            item = self.version_list_ids[version_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.version_list_ids[version_id]

    def remove_icon_version(self, version_id):
        if version_id in self.version_icon_ids.keys():
            item = self.version_icon_ids[version_id]
            self.icon_view.takeItem(self.icon_view.row(item))
            del self.version_icon_ids[version_id]

    def add_empty_version(self):
        if self.work_env_id is not None:
            if assets.add_version(self.work_env_id, 'Empty version', 0):
                gui_server.refresh_ui()

    def open_folder(self):
        if self.work_env_id is not None:
            path_utils.startfile(assets.get_work_env_path(self.work_env_id))

class custom_version_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, version_row, software_icon, parent=None):
        super(custom_version_tree_item, self).__init__(parent)
        self.software_icon = software_icon
        self.version_row = version_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.version_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setIcon(1, self.software_icon)
        self.setText(2, self.version_row['creation_user'])
        day, hour = tools.convert_time(self.version_row['creation_time'])
        self.setText(3, f"{day} - {hour}")
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('gray')))
        self.setText(4, self.version_row['comment'])
        self.setText(5, os.path.basename(self.version_row['file_path']))

    def set_missing(self):
        self.setForeground(5, QtGui.QBrush(QtGui.QColor('#f79360')))

    def set_not_missing(self):
        self.setForeground(5, QtGui.QBrush(QtGui.QColor('#9ce87b')))

    def refresh(self, version_row):
        self.version_row = version_row
        self.fill_ui()

class custom_version_icon_item(QtWidgets.QListWidgetItem):
    def __init__(self, version_row, parent=None):
        super(custom_version_icon_item, self).__init__(parent)
        self.version_row = version_row
        self.fill_ui()

    def fill_ui(self):
        icon = QtGui.QIcon()
        
        pixmap = QtGui.QPixmap(self.version_row['thumbnail_path'])
        icon.addPixmap(pixmap, QtGui.QIcon.Normal)
        icon.addPixmap(pixmap, QtGui.QIcon.Selected)
        if not path_utils.isfile(self.version_row['thumbnail_path']):
            default_icon = QtGui.QIcon(ressources._no_screenshot_small_)
            icon.addPixmap(default_icon.pixmap(200), QtGui.QIcon.Normal)
            icon.addPixmap(default_icon.pixmap(200), QtGui.QIcon.Selected)

        self.setIcon(icon)
        self.setText(f"{self.version_row['name']} - {self.version_row['creation_user']}")
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
        self.versions_rows = None
        self.running = True

    def run(self):
        if self.versions_rows is not None:
            for version_row in self.versions_rows:
                if not path_utils.isfile(version_row['file_path']):
                    self.missing_file_signal.emit(version_row['id'])
                else:
                    self.not_missing_file_signal.emit(version_row['id'])
                if not self.running:
                    break

    def update_versions_rows(self, versions_rows):
        self.running = False
        self.versions_rows = versions_rows
        self.running = True
        self.start()

class search_thread(QtCore.QThread):

    id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, work_env_id, search_data, search_column):
        self.running = False
        self.work_env_id = work_env_id
        self.search_data = search_data
        self.search_column = search_column
        self.running = True
        self.start()

    def run(self):
        versions_ids = project.search_version(self.search_data, 
                                                self.work_env_id, 
                                                column_to_search=self.search_column,
                                                column='id')
        for version_id in versions_ids:
            if not self.running:
                break
            self.id_signal.emit(version_id)
