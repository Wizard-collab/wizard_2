# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging
import traceback
import copy

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import logging_widget
from wizard.gui import tag_label
from wizard.gui import comment_widget
from wizard.gui import asset_tracking_widget

# Wizard modules
from wizard.core import user
from wizard.core import repository
from wizard.core import tools
from wizard.core import assets
from wizard.core import project
from wizard.core import launch
from wizard.core import environment
from wizard.core import image
from wizard.core import path_utils
from wizard.vars import ressources
from wizard.vars import assets_vars
from wizard.vars import user_vars

logger = logging.getLogger(__name__)

class production_table_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(production_table_widget, self).__init__(parent)
        self.asset_ids = dict()
        self.stage_ids = dict()
        self.variant_ids = dict()
        self.update_categories = True
        self.update_assets = True
        self.domain = None
        self.category = None
        self.domain_ids = []
        self.category_ids = []
        self.old_thread_id = None
        self.search_threads = dict()
        self.view_comment_widget = tag_label.view_comment_widget(self)
        self.show_notes = 1
        self.show_states = 1
        self.show_assignments = 1
        self.show_priorities = 1
        self.init_users_images()
        self.build_ui()
        self.connect_functions()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 30, 8)
            self.users_images_dic[user_row['user_name']] = pixmap

    def set_context(self):
        context_dic = dict()
        context_dic['show_notes'] = self.show_notes 
        context_dic['show_states'] = self.show_states 
        context_dic['show_assignments'] = self.show_assignments 
        context_dic['show_priorities'] = self.show_priorities 
        context_dic['domain'] = self.domain 
        context_dic['search_text'] = self.search_bar.text() 
        user.user().add_context(user_vars._production_table_context_, context_dic)
        self.asset_tracking_widget.set_context()

    def get_context(self):
        context_dic = user.user().get_context(user_vars._production_table_context_)
        if context_dic is not None and context_dic != dict():
            self.show_notes = context_dic['show_notes']
            self.show_states = context_dic['show_states']
            self.show_assignments = context_dic['show_assignments']
            self.show_priorities = context_dic['show_priorities']
            self.search_bar.setText(context_dic['search_text'])
            self.update_stage_datas_visibility()
            self.update_layout()
            self.domain_comboBox.setCurrentText(context_dic['domain'])
            self.asset_tracking_widget.get_context()
        self.asset_tracking_widget.get_context()

    def context_menu_requested(self, point):
        menu = gui_utils.QMenu(self)
        menu.addSeparator()
        show_notes_icon = ressources._uncheck_icon_
        if self.show_notes:
            show_notes_icon = ressources._check_icon_
        show_states_icon = ressources._uncheck_icon_
        if self.show_states:
            show_states_icon = ressources._check_icon_
        show_assignments_icon = ressources._uncheck_icon_
        if self.show_assignments:
            show_assignments_icon = ressources._check_icon_
        show_priorities_icon = ressources._uncheck_icon_
        if self.show_priorities:
            show_priorities_icon = ressources._check_icon_

        show_states_item = menu.addAction(QtGui.QIcon(show_states_icon), f'Show states')
        show_assignment_item = menu.addAction(QtGui.QIcon(show_assignments_icon), f'Show assignments')
        show_notes_item = menu.addAction(QtGui.QIcon(show_notes_icon), f'Show notes')
        show_priorities_item = menu.addAction(QtGui.QIcon(show_priorities_icon), f'Show priorities')

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == show_notes_item:
                self.show_notes = 1-self.show_notes
                self.update_stage_datas_visibility()
                self.update_layout()
            if action == show_states_item:
                self.show_states = 1-self.show_states
                self.update_stage_datas_visibility()
                self.update_layout()
            if action == show_assignment_item:
                self.show_assignments = 1-self.show_assignments
                self.update_stage_datas_visibility()
                self.update_layout()
            if action == show_priorities_item:
                self.show_priorities = 1-self.show_priorities
                self.update_stage_datas_visibility()
                self.update_layout()

    def update_stage_datas_visibility(self):
        for stage_id in self.stage_ids.keys():
            self.stage_ids[stage_id]['widget'].update_notes_visibility(self.show_notes)
            self.stage_ids[stage_id]['widget'].update_states_visibility(self.show_states)
            self.stage_ids[stage_id]['widget'].update_assignments_visibility(self.show_assignments)
            self.stage_ids[stage_id]['widget'].update_priorities_visibility(self.show_priorities)

    def update_layout(self):
        QtWidgets.QApplication.processEvents()
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()
        QtWidgets.QApplication.processEvents()

    def build_ui(self):
        self.resize(1400,800)
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.domain_comboBox = gui_utils.QComboBox()
        self.domain_comboBox.setMinimumHeight(36)
        self.header_layout.addWidget(self.domain_comboBox)

        self.search_bar = gui_utils.search_bar(red=36, green=36, blue=43)
        self.header_layout.addWidget(self.search_bar)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.content_widget = gui_utils.QSplitter()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_widget.setObjectName('main_widget')
        self.main_layout.addWidget(self.content_widget)

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setObjectName('dark_widget')
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setObjectName('table_widget_horizontal_header_view')
        self.table_widget.verticalHeader().setObjectName('table_widget_vertical_header_view')
        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.content_widget.addWidget(self.table_widget)
        self.content_widget.setCollapsible(0, False)

        self.asset_tracking_widget = asset_tracking_widget.asset_tracking_widget()
        self.asset_tracking_widget.setFixedWidth(350)
        self.content_widget.addWidget(self.asset_tracking_widget)
        self.content_widget.setCollapsible(1, True)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(11,11,11,11)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

    def update_state(self, state):
        comment = ''
        self.comment_widget = comment_widget.comment_widget()
        if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
            comment = self.comment_widget.comment
        for modelIndex in self.table_widget.selectedIndexes():
            widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
            if widget and widget.type == 'stage':
                if not widget.isVisible():
                    continue
                stage_row = widget.stage_row
                stage_id = stage_row['id']
                if stage_row['state'] != state:
                    assets.modify_stage_state(stage_id, state, comment)
        gui_server.refresh_team_ui()

    def update_priority(self, priority):
        for modelIndex in self.table_widget.selectedIndexes():
            widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
            if widget and widget.type == 'stage':
                if not widget.isVisible():
                    continue
                stage_row = widget.stage_row
                stage_id = stage_row['id']
                if stage_row['priority'] != priority:
                    assets.modify_stage_priority(stage_id, priority)
        gui_server.refresh_team_ui()

    def update_assignment(self, assignment):
        for modelIndex in self.table_widget.selectedIndexes():
            widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
            if widget and widget.type == 'stage':
                if not widget.isVisible():
                    continue
                stage_row = widget.stage_row
                stage_id = stage_row['id']
                if stage_row['assignment'] != assignment:
                    assets.modify_stage_assignment(stage_id, assignment)
        gui_server.refresh_team_ui()

    def connect_functions(self):
        self.domain_comboBox.currentTextChanged.connect(self.refresh_assets)
        self.table_widget.itemSelectionChanged.connect(self.change_stage_asset_tracking_widget)
        self.search_bar.textChanged.connect(self.update_search)
        self.table_widget.customContextMenuRequested.connect(self.context_menu_requested)

    def showEvent(self, event):
        self.refresh()

    def refresh(self):
        if self.isVisible():
            self.update_assets = False
            domain_rows = project.get_domains()
            for domain_row in domain_rows:
                if (domain_row['id'] not in self.domain_ids) and (domain_row['name'] != 'library'):
                    self.domain_comboBox.addItem(QtGui.QIcon(ressources._domains_icons_dic_[domain_row['name']]), domain_row['name'])
                    self.domain_ids.append(domain_row['id'])
            self.update_assets = True
            self.refresh_assets()
            self.asset_tracking_widget.refresh()

    def change_stage_asset_tracking_widget(self):
        if len(self.table_widget.selectedIndexes()) != 1:
            self.asset_tracking_widget.change_stage(None)
            return
        modelIndex = self.table_widget.selectedIndexes()[0]
        widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
        if not widget:
            self.asset_tracking_widget.change_stage(None)
            return
        if widget.type != 'stage':
            self.asset_tracking_widget.change_stage(None)
            return
        stage_id = widget.stage_row['id']
        self.asset_tracking_widget.change_stage(stage_id)

    def refresh_assets(self):
        start_time = time.perf_counter()

        if not self.update_assets:
            return

        current_domain = self.domain_comboBox.currentText()
        if current_domain != self.domain:
            self.show_all_stages()
            self.show_all_assets()
            #self.update_layout()
            self.table_widget.clear()
            self.asset_ids = dict()
            self.stage_ids = dict()
            self.domain = current_domain
        
        assets_preview_rows = project.get_all_assets_preview()
        assets_preview = dict()

        domain_id = project.get_domain_by_name(self.domain, 'id')
        self.asset_rows = []
        self.category_rows = dict()
        for category_row in project.get_domain_childs(domain_id):
            self.category_rows[category_row['id']] = category_row
            self.asset_rows += project.get_category_childs(category_row['id'])

        for assets_preview_row in assets_preview_rows:
            assets_preview[assets_preview_row['asset_id']] = assets_preview_row
        
        if self.domain == assets_vars._assets_:
            labels_names = ["Name", "Modeling", "Rigging", "Grooming", "Texturing", "Shading"]
            self.task_list = ["", "modeling", "rigging", "grooming", "texturing", "shading"]
        elif self.domain == assets_vars._sequences_:
            labels_names = ["Name", "Frame range", "Layout", "Animation", "Cfx", "Fx", "Camera", "Lighting", "Compositing"]
            self.task_list = ["", "", "layout", "animation", "cfx", "fx", "camera", "lighting", "compositing"]

        stage_ids = list(self.stage_ids.keys())
        project_stage_ids = project.get_all_stages('id')
        for stage_id in stage_ids:
            if stage_id not in project_stage_ids:
                self.remove_stage(stage_id)

        project_asset_ids = [asset_row['id'] for asset_row in self.asset_rows]
        asset_ids = list(self.asset_ids.keys())
        for asset_id in asset_ids:
            if asset_id not in project_asset_ids:
                self.remove_asset(asset_id)

        self.table_widget.setColumnCount(len(labels_names))
        self.table_widget.setHorizontalHeaderLabels(labels_names)
        self.table_widget.setRowCount(len(self.asset_rows))

        for asset_row in self.asset_rows:
            if asset_row['id'] not in self.asset_ids.keys():
                index = self.asset_rows.index(asset_row)
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsSelectable)
                self.table_widget.setItem(index, 0, item)
                widget = asset_widget(asset_row, self.category_rows[asset_row['category_id']], assets_preview[asset_row['id']])
                self.table_widget.setCellWidget(index, 0, widget)
                self.asset_ids[asset_row['id']] = dict()
                self.asset_ids[asset_row['id']]['row'] = asset_row
                self.asset_ids[asset_row['id']]['table_row'] = index
                self.asset_ids[asset_row['id']]['preview_row'] = assets_preview[asset_row['id']]
                self.asset_ids[asset_row['id']]['widget'] = widget
                if self.domain == assets_vars._sequences_:
                    item = QtWidgets.QTableWidgetItem()
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsSelectable)
                    self.table_widget.setItem(index, 1, item)
                    frange_widget = frame_range_widget(asset_row)
                    self.table_widget.setCellWidget(index, 1, frange_widget)
                    self.asset_ids[asset_row['id']]['frame_range_widget'] = frange_widget
            else:
                if assets_preview[asset_row['id']] != self.asset_ids[asset_row['id']]['preview_row']:
                    self.asset_ids[asset_row['id']]['widget'].refresh(asset_row, assets_preview[asset_row['id']])
                    self.asset_ids[asset_row['id']]['row'] = asset_row
                    self.asset_ids[asset_row['id']]['preview_row'] = assets_preview[asset_row['id']]
                    if self.domain == assets_vars._sequences_:
                        self.asset_ids[asset_row['id']]['frame_range_widget'].refresh(asset_row)

        self.update_layout()

        stage_rows = project.get_all_stages()
        self.stage_rows = []

        for stage_row in stage_rows:
            if stage_row['asset_id'] in self.asset_ids.keys():
                self.stage_rows.append(stage_row)
                if stage_row['id'] not in self.stage_ids.keys():
                    row_index = self.get_asset_coord(stage_row['asset_id']).row()
                    self.stage_ids[stage_row['id']] = dict()
                    self.stage_ids[stage_row['id']]['row'] = stage_row
                    self.stage_ids[stage_row['id']]['widget'] = stage_widget(stage_row, self.users_images_dic)
                    self.table_widget.setCellWidget(row_index, self.task_list.index(stage_row['name']), self.stage_ids[stage_row['id']]['widget'])
                    self.stage_ids[stage_row['id']]['widget'].show_comment_signal.connect(self.view_comment_widget.show_comment)
                    self.stage_ids[stage_row['id']]['widget'].hide_comment_signal.connect(self.view_comment_widget.close)
                    self.stage_ids[stage_row['id']]['widget'].move_comment.connect(self.view_comment_widget.move_ui)
                    self.stage_ids[stage_row['id']]['widget'].state_signal.connect(self.update_state)
                    self.stage_ids[stage_row['id']]['widget'].priority_signal.connect(self.update_priority)
                    self.stage_ids[stage_row['id']]['widget'].assignment_signal.connect(self.update_assignment)
                else:
                    if stage_row != self.stage_ids[stage_row['id']]['row']:
                        self.stage_ids[stage_row['id']]['widget'].refresh(stage_row)
                        self.stage_ids[stage_row['id']]['row'] = stage_row

        self.update_stage_datas_visibility()
        self.update_layout()
        self.update_search()

        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def get_asset_coord(self, asset_id):
        if asset_id in self.asset_ids.keys():
            widget = self.asset_ids[asset_id]['widget']
            model_index = self.table_widget.indexAt(widget.pos())
            return model_index

    def get_asset_row(self, asset_id):
        if asset_id in self.asset_ids.keys():
            widget = self.asset_ids[asset_id]['widget']
            row = self.table_widget.rowAt(widget.pos().y())
            return row

    def get_stage_coord(self, stage_id):
        if stage_id in self.stage_ids.keys():
            widget = self.stage_ids[stage_id]['widget']
            model_index = self.table_widget.indexAt(widget.pos())
            return model_index

    def get_stage_item(self, stage_id):
        if stage_id in self.stage_ids.keys():
            widget = self.stage_ids[stage_id]['widget']
            item = self.table_widget.itemAt(widget.pos())
            return item

    def remove_stage(self, stage_id):
        if stage_id in self.stage_ids.keys():
            model_index = self.get_stage_coord(stage_id)
            self.table_widget.removeCellWidget(model_index.row(), model_index.column())
            del self.stage_ids[stage_id]

    def remove_asset(self, asset_id):
        if asset_id in self.asset_ids.keys():
            row_index = self.get_asset_coord(asset_id).row()
            self.table_widget.removeRow(row_index)
            del self.asset_ids[asset_id]

    def update_search(self):
        if not self.isVisible():
            return
        search_data = self.search_bar.text()
        self.search_start_time = time.perf_counter()
        self.accept_item_from_thread = False
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
            self.search_threads[self.old_thread_id].show_stage_signal.disconnect()
            self.search_threads[self.old_thread_id].hide_stage_signal.disconnect()
            self.search_threads[self.old_thread_id].show_asset_signal.disconnect()
            self.search_threads[self.old_thread_id].hide_asset_signal.disconnect()
            self.search_threads[self.old_thread_id].hide_task_signal.disconnect()
            self.search_threads[self.old_thread_id].show_task_signal.disconnect()
        thread_id = time.time()
        self.search_threads[thread_id] = search_thread()
        self.search_threads[thread_id].show_stage_signal.connect(self.show_stage)
        self.search_threads[thread_id].hide_stage_signal.connect(self.hide_stage)
        self.search_threads[thread_id].show_asset_signal.connect(self.show_asset)
        self.search_threads[thread_id].hide_asset_signal.connect(self.hide_asset)
        self.search_threads[thread_id].hide_task_signal.connect(self.hide_task)
        self.search_threads[thread_id].show_task_signal.connect(self.show_task)
        self.old_thread_id = thread_id
        if len(search_data) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(self.asset_rows, self.stage_rows, self.task_list, search_data)
        else:
            self.search_threads[thread_id].running=False
            self.show_all_stages()
            self.show_all_assets()
            self.show_all_tasks()
            self.update_layout()
        self.clean_threads()

    def clean_threads(self):
        ids = list(self.search_threads.keys())
        for thread_id in ids:
            if not self.search_threads[thread_id].running:
                self.search_threads[thread_id].terminate()
                del self.search_threads[thread_id]

    def hide_stage(self, stage_id):
        if stage_id in self.stage_ids.keys():
            self.stage_ids[stage_id]['widget'].setVisible(False)

    def show_stage(self, stage_id):
        if stage_id in self.stage_ids.keys():
            self.stage_ids[stage_id]['widget'].setVisible(True)

    def show_all_stages(self):
        for stage_id in self.stage_ids.keys():
            self.show_stage(stage_id)
        self.update_layout()

    def hide_asset(self, asset_id):
        if asset_id in self.asset_ids.keys():
            model_index = self.get_asset_coord(asset_id)
            self.table_widget.hideRow(self.asset_ids[asset_id]['table_row'])

    def show_asset(self, asset_id):
        if asset_id in self.asset_ids.keys():
            self.table_widget.showRow(self.asset_ids[asset_id]['table_row'])

    def show_all_assets(self):
        for asset_id in self.asset_ids.keys():
            self.show_asset(asset_id)

    def hide_task(self, task):
        task_index = self.task_list.index(task)
        self.table_widget.hideColumn(task_index)

    def show_task(self, task):
        task_index = self.task_list.index(task)
        self.table_widget.showColumn(task_index)

    def show_all_tasks(self):
        for task in self.task_list:
            self.show_task(task)

class asset_widget(QtWidgets.QWidget):
    def __init__(self, asset_row, category_row, preview_row, parent=None):
        super(asset_widget, self).__init__(parent)
        self.thumbnail_width = 150
        self.type = 'asset'
        self.asset_row = asset_row
        self.category_row = category_row
        self.preview_row = preview_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,8,0)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedWidth(self.thumbnail_width)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName('production_manager_variant_frame')
        self.main_layout.addWidget(self.image_label)

        self.name_layout = QtWidgets.QVBoxLayout()
        self.name_layout.setSpacing(2)
        self.name_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.asset_name_label = QtWidgets.QLabel()
        self.name_layout.addWidget(self.asset_name_label)
        self.category_name_label = QtWidgets.QLabel()
        self.category_name_label.setObjectName('gray_label')
        self.name_layout.addWidget(self.category_name_label)
        self.name_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.main_layout.addLayout(self.name_layout)


    def fill_ui(self):
        self.asset_name_label.setText(self.asset_row['name'])
        self.category_name_label.setText(self.category_row['name'])

        image = ressources._no_preview_
        if self.preview_row['manual_override'] is None:
            if self.preview_row['preview_path'] is not None:
                image = self.preview_row['preview_path']
        else:
            image = self.preview_row['manual_override']
        self.image_label.setPixmap(QtGui.QIcon(image).pixmap(self.thumbnail_width, int(self.thumbnail_width/1.8)))

    def show_context_menu(self):
        menu = gui_utils.QMenu(self)
        custom_preview_action = menu.addAction(QtGui.QIcon(ressources._add_icon_), 'Add custom preview')
        default_preview_action = menu.addAction(QtGui.QIcon(ressources._refresh_icon_), 'Set preview to auto')
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == default_preview_action:
                assets.set_asset_preview(self.preview_row['asset_id'], None)
                gui_server.refresh_team_ui()
            elif action == custom_preview_action:
                self.set_preview()

    def set_preview(self):
        options = QtWidgets.QFileDialog.Options()
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select preview image", "",
                            "All Files (*);;Images Files (*.png);;Images Files (*.jpg);;Images Files (*.jpeg)",
                            options=options)
        if image_file:
            extension = image_file.split('.')[-1].upper()
            if (extension == 'PNG') or (extension == 'JPG') or (extension == 'JPEG'):
                assets.set_asset_preview(self.preview_row['asset_id'], image_file)
                gui_server.refresh_team_ui()
            else:
                logger.warning('{} is not a valid image file...'.format(image_file))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.show_context_menu()

    def refresh(self, asset_row, preview_row):
        self.asset_row = asset_row
        self.preview_row = preview_row
        self.fill_ui()

class frame_range_widget(QtWidgets.QWidget):
    def __init__(self, asset_row, parent = None):
        super(frame_range_widget, self).__init__(parent)
        self.asset_row = asset_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.frame_range_label = QtWidgets.QLabel()
        self.frame_range_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.frame_range_label)

        self.details_label = QtWidgets.QLabel()
        self.details_label.setAlignment(QtCore.Qt.AlignCenter)
        self.details_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.details_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def fill_ui(self):
        self.frame_range_label.setText(f"{self.asset_row['inframe']} - {self.asset_row['outframe']}")
        self.details_label.setText(f"{self.asset_row['outframe'] - self.asset_row['inframe']} frames")

    def refresh(self, asset_row):
        self.asset_row = asset_row
        self.fill_ui()

class stage_widget(QtWidgets.QWidget):

    state_signal = pyqtSignal(str)
    assignment_signal = pyqtSignal(str)
    priority_signal = pyqtSignal(str)
    show_comment_signal = pyqtSignal(str, str)
    hide_comment_signal = pyqtSignal(int)
    move_comment = pyqtSignal(int)

    def __init__(self, stage_row, users_images_dic, parent=None):
        super(stage_widget, self).__init__(parent)
        self.type = 'stage'
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def update_notes_visibility(self, show_notes):
        self.note_content.setVisible(show_notes)

    def update_states_visibility(self, show_states):
        self.state_label.setVisible(show_states)

    def update_assignments_visibility(self, show_assignments):
        self.user_image_label.setVisible(show_assignments)

    def update_priorities_visibility(self, show_priorities):
        self.priority_label.setVisible(show_priorities)

    def connect_functions(self):
        self.state_label.state_signal.connect(self.state_signal.emit)
        self.state_label.enter.connect(self.show_comment)
        self.state_label.leave.connect(self.hide_comment)
        self.state_label.move_event.connect(self.move_comment.emit)
        self.user_image_label.assignment_signal.connect(self.assignment_signal.emit)
        self.priority_label.priority_signal.connect(self.priority_signal.emit)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.color_frame = QtWidgets.QFrame()
        self.color_frame.setFixedWidth(4)
        self.main_layout.addWidget(self.color_frame)

        self.data_layout = QtWidgets.QHBoxLayout()
        self.data_layout.setSpacing(3)
        self.data_layout.setContentsMargins(3,3,3,3)
        self.main_layout.addLayout(self.data_layout)

        self.priority_label = priority_widget()
        self.priority_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.priority_label.setFixedSize(30, 30)
        self.data_layout.addWidget(self.priority_label)

        self.state_label = state_widget()
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_label.setFixedHeight(30)
        self.data_layout.addWidget(self.state_label)

        self.user_image_label = assignment_widget()
        self.user_image_label.setFixedSize(QtCore.QSize(30,30))
        self.data_layout.addWidget(self.user_image_label)

        self.note_content = gui_utils.minimum_height_textEdit(77)
        self.note_content.setFixedWidth(150)
        self.note_content.setReadOnly(True)
        self.note_content.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.note_content.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.note_content.setObjectName('gray_label')
        self.note_content.setStyleSheet('background-color:transparent;padding:0px;')
        self.data_layout.addWidget(self.note_content)

    def show_comment(self):
        if self.isActiveWindow():
            tracking_events = project.get_asset_tracking_events(self.stage_row['id'])
            if len(tracking_events) == 0:
                return
            user = tracking_events[-1]['creation_user']
            self.show_comment_signal.emit(self.stage_row['tracking_comment'], user)

    def hide_comment(self):
        self.hide_comment_signal.emit(1)

    def fill_ui(self):
        self.color_frame.setStyleSheet('background-color:%s;'%ressources._stages_colors_[self.stage_row['name']])
        self.priority_label.setPixmap(QtGui.QIcon(ressources._priority_icons_list_[self.stage_row['priority']]).pixmap(22))
        self.state_label.setText(self.stage_row['state'])
        self.state_label.setStyleSheet('#bold_label{background-color:%s;border-radius:4px;padding:6px;}'%ressources._states_colors_[self.stage_row['state']])
        self.user_image_label.setPixmap(self.users_images_dic[self.stage_row['assignment']])
        if self.stage_row['note'] is None or self.stage_row['note'] == '':
            self.note_content.setText('Missing note')
        else:
            self.note_content.setText(self.stage_row['note'])

    def refresh(self, stage_row):
        self.stage_row = stage_row
        self.fill_ui()

class priority_widget(QtWidgets.QLabel):

    priority_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(priority_widget, self).__init__(parent)
        self.setFixedWidth(60)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setObjectName('priority_label')
        self.setStyleSheet('#priority_label{border-radius:4px;background-color:rgba(0,0,0,40);}')

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.states_menu_requested()

    def states_menu_requested(self):
        menu = gui_utils.QMenu(self)
        for priority in assets_vars._priority_list_:
            menu.addAction(QtGui.QIcon(ressources._priority_icons_list_[priority]), priority)
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.priority_signal.emit(action.text())

    def contextMenuEvent(self, event):
        event.accept()

class state_widget(QtWidgets.QLabel):

    state_signal = pyqtSignal(str)
    enter = pyqtSignal(int)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super(state_widget, self).__init__(parent)
        self.setMouseTracking(True)
        self.setFixedWidth(60)
        self.setObjectName('bold_label')
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.states_menu_requested()

    def states_menu_requested(self):
        menu = gui_utils.QMenu(self)
        for state in assets_vars._asset_states_list_:
            menu.addAction(QtGui.QIcon(ressources._states_icons_[state]), state)
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.state_signal.emit(action.text())

    def mouseMoveEvent(self, event):
        self.move_event.emit(1)
        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.enter.emit(1)

    def leaveEvent(self, event):
        self.leave.emit(1)

    def contextMenuEvent(self, event):
        event.accept()

class assignment_widget(QtWidgets.QLabel):

    assignment_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(assignment_widget, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.users_menu_requested()

    def users_menu_requested(self):
        users_actions = []
        menu = gui_utils.QMenu(self)
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            user_row = repository.get_user_data(user_id)
            icon = QtGui.QIcon()
            pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 24)
            icon.addPixmap(pm)
            menu.addAction(icon, user_row['user_name'])
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.assignment_signal.emit(action.text())

    def contextMenuEvent(self, event):
        event.accept()

class search_thread(QtCore.QThread):

    show_stage_signal = pyqtSignal(int)
    hide_stage_signal = pyqtSignal(int)
    show_asset_signal = pyqtSignal(int)
    hide_asset_signal = pyqtSignal(int)
    show_task_signal = pyqtSignal(str)
    hide_task_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, asset_rows, stage_rows, tasks, search_data):
        self.search_data = search_data
        self.asset_rows = copy.deepcopy(asset_rows)
        self.stage_rows = copy.deepcopy(stage_rows)
        self.tasks = copy.deepcopy(tasks)
        self.start()

    def run(self):
        try:
            asset_ids = []
            stages_to_show = []
            stages_to_hide = []
            task_to_show = []

            keywords_sets = self.search_data.split('+')
            
            for stage_row in self.stage_rows:

                stage_id = stage_row['id']
                values = []
                for key in stage_row:
                    if key in ['id', 'creation_time', 'creation_user']:
                        continue
                    values.append(stage_row[key])

                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)
                data = data.replace('assets','')
                data = data.replace('sequences','')

                for keywords_set in keywords_sets:
                    if keywords_set == '':
                        continue
                    keywords = keywords_set.split('&')
                    if all(keyword.upper() in data.upper() for keyword in keywords):
                        stages_to_show.append(stage_id)
                        task_to_show.append(stage_row['name'])
                        asset_ids.append(stage_row['asset_id'])

            for asset_row in self.asset_rows:
                if asset_row['id'] in asset_ids:
                    self.show_asset_signal.emit(asset_row['id'])
                else:
                    self.hide_asset_signal.emit(asset_row['id'])
            for task in self.tasks:
                if task == '':
                    continue
                if task in set(task_to_show):
                    self.show_task_signal.emit(task)
                else:
                    self.hide_task_signal.emit(task)
            QtWidgets.QApplication.processEvents()
            time.sleep(0.1)
            for stage_row in self.stage_rows:
                if stage_row['id'] in stages_to_show:
                    self.show_stage_signal.emit(stage_row['id'])
                else:
                    self.hide_stage_signal.emit(stage_row['id'])

        except:
            logger.info(str(traceback.format_exc()))
        self.running = False
