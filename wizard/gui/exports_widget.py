# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import json
import time
import os
import traceback
import copy
import logging

# Wizard modules
from wizard.core import launch
from wizard.core import assets
from wizard.core import project
from wizard.core import tools
from wizard.core import subtasks_library
from wizard.core import path_utils
from wizard.core import repository
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import confirm_widget
from wizard.gui import manual_export_widget
from wizard.gui import drop_files_widget
from wizard.gui import comment_widget
from wizard.gui import destination_manager
from wizard.gui import tag_label
from wizard.gui import current_asset_viewer

logger = logging.getLogger(__name__)

class exports_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(exports_widget, self).__init__(parent)

        self.search_thread = search_thread()

        self.icons_dic = dict()
        self.icons_dic['modeling'] = QtGui.QIcon(ressources._modeling_icon_)
        self.icons_dic['rigging'] = QtGui.QIcon(ressources._rigging_icon_)
        self.icons_dic['grooming'] = QtGui.QIcon(ressources._grooming_icon_)
        self.icons_dic['texturing'] = QtGui.QIcon(ressources._texturing_icon_)
        self.icons_dic['shading'] = QtGui.QIcon(ressources._shading_icon_)
        self.icons_dic['layout'] = QtGui.QIcon(ressources._layout_icon_)
        self.icons_dic['animation'] = QtGui.QIcon(ressources._animation_icon_)
        self.icons_dic['cfx'] = QtGui.QIcon(ressources._cfx_icon_)
        self.icons_dic['fx'] = QtGui.QIcon(ressources._fx_icon_)
        self.icons_dic['lighting'] = QtGui.QIcon(ressources._lighting_icon_)
        self.icons_dic['rendering'] = QtGui.QIcon(ressources._rendering_icon_)
        self.icons_dic['camera'] = QtGui.QIcon(ressources._camera_icon_)
        self.icons_dic['compositing'] = QtGui.QIcon(ressources._compositing_icon_)
        self.icons_dic['custom'] = QtGui.QIcon(ressources._custom_icon_)
        self.icons_dic['camrig'] = QtGui.QIcon(ressources._camera_rig_icon_)

        self.view_comment_widget = tag_label.view_comment_widget(self)

        self.stage_id = None
        self.export_versions_rows = None
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.check_existence_thread = check_existence_thread()
        self.destination_manager = None
        self.build_ui()
        self.start_timer()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def start_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.start(10000)

    def update_times_ago(self):
        for export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].update_time_ago()
        for export_id in self.export_ids.keys():
            self.export_ids[export_id].update_time_ago()

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

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.current_asset_viewer = current_asset_viewer.current_asset_viewer()
        self.main_layout.addWidget(self.current_asset_viewer)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setAnimated(1)
        self.list_view.setExpandsOnDoubleClick(0)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(10)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Export name', 'Version', 'User', 'Date', 'Comment', 'From', 'Format', 'Infos', 'Default', 'ID'])
        self.list_view.header().resizeSection(0, 150)
        self.list_view.header().resizeSection(3, 150)
        self.list_view.header().resizeSection(4, 250)
        self.list_view.header().resizeSection(5, 60)
        self.list_view.header().resizeSection(6, 60)
        self.list_view.header().resizeSection(8, 100)
        self.list_view.header().resizeSection(9, 40)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

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

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "j.smith", "retake eye", "houdini"')
        self.buttons_layout.addWidget(self.search_bar)

        self.manual_publish_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.manual_publish_button, "Manually add a file")
        self.manual_publish_button.setFixedSize(35,35)
        self.manual_publish_button.setIconSize(QtCore.QSize(25,25))
        self.manual_publish_button.setIcon(QtGui.QIcon(ressources._tool_manually_publish_))
        self.buttons_layout.addWidget(self.manual_publish_button)

        self.launch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.launch_button, "Launch related work version")
        self.launch_button.setFixedSize(35,35)
        self.launch_button.setIconSize(QtCore.QSize(25,25))
        self.launch_button.setIcon(QtGui.QIcon(ressources._launch_icon_))
        self.buttons_layout.addWidget(self.launch_button)

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open export folder")
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
        self.drop_widget.setText('Merge file as new export version')
        self.drop_widget.setVisible(0)

    def check_if_export_is_referenced(self, export_version_row):
        string = None
        if len(project.get_references_by_export_version(export_version_row['id'], 'id'))!=0:
            export_row = project.get_export_data(export_version_row['export_id'])
            stage_row = project.get_stage_data(export_version_row['stage_id'])
            asset_row = project.get_asset_data(stage_row['asset_id'])
            string = f"{asset_row['name']}/{stage_row['name']}/{export_row['name']}/{export_version_row['name']}"
        return string

    def archive(self):
        if not repository.is_admin():
            return
        selection = self.list_view.selectedItems()
        if selection is not None:
            if selection != []:

                # Check if exports are referenced somewhere
                referenced_items = []
                for item in selection:
                    if item.type == 'export_version':
                        string = self.check_if_export_is_referenced(item.export_version_row)
                        if string is not None and string not in referenced_items:
                            referenced_items.append(string)
                    elif item.type == 'export':
                        childs_ids = project.get_export_versions(item.export_row['id'], 'id')
                        for export_version_id in childs_ids:
                            export_version_row = project.get_export_version_data(export_version_id)
                            string = self.check_if_export_is_referenced(export_version_row)
                            if string is not None and string not in referenced_items:
                                referenced_items.append(string)

                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if len(referenced_items)!=0:
                    message = 'The following export versions are referenced in some scenes,\ndo you REALLY want to continue ?\n\n-'
                    message += ('\n-').join(referenced_items)
                    self.confirm_widget.set_important_message(message)
                    self.confirm_widget.set_security_sentence('archive anyway')

                if self.confirm_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:

                    export_ids = []
                    export_version_ids = []

                    for item in selection:
                        if item.type == 'export_version':
                            export_version_ids.append(item.export_version_row['id'])
                        elif item.type == 'export':
                            export_ids.append(item.export_row['id'])

                    if len(export_ids) > 0:
                        subtasks_library.archive_exports(export_ids)
                    if len(export_version_ids) > 0:
                        subtasks_library.archive_export_versions(export_version_ids)

    def open_folder(self):
        if self.stage_id is not None:
            folder = assets.get_stage_export_path(self.stage_id)
            selection = self.list_view.selectedItems()
            if selection is not None:
                if len(selection)==1:
                    if selection[0].type == 'export_version':
                        export_version_id = selection[0].export_version_row['id']
                        folder = assets.get_export_version_path(export_version_id)
                    elif selection[0].type == 'export':
                        export_id = selection[0].export_row['id']
                        folder = assets.get_export_path(export_id)
            if path_utils.isdir(folder):
                path_utils.startfile(folder)
            else:
                logger.warning(f"{folder} not found")

    def focus_on_work_version(self):
        selection = self.list_view.selectedItems()
        if len(selection)==1:
            if selection[0].type == 'export_version':
                if selection[0].export_version_row['work_version_id']:
                    gui_server.focus_work_version(selection[0].export_version_row['work_version_id'])
                else:
                    logger.warning(f"Export version {selection[0].export_version_row['name']}\nis not related to any work version")

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.search_thread.update_search(search_data, self.export_versions_rows)
        else:
            self.show_all()

    def hide_all(self):
        for export_id in self.export_ids.keys():
            self.export_ids[export_id].setHidden(1)
        for export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].setHidden(1)

    def show_all(self):
        for export_id in self.export_ids.keys():
            self.export_ids[export_id].setHidden(0)
        for export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].setHidden(0)

    def show_search_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            export_id = self.export_versions_ids[export_version_id].export_version_row['export_id']
            if export_id in self.export_ids.keys():
                self.export_ids[export_id].setHidden(False)
            self.export_versions_ids[export_version_id].setHidden(False)

    def hide_search_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].setHidden(True)
            export_id = self.export_versions_ids[export_version_id].export_version_row['export_id']
            if export_id in self.export_ids.keys():
                children_visibility_list = []
                for index in range(0, self.export_ids[export_id].childCount()-1):
                    children_visibility_list.append(self.export_ids[export_id].child(index).isHidden())
                if all(children_visibility_list):
                    self.export_ids[export_id].setHidden(True)
                else:
                    self.export_ids[export_id].setHidden(False)

    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)
        self.list_view.itemDoubleClicked.connect(self.open_folder)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)

        self.check_existence_thread.missing_file_signal.connect(self.missing_file)
        self.check_existence_thread.missing_folder_signal.connect(self.missing_folder)
        self.check_existence_thread.not_missing_file_signal.connect(self.not_missing_file)
        self.check_existence_thread.extension_signal.connect(self.extension_signal)

        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.show_id_signal.connect(self.show_search_version)
        self.search_thread.hide_id_signal.connect(self.hide_search_version)

        self.archive_button.clicked.connect(self.archive)
        self.manual_publish_button.clicked.connect(lambda:self.merge_files())
        self.folder_button.clicked.connect(self.open_folder)
        self.launch_button.clicked.connect(self.launch_work_version)

        self.timer.timeout.connect(self.update_times_ago)

    def refresh_infos(self):
        self.versions_count_label.setText(f"{len(self.export_ids)} exports / {len(self.export_versions_ids)} export versions -")
        selection = self.list_view.selectedItems()
        if selection is not None:
            number = len(selection)
        else:
            number = 0
        self.selection_count_label.setText(f"{number} selected")

    def refresh(self):
        QtWidgets.QApplication.processEvents()
        start_time = time.perf_counter()
        if self.isVisible():
            if self.stage_id is not None:
                self.setAcceptDrops(True)
                stage_name = project.get_stage_data(self.stage_id, 'name')
                stage_icon = QtGui.QIcon(self.icons_dic[stage_name])
                exports_rows = project.get_stage_export_childs(self.stage_id)
                project_export_id = []

                if exports_rows is not None:
                    if exports_rows != []:
                        self.hide_info_mode()
                        for export_row in exports_rows:
                            project_export_id.append(export_row['id'])
                            if export_row['id'] not in self.export_ids.keys():
                                export_item = custom_export_tree_item(export_row, stage_icon, 
                                                                self.list_view.invisibleRootItem())
                                export_item.setExpanded(1)
                                self.export_ids[export_row['id']] = export_item
                            else:
                                self.export_ids[export_row['id']].refresh(export_row)
                    else:
                        self.show_info_mode("No exports, create exports\nwithin softwares !", 
                                                                ressources._empty_info_image_)

                    project_export_versions_id = []
                    self.export_versions_rows = project.get_export_versions_by_stage(self.stage_id)
                    if self.export_versions_rows is not None:
                        if self.export_versions_rows != []:
                            for export_version_row in self.export_versions_rows:
                                project_export_versions_id.append(export_version_row['id'])
                                if export_version_row['id'] not in self.export_versions_ids.keys():
                                    if export_version_row['export_id'] in self.export_ids.keys():
                                        export_version_item = custom_export_version_tree_item(export_version_row,
                                                                    self.export_ids[export_version_row['export_id']])
                                        export_version_item.signal_handler.enter.connect(self.view_comment_widget.show_comment)
                                        export_version_item.signal_handler.leave.connect(self.view_comment_widget.close)
                                        export_version_item.signal_handler.move_event.connect(self.view_comment_widget.move_ui)
                                    self.export_versions_ids[export_version_row['id']] = export_version_item
                                else:
                                    self.export_versions_ids[export_version_row['id']].refresh(export_version_row)
                            self.check_existence_thread.update_versions_rows(self.export_versions_rows)


                    export_list_ids = list(self.export_ids.keys())
                    for export_id in export_list_ids:
                        if export_id not in project_export_id:
                            self.remove_export(export_id)
                    export_version_list_ids = list(self.export_versions_ids.keys())
                    for export_version_id in export_version_list_ids:
                        if export_version_id not in project_export_versions_id:
                            self.remove_export_version(export_version_id)

                    for export_id in self.export_ids.keys():
                        default_export_version = project.get_default_export_version(export_id)
                        if default_export_version:
                            self.export_ids[export_id].set_default_name(default_export_version['name'])
                            self.export_versions_ids[default_export_version['id']].set_default(True)

                else:
                    self.show_info_mode("No exports, create exports\nwithin softwares !",
                                                        ressources._empty_info_image_)

            else:
                self.show_info_mode("Select or create a stage\nin the project tree !",
                                                    ressources._select_stage_info_image_)
                self.setAcceptDrops(False)
        self.refresh_infos()
        self.update_refresh_time(start_time)
        if self.destination_manager is not None:
            self.destination_manager.refresh()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def extension_signal(self, tuple_signal):
        export_version_id = tuple_signal[0]
        extension = tuple_signal[-1]
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_extension(extension)

    def missing_file(self, tuple_signal):
        export_version_id = tuple_signal[0]
        number = tuple_signal[-1]
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_missing(number)

    def missing_folder(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_missing_folder()

    def not_missing_file(self, tuple_signal):
        export_version_id = tuple_signal[0]
        number = tuple_signal[-1]
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_not_missing(number)

    def remove_export_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            item = self.export_versions_ids[export_version_id]
            try:
                item.parent().removeChild(item)
            except RuntimeError:
                pass
            del self.export_versions_ids[export_version_id]

    def remove_export(self, export_id):
        if export_id in self.export_ids.keys():
            item = self.export_ids[export_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.export_ids[export_id]

    def context_menu_requested(self):
        menu = gui_utils.QMenu(self)
        selection = self.list_view.selectedItems()
        folder_action = menu.addAction(QtGui.QIcon(ressources._tool_folder_), 'Open folder')
        manual_action = menu.addAction(QtGui.QIcon(ressources._tool_manually_publish_), 'Manually add a file')
        archive_action = None
        launch_action = None
        set_default_action = None
        focus_version_action = None
        comment_action = None
        if len(selection)>=1:
            archive_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Archive version(s)')
        if len(selection)==1:
            launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), 'Launch related work version')
            destination_action = menu.addAction(QtGui.QIcon(ressources._destination_icon_), 'Open destination manager')
            focus_version_action = menu.addAction(QtGui.QIcon(ressources._tool_focus_), 'Focus on work version')
            if selection[0].type != 'export':
                set_default_action = menu.addAction(QtGui.QIcon(ressources._default_export_version_icon_), 'Set as default')
                comment_action = menu.addAction(QtGui.QIcon(ressources._tool_comment_), 'Modify comment')
            else:
                set_default_action = menu.addAction(QtGui.QIcon(ressources._default_export_version_icon_), 'Set default as always last')
        pos = QtGui.QCursor().pos()
        action = menu.exec(pos)
        if action is not None:
            if action == folder_action:
                self.open_folder()
            elif action == archive_action:
                self.archive()
            elif action == launch_action:
                self.launch_work_version()
            elif action == manual_action:
                self.merge_files()
            elif action == comment_action:
                self.modify_comment(pos)
            elif action == destination_action:
                self.open_destination_manager()
            elif action == set_default_action:
                self.set_default_export_version()
            elif action == focus_version_action:
                self.focus_on_work_version()

    def set_default_export_version(self):
        selection = self.list_view.selectedItems()
        if len(selection) == 1:
            item = selection[0]
            if item.type != 'export':
                project.set_default_export_version(item.export_version_row['export_id'],
                                                        item.export_version_row['id'])
            else:
                project.set_default_export_version(item.export_row['id'], None)
            gui_server.refresh_team_ui()

    def open_destination_manager(self):
        selection = self.list_view.selectedItems()
        if len(selection) == 1:
            item = selection[0]
            if item.type == 'export':
                export_id = item.export_row['id']
            else:
                export_id = item.parent().export_row['id']
            self.destination_manager = destination_manager.destination_manager(export_id)  
            self.destination_manager.show()  

    def modify_comment(self, pos=None):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if len(selection) > 0:
                old_comment = ''
                if len(selection) == 1:
                    old_comment = selection[0].export_version_row['comment']
                self.comment_widget = comment_widget.comment_widget(old_comment=old_comment, pos=pos)
                if self.comment_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    comment = self.comment_widget.comment
                    for item in selection:
                        assets.modify_export_version_comment(item.export_version_row['id'], comment)
                    gui_server.refresh_team_ui()

    def launch_work_version(self):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if len(selection) == 1:
                item = selection[0]
                if item.type == 'export_version':
                    work_version_id = item.export_version_row['work_version_id']
                    if work_version_id is not None:
                        launch.launch_work_version(work_version_id)
                        gui_server.refresh_ui()

    def merge_files(self, files=[]):
        if self.stage_id is not None:
            self.manual_export_widget = manual_export_widget.manual_export_widget()
            self.manual_export_widget.add_files(files)

            stage_row = project.get_stage_data(self.stage_id)
            asset_row = project.get_asset_data(stage_row['asset_id'])

            self.manual_export_widget.set_export_name('main')

            if self.manual_export_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                files = self.manual_export_widget.files
                export_name = self.manual_export_widget.export_name
                comment = self.manual_export_widget.comment
                if comment != None and comment != '':
                    analyse_comment = True
                else:
                    analyse_comment = False
                if assets.merge_file_as_export_version(export_name, files, self.stage_id, comment, analyse_comment=analyse_comment):
                    gui_server.refresh_ui()

    def focus_export_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            item = self.export_versions_ids[export_version_id]
            item.parent().setExpanded(1)
            self.list_view.scrollToItem(item)
            self.list_view.setCurrentItem(item)

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def change_stage(self, stage_id):
        self.check_existence_thread.running = False
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.list_view.clear()
        self.stage_id = stage_id
        self.current_asset_viewer.refresh('stage', stage_id)
        self.refresh()
        
class custom_export_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_row, stage_icon, parent=None):
        super(custom_export_tree_item, self).__init__(parent)
        self.export_row = export_row
        self.stage_icon = stage_icon
        self.type = 'export'
        self.fill_ui()
        self.update_time_ago()

    def update_time_ago(self):
        self.setText(3, tools.time_ago_from_timestamp(self.export_row['creation_time']))

    def fill_ui(self):
        self.setText(0, self.export_row['name'])
        self.setIcon(0, self.stage_icon)
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setText(2, self.export_row['creation_user'])
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('gray')))
        self.setForeground(8, QtGui.QBrush(QtGui.QColor('gray')))
        self.setText(9, str(self.export_row['id']))
        self.setForeground(9, QtGui.QBrush(QtGui.QColor('gray')))

    def set_default_name(self, name):
        if self.export_row['default_export_version'] is None:
            self.setText(8, 'Always last')
        else:
            self.setText(8, name)

    def refresh(self, export_row):
        self.export_row = export_row
        self.fill_ui()

class custom_export_version_tree_item(QtWidgets.QTreeWidgetItem):

    def __init__(self, export_version_row, parent=None):
        super(custom_export_version_tree_item, self).__init__(parent)
        self.export_version_row = export_version_row
        self.type = 'export_version'
        self.comment_label = tag_label.tag_label()
        self.comment_label.setNoMultipleLines()
        self.treeWidget().setItemWidget(self, 4, self.comment_label)
        self.fill_ui()
        self.update_time_ago()
        self.signal_handler = signal_handler()
        self.connect_functions()

    def show_comment(self):
        if self.comment_label.isActiveWindow():
            self.signal_handler.enter.emit(self.export_version_row['comment'], self.export_version_row['creation_user'])

    def connect_functions(self):
        self.comment_label.enter.connect(self.show_comment)
        self.comment_label.leave.connect(self.signal_handler.leave.emit)
        self.comment_label.move_event.connect(self.signal_handler.move_event.emit)

    def update_time_ago(self):
        self.setText(3, tools.time_ago_from_timestamp(self.export_version_row['creation_time']))

    def fill_ui(self):
        self.setText(1, self.export_version_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setIcon(0, QtGui.QIcon(ressources._exports_icon_))
        self.setFont(1, bold_font)
        self.setText(2, self.export_version_row['creation_user'])
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('gray')))
        self.comment_label.setText(self.export_version_row['comment'])
        if self.export_version_row['software'] is not None:
            self.setIcon(5, QtGui.QIcon(ressources._softwares_icons_dic_[self.export_version_row['software']]))
        else:
            self.setIcon(5, QtGui.QIcon(ressources._manual_export_))
        files = json.loads(self.export_version_row['files'])
        if len(files) > 0:
            extension = files[0].split('.')[-1]
        else:
            extension = ''
        self.setText(6, extension)
        self.setText(9, str(self.export_version_row['id']))
        self.setForeground(9, QtGui.QBrush(QtGui.QColor('gray')))

    def refresh(self, export_version_row):
        self.export_version_row = export_version_row
        self.set_default(False)
        self.fill_ui()

    def set_default(self, default):
        if default:
            self.setIcon(8, QtGui.QIcon(ressources._default_export_version_icon_))
        else:
            self.setIcon(8, QtGui.QIcon(''))

    def set_extension(self, extension):
        self.setText(6, extension)

    def set_missing(self, number):
        self.setText(7, f'missing {number} files')
        self.setForeground(7, QtGui.QBrush(QtGui.QColor('#f79360')))

    def set_missing_folder(self):
        self.setText(7, f"missing folder")
        self.setForeground(7, QtGui.QBrush(QtGui.QColor('#ff4b3b')))

    def set_not_missing(self, number):
        if number > 0:
            self.setText(7, f'{number} files')
        else:
            self.setText(7, '')
        self.setForeground(7, QtGui.QBrush(QtGui.QColor('#9ce87b')))

class signal_handler(QtCore.QObject):

    enter = pyqtSignal(str, str)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_handler, self).__init__(parent)

class check_existence_thread(QtCore.QThread):

    missing_file_signal = pyqtSignal(tuple)
    missing_folder_signal = pyqtSignal(int)
    not_missing_file_signal = pyqtSignal(tuple)
    extension_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(check_existence_thread, self).__init__(parent)
        self.export_versions_rows = None
        self.running = True

    def run(self):
        try:
            if self.export_versions_rows is not None:
                for export_version_row in self.export_versions_rows:
                    files_list = json.loads(export_version_row['files'])
                    export_version_dir = assets.get_export_version_path(export_version_row['id'])
                    if not path_utils.isdir(export_version_dir):
                        self.missing_folder_signal.emit(export_version_row['id'])
                        continue
                    if files_list == []:
                        missing_files = 0
                        export_version_dir = assets.get_export_version_path(export_version_row['id'])
                        files_list = os.listdir(export_version_dir)
                        if len(files_list) > 0:
                            self.extension_signal.emit((export_version_row['id'], files_list[0].split('.')[-1]))
                    else:
                        missing_files = 0
                        for file in files_list:
                            if not path_utils.isfile(file):
                                missing_files += 1
                    if not self.running:
                        break

                    if missing_files:
                        self.missing_file_signal.emit((export_version_row['id'], missing_files))
                    else:
                        self.not_missing_file_signal.emit((export_version_row['id'], len(files_list)))
                    if not self.running:
                        break
        except:
            logger.debug(str(traceback.format_exc()))

    def update_versions_rows(self, export_versions_rows):
        self.running = False
        self.export_versions_rows = export_versions_rows
        self.running = True
        self.start()

class search_thread(QtCore.QThread):

    show_id_signal = pyqtSignal(int)
    hide_id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, search_data, export_versions_rows):
        self.running = False
        self.search_data = search_data
        self.export_versions_rows = copy.deepcopy(export_versions_rows)
        self.running = True
        self.start()

    def run(self):
        try:
            keywords = self.search_data.split('&')
            for export_version_row in self.export_versions_rows:

                export_version_id = export_version_row['id']
                del export_version_row['id']
                del export_version_row['creation_time']
                del export_version_row['variant_id']
                del export_version_row['stage_id']
                del export_version_row['work_version_id']
                del export_version_row['work_version_thumbnail_path']
                del export_version_row['export_id']

                values = list(export_version_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_id_signal.emit(export_version_id)
                else:
                    self.hide_id_signal.emit(export_version_id)
        except:
            logger.debug(str(traceback.format_exc()))

