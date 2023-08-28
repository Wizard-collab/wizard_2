# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging
import copy
import traceback
import json

# Wizard gui modules
from wizard.gui import search_reference_widget
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import comment_widget
from wizard.gui import tag_label
from wizard.gui import current_asset_viewer

# Wizard modules
from wizard.core import assets
from wizard.core import launch
from wizard.core import path_utils
from wizard.core import project
from wizard.vars import ressources
from wizard.vars import assets_vars

logger = logging.getLogger(__name__)

class references_widget(QtWidgets.QWidget):

    focus_export = pyqtSignal(int)
    focus_on_group_signal = pyqtSignal(int)

    def __init__(self, context='work_env', parent=None):
        super(references_widget, self).__init__(parent)
        self.reference_infos_thread = reference_infos_thread()
        self.search_thread = search_thread()
        self.view_comment_widget = tag_label.view_comment_widget(self)

        self.context = context
        self.group_item = None
        self.parent_instance_id = None
        self.reference_ids = dict()
        self.referenced_group_ids = dict()
        self.stage_dic = dict()
        self.quick_import_buttons = dict()

        self.build_ui()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def connect_functions(self):
        self.search_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Tab'), self)
        self.search_sc.activated.connect(self.search_reference)
        self.reference_infos_thread.reference_infos_signal.connect(self.update_item_infos)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)
        self.list_view.itemDoubleClicked.connect(self.item_double_clicked)
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.remove_selection_button.clicked.connect(self.remove_selection)
        self.update_button.clicked.connect(self.update_selection)
        self.add_reference_button.clicked.connect(self.search_reference)

        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.show_ref_signal.connect(self.show_search_reference)
        self.search_thread.hide_ref_signal.connect(self.hide_search_reference)
        self.search_thread.show_group_signal.connect(self.show_search_referenced_group)
        self.search_thread.hide_group_signal.connect(self.hide_search_referenced_group)

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.search_thread.update_search(self.reference_rows, self.referenced_groups_rows, search_data)
        else:
            self.show_all()

    def show_search_reference(self, reference_id):
        if reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].setHidden(False)
            self.reference_ids[reference_id].parent().setHidden(False)

    def show_search_referenced_group(self, referenced_group_id):
        if referenced_group_id in self.referenced_group_ids.keys():
            self.referenced_group_ids[referenced_group_id].setHidden(False)
            self.referenced_group_ids[referenced_group_id].parent().setHidden(False)

    def hide_search_reference(self, reference_id):
        if reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].setHidden(True)

            parent_item = self.reference_ids[reference_id].parent()

            children_visibility_list = []
            for index in range(0, parent_item.childCount()-1):
                children_visibility_list.append(parent_item.child(index).isHidden())
            if all(children_visibility_list):
                parent_item.setHidden(True)
            else:
                parent_item.setHidden(False)

    def hide_search_referenced_group(self, referenced_group_id):
        if referenced_group_id in self.referenced_group_ids.keys():
            self.referenced_group_ids[referenced_group_id].setHidden(True)

            parent_item = self.referenced_group_ids[referenced_group_id].parent()

            children_visibility_list = []
            for index in range(0, parent_item.childCount()-1):
                children_visibility_list.append(parent_item.child(index).isHidden())
            if all(children_visibility_list):
                parent_item.setHidden(True)
            else:
                parent_item.setHidden(False)

    def show_all(self):
        for reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].setHidden(False)
        for stage in self.stage_dic.keys():
            self.stage_dic[stage].setHidden(False)
        for referenced_group_id in self.referenced_group_ids.keys():
            self.referenced_group_ids[referenced_group_id].setHidden(False)
        if self.group_item:
            self.group_item.setHidden(False)

    def update_item_infos(self, infos_list):
        reference_id = infos_list[0]
        if reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].update_item_infos(infos_list)

    def search_reference(self):
        if self.parent_instance_id is not None and self.parent_instance_id != 0:
            self.search_reference_widget = search_reference_widget.search_reference_widget(self.context, self)
            self.search_reference_widget.stage_ids_signal.connect(self.create_references_from_stage_ids)
            self.search_reference_widget.groups_ids_signal.connect(self.create_referenced_groups)
            self.search_reference_widget.show()

            if self.context == 'work_env':
                variant_row = project.get_variant_data(project.get_work_env_data(self.parent_instance_id, 'variant_id'))
                stage_row = project.get_stage_data(variant_row['stage_id'])
                asset_row = project.get_asset_data(stage_row['asset_id'])
                category_row = project.get_category_data(asset_row['category_id'])
                self.search_reference_widget.search_asset(f"{category_row['name']}/{asset_row['name']}")
            else:
                self.search_reference_widget.search_asset(f"")

    def create_references_from_stage_ids(self, stage_ids):
        if self.parent_instance_id is not None:
            for stage_id in stage_ids:
                if self.context == 'work_env':
                    if assets.create_references_from_stage_id(self.parent_instance_id, stage_id):
                        gui_server.refresh_team_ui()
                else:
                    if assets.create_grouped_references_from_stage_id(self.parent_instance_id, stage_id):
                        gui_server.refresh_team_ui()

    def quick_import(self, stage):
        assets.quick_reference(self.parent_instance_id, stage)
        gui_server.refresh_team_ui()

    def create_referenced_groups(self, groups_ids):
        if self.context == 'work_env':
            for group_id in groups_ids:
                assets.create_referenced_group(self.parent_instance_id, group_id)
            gui_server.refresh_team_ui()

    def change_work_env(self, work_env_id):
        self.reference_ids = dict()
        self.referenced_group_ids = dict()
        self.stage_dic = dict()
        self.group_item = None
        self.list_view.clear()
        self.parent_instance_id = work_env_id
        if self.context == 'work_env':
            self.current_asset_viewer.refresh('work_env', work_env_id)
        self.refresh()

    def refresh(self, start_time=None):
        QtWidgets.QApplication.processEvents()
        start_time = time.perf_counter()
        if self.isVisible():
            self.update_quick_import_buttons()
            if self.parent_instance_id is not None and self.parent_instance_id != 0:
                if self.context == 'work_env':
                    self.reference_rows = project.get_references(self.parent_instance_id)
                    self.referenced_groups_rows = project.get_referenced_groups(self.parent_instance_id)
                else:
                    self.reference_rows = project.get_grouped_references(self.parent_instance_id)
                    self.referenced_groups_rows = []
                if (self.reference_rows is not None) or (self.referenced_groups_rows is not None):
                    self.hide_info_mode()
                    if (len(self.reference_rows) >=1) or (len(self.referenced_groups_rows) >=1):
                        self.add_references_rows(self.reference_rows)
                        self.add_referenced_groups_rows(self.referenced_groups_rows)
                    else:
                        self.show_info_mode("No references\nPress Tab to create a reference !", ressources._references_info_image_)
            elif self.parent_instance_id is None:
                if self.context == 'work_env':
                    self.show_info_mode("You need to init the work environment\nto create references...", ressources._init_work_env_info_image_)
                else:
                    self.show_info_mode("You need to add a group\nto create references...", ressources._add_group_info_image_)
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()
        self.update_refresh_time(start_time)

    def add_references_rows(self, reference_rows):
        project_references_id = []
        for reference_row in reference_rows:
            project_references_id.append(reference_row['id'])
            if reference_row['id'] not in self.reference_ids.keys():
                stage = reference_row['stage']
                if stage not in self.stage_dic.keys():
                    stage_item = custom_stage_tree_item(stage, self.list_view.invisibleRootItem())
                    self.stage_dic[stage] = stage_item
                reference_item = custom_reference_tree_item(reference_row, self.context, self.stage_dic[stage])
                reference_item.signal_handler.enter.connect(self.view_comment_widget.show_comment)
                reference_item.signal_handler.leave.connect(self.view_comment_widget.close)
                reference_item.signal_handler.move_event.connect(self.view_comment_widget.move_ui)
                self.reference_ids[reference_row['id']] = reference_item
            else:
                self.reference_ids[reference_row['id']].reference_row = reference_row
        references_list_ids = list(self.reference_ids.keys())
        for reference_id in references_list_ids:
            if reference_id not in project_references_id:
                self.remove_reference_item(reference_id)
        self.reference_infos_thread.update_references_rows(reference_rows)
        self.update_stages_items()

    def add_referenced_groups_rows(self, referenced_groups_rows):
        self.add_group_item()

        groups_ids = dict()
        groups_rows = project.get_groups()
        for group_row in groups_rows:
            groups_ids[group_row['id']] = group_row

        project_referenced_groups_id = []
        for referenced_group_row in referenced_groups_rows:
            project_referenced_groups_id.append(referenced_group_row['id'])
            group_row = groups_ids[referenced_group_row['group_id']]
            if referenced_group_row['id'] not in self.referenced_group_ids.keys():
                referenced_group_item = custom_referenced_group_tree_item(referenced_group_row, group_row,
                                                            self.group_item)
                self.referenced_group_ids[referenced_group_row['id']] = referenced_group_item
            else:
                self.referenced_group_ids[referenced_group_row['id']].update(group_row)

        referenced_group_list_ids = list(self.referenced_group_ids.keys())
        for referenced_group_id in referenced_group_list_ids:
            if referenced_group_id not in project_referenced_groups_id:
                self.remove_referenced_group_item(referenced_group_id)
        self.update_group_item()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def remove_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                reference_id = selected_item.reference_row['id']
                if self.context == 'work_env':
                    assets.remove_reference(reference_id)
                else:
                    assets.remove_grouped_reference(reference_id)
            elif selected_item.type == 'group':
                referenced_group_id = selected_item.referenced_group_row['id']
                assets.remove_referenced_group(referenced_group_id)
        gui_server.refresh_team_ui()

    def update_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                reference_id = selected_item.reference_row['id']
                if self.context == 'work_env':
                    assets.set_reference_last_version(reference_id)
                else:
                    assets.set_grouped_reference_last_version(reference_id)
        gui_server.refresh_team_ui()

    def update_all(self):
        for reference_id in self.reference_ids.keys():
            if self.context == 'work_env':
                assets.set_reference_last_version(reference_id)
            else:
                assets.set_grouped_reference_last_version(reference_id)
        gui_server.refresh_team_ui()

    def launch_work_version(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                export_version_id = selected_item.reference_row['export_version_id']
                export_version_row = project.get_export_version_data(export_version_id)
                if export_version_row['work_version_id'] is not None:
                    launch.launch_work_version(export_version_row['work_version_id'])
        gui_server.refresh_team_ui()

    def focus_on_export_version(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                self.focus_export.emit(selected_item.reference_row['export_version_id'])

    def open_folder(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                path = assets.get_export_version_path(selected_item.reference_row['export_version_id'])
                path_utils.startfile(path)

    def declare_error(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                export_id = selected_item.reference_row['export_id']
                variant_id = project.get_export_data(export_id, 'variant_id')
                stage_id = project.get_variant_data(variant_id, 'stage_id')
                self.comment_widget = comment_widget.comment_widget()
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    assets.modify_stage_state(variant_id, 'error', self.comment_widget.comment)
                    gui_server.refresh_team_ui()

    def remove_reference_item(self, reference_id):
        if reference_id in self.reference_ids.keys():
            item = self.reference_ids[reference_id]
            item.parent().removeChild(item)
            del self.reference_ids[reference_id]

    def remove_referenced_group_item(self, referenced_group_id):
        if referenced_group_id in self.referenced_group_ids.keys():
            item = self.referenced_group_ids[referenced_group_id]
            item.parent().removeChild(item)
            del self.referenced_group_ids[referenced_group_id]

    def add_group_item(self):
        if self.group_item is None:
            self.group_item = custom_group_tree_item(self.list_view.invisibleRootItem())

    def update_group_item(self):
        if self.group_item is not None:
            childs = self.group_item.childCount()
            if childs == 0:
                self.list_view.invisibleRootItem().removeChild(self.group_item)
                self.group_item = None

    def update_stages_items(self):
        stages_list = list(self.stage_dic.keys())
        for stage in stages_list:
            item = self.stage_dic[stage]
            childs = item.childCount()
            if childs >= 1:
                item.update_infos(childs)
            else:
                self.list_view.invisibleRootItem().removeChild(item)
                del self.stage_dic[stage]

    def refresh_infos(self):
        references_count = len(self.reference_ids.keys())
        selection_count = len(self.list_view.selectedItems())
        self.references_count_label.setText(f"{references_count} references -")
        self.selection_count_label.setText(f"{selection_count} selected")

    def context_menu_requested(self):
        selection = self.list_view.selectedItems()
        menu = gui_utils.QMenu(self)
        remove_action = None
        update_action = None
        launch_action = None
        focus_action = None
        declare_error_action = None
        open_folder_action = None
        update_all_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update all references')
        if len(selection)>=1:
            update_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update selected references')
            remove_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Remove selected references')
            if len(selection) == 1:
                if selection[0].type == 'reference':
                    launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), 'Launch related work version')
                    focus_action = menu.addAction(QtGui.QIcon(ressources._tool_focus_), 'Focus on export instance')
                    declare_error_action = menu.addAction(QtGui.QIcon(ressources._tool_error_), 'Declare error on this asset')
                    open_folder_action = menu.addAction(QtGui.QIcon(ressources._tool_folder_), 'Open folder')
        add_action = menu.addAction(QtGui.QIcon(ressources._tool_add_), 'Add references (Tab)')

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == remove_action:
                self.remove_selection()
            elif action == update_action:
                self.update_selection()
            elif action == add_action:
                self.search_reference()
            elif action == update_all_action:
                self.update_all()
            elif action == launch_action:
                self.launch_work_version()
            elif action == focus_action:
                self.focus_on_export_version()
            elif action == declare_error_action:
                self.declare_error()
            elif action == open_folder_action:
                self.open_folder()

    def item_double_clicked(self, item):
        if item.type == 'group':
            self.focus_on_group_signal.emit(item.referenced_group_row['group_id'])

    def update_quick_import_buttons(self):
        if self.parent_instance_id is None or self.parent_instance_id == 0:
            self.clear_quick_imports_buttons()
            return
        if self.context != 'work_env':
            self.clear_quick_imports_buttons()
            return
        variant_id = project.get_work_env_data(self.parent_instance_id, 'variant_id')
        variant_row = project.get_variant_data(variant_id)
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        domain_name = project.get_domain_data(stage_row['domain_id'], 'name')
        stages_rows = project.get_asset_childs(asset_row['id'])
        project_stages = []
        for row in stages_rows:
            project_stages.append(row['name'])
            if row['name'] == stage_row['name']:
                self.remove_quick_button(row['name'])
                continue 
            if row['name'] not in self.quick_import_buttons.keys():
                button = quick_import_button(row['name'])
                button.quick_import_signal.connect(self.quick_import)
                self.quick_import_layout.addWidget(button)
                self.quick_import_buttons[row['name']] = button
        buttons_list = list(self.quick_import_buttons.keys())
        for stage in buttons_list:
            if stage not in project_stages:
                self.remove_quick_button(stage)

    def remove_quick_button(self, stage):
        if stage not in self.quick_import_buttons.keys():
            return
        self.quick_import_buttons[stage].setParent(None)
        self.quick_import_buttons[stage].deleteLater()
        del self.quick_import_buttons[stage]

    def clear_quick_imports_buttons(self):
        buttons_list = list(self.quick_import_buttons.keys())
        for stage in buttons_list:
            self.remove_quick_button(stage)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        if self.context == 'work_env':
            self.current_asset_viewer = current_asset_viewer.current_asset_viewer()
            self.main_layout.addWidget(self.current_asset_viewer)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setAnimated(1)
        self.list_view.setExpandsOnDoubleClick(1)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(7)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Stage', 'Namespace', 'Exported asset', 'Version', 'Format', 'Auto update', 'State', 'ID'])
        self.list_view.header().resizeSection(0, 200)
        self.list_view.header().resizeSection(1, 250)
        self.list_view.header().resizeSection(2, 250)
        self.list_view.header().resizeSection(3, 80)
        self.list_view.header().resizeSection(4, 60)
        self.list_view.header().resizeSection(5, 100)
        self.list_view.header().resizeSection(6, 80)
        self.list_view.header().resizeSection(7, 40)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.references_count_label = QtWidgets.QLabel()
        self.references_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.references_count_label)

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

        self.quick_import_widget = QtWidgets.QWidget()
        self.quick_import_widget.setObjectName('transparent_widget')
        self.quick_import_layout = QtWidgets.QHBoxLayout()
        self.quick_import_widget.setLayout(self.quick_import_layout)
        self.quick_import_layout.setContentsMargins(0,0,0,0)
        self.quick_import_layout.setSpacing(4)
        self.buttons_layout.addWidget(self.quick_import_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"modeling", "props", "Joe"')
        self.buttons_layout.addWidget(self.search_bar)

        self.remove_selection_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.remove_selection_button, "Remove selected references")
        self.remove_selection_button.setFixedSize(35,35)
        self.remove_selection_button.setIconSize(QtCore.QSize(25,25))
        self.remove_selection_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.remove_selection_button)

        self.add_reference_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.add_reference_button, "Add references (Tab)")
        self.add_reference_button.setFixedSize(35,35)
        self.add_reference_button.setIconSize(QtCore.QSize(25,25))
        self.add_reference_button.setIcon(QtGui.QIcon(ressources._tool_add_))
        self.buttons_layout.addWidget(self.add_reference_button)

        self.update_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.update_button, "Update selected references")
        self.update_button.setFixedSize(35,35)
        self.update_button.setIconSize(QtCore.QSize(25,25))
        self.update_button.setIcon(QtGui.QIcon(ressources._tool_update_))
        self.buttons_layout.addWidget(self.update_button)     

class custom_stage_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, stage, parent=None):
        super(custom_stage_tree_item, self).__init__(parent)
        self.stage = stage
        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setExpanded(1)
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.stage)
        self.setIcon(0, QtGui.QIcon(ressources._stage_icons_dic_[self.stage]))

    def update_infos(self, childs):
        self.setText(0, f"{self.stage} ({childs})")

class custom_group_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None):
        super(custom_group_tree_item, self).__init__(parent)
        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setExpanded(1)
        self.setText(0, 'Groups')
        self.setIcon(0, QtGui.QIcon(ressources._group_icon_))

class custom_referenced_group_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, referenced_group_row, group_row, parent=None):
        super(custom_referenced_group_tree_item, self).__init__(parent)
        self.type = 'group'
        self.referenced_group_row = referenced_group_row
        self.group_row = group_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.referenced_group_row['group_name'])
        self.setText(1, self.referenced_group_row['namespace'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setIcon(0, gui_utils.QIcon_from_svg(ressources._group_icon_,
                                                    self.group_row['color']))

    def update(self, group_row):
        self.group_row = group_row
        self.fill_ui()

class signal_handler(QtCore.QObject):

    enter = pyqtSignal(str, str)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_handler, self).__init__(parent)

class custom_reference_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, reference_row, context, parent=None):
        super(custom_reference_tree_item, self).__init__(parent)
        self.context = context
        self.type = 'reference'
        self.reference_row = reference_row
        self.signal_handler = signal_handler()
        self.apply_auto_update_change = False
        self.stage_row = None
        self.fill_ui()
        self.connect_functions()

    def fill_ui(self):
        self.setText(1, self.reference_row['namespace'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.export_widget = editable_data_widget()
        self.treeWidget().setItemWidget(self, 2, self.export_widget)
        self.version_widget = editable_data_widget(bold=True)
        self.treeWidget().setItemWidget(self, 3, self.version_widget)
        self.auto_update_checkbox = QtWidgets.QCheckBox()
        self.auto_update_checkbox.setStyleSheet('background-color:transparent;')
        self.treeWidget().setItemWidget(self, 5, self.auto_update_checkbox)

        self.setIcon(0, QtGui.QIcon(ressources._stage_icons_dic_[self.reference_row['stage']]))
        self.setForeground(4, QtGui.QBrush(QtGui.QColor('gray')))

        self.state_widget = state_widget()
        self.treeWidget().setItemWidget(self, 6, self.state_widget)
        
        self.setText(7, str(self.reference_row['id']))
        self.setForeground(7, QtGui.QBrush(QtGui.QColor('gray')))

    def update_item_infos(self, infos_list):
        self.export_widget.setText(infos_list[1])
        self.version_widget.setText(infos_list[2])
        self.set_auto_update(infos_list[4])
        self.setText(0, infos_list[5])
        self.stage_row = infos_list[6]
        self.state_widget.set_state(self.stage_row['state'])
        self.setText(4, infos_list[7])
        if infos_list[3]:
            self.version_widget.setColor('#9ce87b')
        else:
            self.version_widget.setColor('#f79360')

    def show_comment(self):
        if self.state_widget.isActiveWindow():
            if not self.stage_row:
                return
            tracking_events = project.get_asset_tracking_events(self.stage_row['id'])
            if len(tracking_events) == 0:
                return
            user = tracking_events[-1]['creation_user']
            self.signal_handler.enter.emit(self.stage_row['tracking_comment'], user)

    def connect_functions(self):
        self.version_widget.button_clicked.connect(self.version_modification_requested)
        self.export_widget.button_clicked.connect(self.export_modification_requested)
        self.auto_update_checkbox.stateChanged.connect(self.modify_auto_update)
        self.state_widget.enter.connect(self.show_comment)
        self.state_widget.leave.connect(self.signal_handler.leave.emit)
        self.state_widget.move_event.connect(self.signal_handler.move_event.emit)
        self.state_widget.modify_state_signal.connect(self.modify_state)

    def export_modification_requested(self, point):
        stage_id = project.get_export_data(self.reference_row['export_id'], 'stage_id')
        exports_list = project.get_stage_export_childs(stage_id)
        if exports_list is not None and exports_list != []:
            menu = gui_utils.QMenu()
            for export in exports_list:
                action = menu.addAction(export['name'])
                action.id = export['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_export(action.id)

    def version_modification_requested(self, point):
        versions_list = project.get_export_versions(self.reference_row['export_id'])
        if versions_list is not None and versions_list != []:
            menu = gui_utils.QMenu()
            for version in versions_list:
                if len(version['comment']) > 20:
                    comment = version['comment'][-20:] + '...'
                else:
                    comment = version['comment']
                action = menu.addAction(f"{version['name']} - {comment}")
                action.id = version['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_version(action.id)

    def set_auto_update(self, auto_update):
        self.apply_auto_update_change = False
        self.auto_update_checkbox.setChecked(auto_update)
        if auto_update:
            self.version_widget.hide_button()
        else:
            self.version_widget.unhide_button()
        self.apply_auto_update_change = True

    def modify_auto_update(self, auto_update):
        if self.apply_auto_update_change:
            if self.context == 'work_env':
                project.modify_reference_auto_update(self.reference_row['id'], auto_update)
            else:
                project.modify_grouped_reference_auto_update(self.reference_row['id'], auto_update)
            gui_server.refresh_team_ui()

    def modify_version(self, export_version_id):
        if self.context == 'work_env':
            project.update_reference(self.reference_row['id'], export_version_id)
        else:
            project.update_grouped_reference(self.reference_row['id'], export_version_id)
        gui_server.refresh_team_ui()

    def modify_export(self, export_id):
        if self.context == 'work_env':
            project.modify_reference_export(self.reference_row['id'], export_id)
        else:
            project.modify_grouped_reference_export(self.reference_row['id'], export_id)
        gui_server.refresh_team_ui()

    def modify_state(self, state):
        if self.stage_row['state'] != state:
            self.comment_widget = comment_widget.comment_widget()
            if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                comment = self.comment_widget.comment
                assets.modify_stage_state(self.stage_row['id'], state, comment)
                gui_server.refresh_team_ui()

class editable_data_widget(QtWidgets.QFrame):

    button_clicked = pyqtSignal(int)

    def __init__(self, parent=None, bold=False):
        super(editable_data_widget, self).__init__(parent)
        self.bold=bold
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.main_button.clicked.connect(self.button_clicked.emit)

    def build_ui(self):
        self.setObjectName('reference_edit_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,4,4,4)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.label)
        if self.bold:
            bold_font=QtGui.QFont()
            bold_font.setBold(True)
            self.label.setFont(bold_font)

        self.main_button = QtWidgets.QPushButton()
        self.main_button.setObjectName('dropdown_button')
        self.main_button.setFixedSize(QtCore.QSize(14,14))
        self.main_layout.addWidget(self.main_button)

    def hide_button(self):
        self.main_button.setVisible(0)

    def unhide_button(self):
        self.main_button.setVisible(1)

    def setText(self, text):
        self.label.setText(text)

    def setColor(self, color):
        self.setStyleSheet(f'color:{color}')

class reference_infos_thread(QtCore.QThread):

    reference_infos_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(reference_infos_thread, self).__init__(parent)
        self.reference_rows = None
        self.running = True

    def run(self):
        try:
            if self.reference_rows is not None:
                for reference_row in self.reference_rows:
                    export_version_row = project.get_export_version_data(reference_row['export_version_id'])
                    if not export_version_row:
                        continue
                    files = json.loads(export_version_row['files'])
                    if len(files)>0:
                        extension = files[0].split('.')[-1]
                    else:
                        files_dir = assets.get_export_version_path(reference_row['export_version_id'])
                        files_list = path_utils.listdir(files_dir)
                        if len(files_list) > 0:
                            extension = files_list[0].split('.')[-1]
                        else:
                            extension = '?'
                    export_row = project.get_export_data(export_version_row['export_id'])
                    stage_row = project.get_stage_data(export_row['stage_id'])
                    asset_name = project.get_asset_data(stage_row['asset_id'], 'name')
                    default_export_version_id = project.get_default_export_version(export_row['id'], 'id')

                    if default_export_version_id  != reference_row['export_version_id']:
                        up_to_date = 0
                    else:
                        up_to_date = 1

                    self.reference_infos_signal.emit([reference_row['id'], 
                                                        export_row['name'], 
                                                        export_version_row['name'], 
                                                        up_to_date, 
                                                        reference_row['auto_update'],
                                                        asset_name,
                                                        stage_row,
                                                        extension])
        except:
            logger.error(str(traceback.format_exc()))

    def update_references_rows(self, reference_rows):
        self.running = False
        self.reference_rows = reference_rows
        self.running = True
        self.start()

class search_thread(QtCore.QThread):

    show_ref_signal = pyqtSignal(int)
    hide_ref_signal = pyqtSignal(int)
    show_group_signal = pyqtSignal(int)
    hide_group_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, reference_rows, referenced_groups_rows, search_data):
        self.running = False
        self.search_data = search_data
        self.reference_rows = copy.deepcopy(reference_rows)
        self.referenced_groups_rows = copy.deepcopy(referenced_groups_rows)
        self.running = True
        self.start()

    def run(self):
        try:
            keywords = self.search_data.split('&')
            for reference_row in self.reference_rows:

                reference_id = reference_row['id']
                del reference_row['id']
                del reference_row['creation_time']
                del reference_row['count']
                if 'work_env_id' in reference_row.keys():
                    del reference_row['work_env_id']
                if 'group_id' in reference_row.keys():
                    del reference_row['group_id']
                del reference_row['export_id']
                del reference_row['export_version_id']
                del reference_row['auto_update']

                values = list(reference_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_ref_signal.emit(reference_id)
                else:
                    self.hide_ref_signal.emit(reference_id)

            for referenced_group_row in self.referenced_groups_rows:

                referenced_group_id = referenced_group_row['id']
                del referenced_group_row['id']
                del referenced_group_row['creation_time']
                del referenced_group_row['count']

                values = list(referenced_group_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data_list.append('groups')
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_group_signal.emit(referenced_group_id)
                else:
                    self.hide_group_signal.emit(referenced_group_id)
        except:
            logger.info(str(traceback.format_exc()))

class state_widget(QtWidgets.QLabel):

    enter = pyqtSignal(int)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)
    modify_state_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(state_widget, self).__init__(parent)
        self.setObjectName('state_widget')
        self.setMouseTracking(True)
        self.setFixedWidth(60)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect_functions()

    def connect_functions(self):
        self.customContextMenuRequested.connect(self.states_menu_requested)
        
    def set_state(self, state):
        self.setText(state)
        self.setStyleSheet('#state_widget{padding:3px;background-color:%s;border-radius:4px;}'%ressources._states_colors_[state])

    def states_menu_requested(self):
        menu = gui_utils.QMenu(self)
        for state in assets_vars._asset_states_list_:
            menu.addAction(QtGui.QIcon(ressources._states_icons_[state]), state)
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.modify_state_signal.emit(action.text())

    def mouseMoveEvent(self, event):
        self.move_event.emit(1)
        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.enter.emit(1)

    def leaveEvent(self, event):
        self.leave.emit(1)

    def contextMenuEvent(self, event):
        event.accept()

class quick_import_button(QtWidgets.QPushButton):

    quick_import_signal = pyqtSignal(str)

    def __init__(self, stage, parent=None):
        super(quick_import_button, self).__init__(parent)
        self.stage = stage
        self.setFixedSize(35,35)
        self.setIconSize(QtCore.QSize(21,21))
        self.connect_functions()
        self.fill_ui()
        gui_utils.application_tooltip(self, f"Import the {self.stage} of this asset")

    def fill_ui(self):
        self.setIcon(QtGui.QIcon(ressources._stage_icons_dic_[self.stage]))

    def connect_functions(self):
        self.clicked.connect(self.emit_signal)

    def emit_signal(self):
        self.quick_import_signal.emit(self.stage)