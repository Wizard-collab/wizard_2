# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import logging_widget
from wizard.gui import tag_label

# Wizard modules
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
        self.view_comment_widget = view_comment_widget(self)
        self.init_users_images()
        self.build_ui()
        self.connect_functions()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 22)
            self.users_images_dic[user_row['user_name']] = pixmap

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
        self.category_comboBox = gui_utils.QComboBox()
        self.category_comboBox.setMinimumHeight(36)
        self.header_layout.addWidget(self.category_comboBox)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setObjectName('dark_widget')
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setObjectName('table_widget_horizontal_header_view')
        self.table_widget.verticalHeader().setObjectName('table_widget_vertical_header_view')
        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_layout.addWidget(self.table_widget)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
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
        for modelIndex in self.table_widget.selectedIndexes():
            widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
            if widget and widget.type == 'stage':
                stage_row = widget.stage_row
                stage_id = stage_row['id']
                if stage_row['state'] != state:
                    assets.modify_stage_state(stage_id, state)
        gui_server.refresh_team_ui()

    def update_assignment(self, assignment):
        for modelIndex in self.table_widget.selectedIndexes():
            widget = self.table_widget.cellWidget(modelIndex.row(), modelIndex.column())
            if widget and widget.type == 'stage':
                stage_row = widget.stage_row
                stage_id = stage_row['id']
                if stage_row['assignment'] != assignment:
                    assets.modify_stage_assignment(stage_id, assignment)
        gui_server.refresh_team_ui()

    def connect_functions(self):
        self.domain_comboBox.currentTextChanged.connect(self.refresh_categories)
        self.category_comboBox.currentTextChanged.connect(self.refresh_assets)

    def showEvent(self, event):
        self.refresh()

    def refresh(self):
        if self.isVisible():
            self.update_categories = False
            domain_rows = project.get_domains()
            for domain_row in domain_rows:
                if (domain_row['id'] not in self.domain_ids) and (domain_row['name'] != 'library'):
                    self.domain_comboBox.addItem(QtGui.QIcon(ressources._domains_icons_dic_[domain_row['name']]), domain_row['name'])
                    self.domain_ids.append(domain_row['id'])
            self.update_categories = True
            self.refresh_categories()

    def clear_categories(self):
        self.category_ids = []
        self.category_comboBox.clear()

    def refresh_categories(self):
        if self.update_categories:
            self.update_assets = False
            current_domain = self.domain_comboBox.currentText()
            if current_domain != self.domain:
                self.clear_categories()
                self.domain = current_domain
            domain_id = project.get_domain_by_name(current_domain, 'id')
            category_rows = project.get_domain_childs(domain_id)
            for category_row in category_rows:
                if category_row['id'] not in self.category_ids:
                    self.category_comboBox.addItem(category_row['name'])
                    self.category_ids.append(category_row['id'])
            self.update_assets = True
            self.refresh_assets()

    def clear_assets(self):
        self.table_widget.clear()
        self.asset_ids = dict()
        self.stage_ids = dict()

    def refresh_assets(self):
        start_time = time.perf_counter()

        category = self.category_comboBox.currentText()
        if category != self.category:
            self.clear_assets()
        self.category = category

        if category != "":
            category_id = project.get_category_data_by_name(category, 'id')
            asset_rows = project.get_category_childs(category_id)

            project_asset_ids = []
            assets_preview_rows = project.get_all_assets_preview()
            assets_preview = dict()
            for assets_preview_row in assets_preview_rows:
                assets_preview[assets_preview_row['asset_id']] = assets_preview_row
            
            if self.domain == assets_vars._assets_:
                labels_names = ["Name", "Modeling", "Rigging", "Grooming", "Texturing", "Shading"]
                stages_list = ["", "modeling", "rigging", "grooming", "texturing", "shading"]
            elif self.domain == assets_vars._sequences_:
                labels_names = ["Name", "Frame range", "Layout", "Animation", "Cfx", "Fx", "Camera", "Lighting", "Compositing"]
                stages_list = ["", "", "layout", "animation", "cfx", "fx", "camera", "lighting", "compositing"]

            project_asset_ids = [asset_row['id'] for asset_row in asset_rows]

            asset_ids = list(self.asset_ids.keys())
            for asset_id in asset_ids:
                if asset_id not in project_asset_ids:
                    self.remove_asset(asset_id)

            self.table_widget.setColumnCount(len(labels_names))
            self.table_widget.setHorizontalHeaderLabels(labels_names)
            self.table_widget.setRowCount(len(asset_rows))

            for asset_row in asset_rows:
                project_asset_ids.append(asset_row['id'])
                if asset_row['id'] not in self.asset_ids.keys():
                    index = asset_rows.index(asset_row)
                    item = QtWidgets.QTableWidgetItem()
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsSelectable)
                    self.table_widget.setItem(index, 0, item)
                    widget = asset_widget(asset_row, assets_preview[asset_row['id']])
                    self.table_widget.setCellWidget(index, 0, widget)
                    self.asset_ids[asset_row['id']] = dict()
                    self.asset_ids[asset_row['id']]['row'] = asset_row
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

            stage_rows = project.get_all_stages()
            project_stage_ids = []

            for stage_row in stage_rows:
                project_stage_ids.append(stage_row['id'])
                if stage_row['asset_id'] in self.asset_ids.keys():
                    if stage_row['id'] not in self.stage_ids.keys():
                        row_index = self.get_asset_coord(stage_row['asset_id']).row()
                        widget = stage_widget(stage_row, self.users_images_dic)
                        widget.show_comment_signal.connect(self.show_comment)
                        widget.hide_comment_signal.connect(self.hide_comment)
                        widget.move_comment.connect(self.move_comment)
                        widget.state_signal.connect(self.update_state)
                        widget.assignment_signal.connect(self.update_assignment)
                        self.table_widget.setCellWidget(row_index, stages_list.index(stage_row['name']), widget)
                        self.stage_ids[stage_row['id']] = dict()
                        self.stage_ids[stage_row['id']]['row'] = stage_row
                        self.stage_ids[stage_row['id']]['widget'] = widget
                    else:
                        if stage_row != self.stage_ids[stage_row['id']]['row']:
                            self.stage_ids[stage_row['id']]['widget'].refresh(stage_row)
                            self.stage_ids[stage_row['id']]['row'] = stage_row

            stage_ids = list(self.stage_ids.keys())
            for stage_id in stage_ids:
                if stage_id not in project_stage_ids:
                    self.remove_stage(stage_id)

            QtWidgets.QApplication.processEvents()
            self.table_widget.resizeColumnsToContents()
            self.table_widget.resizeRowsToContents()
        else:
            self.clear_assets()

        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def get_asset_coord(self, asset_id):
        if asset_id in self.asset_ids.keys():
            widget = self.asset_ids[asset_id]['widget']
            model_index = self.table_widget.indexAt(widget.pos())
            return model_index

    def get_stage_coord(self, stage_id):
        if stage_id in self.stage_ids.keys():
            widget = self.stage_ids[stage_id]['widget']
            model_index = self.table_widget.indexAt(widget.pos())
            return model_index

    def remove_stage(self, stage_id):
        if stage_id in self.stage_ids.keys():
            model_index = self.get_stage_coord(stage_id)
            self.table_widget.removeCellWidget(model_index.row(), model_index.column())
            del self.stage_ids[stage_id]

    def remove_asset(self, asset_id):
        if asset_id in self.asset_ids.keys():
            row_index = self.get_asset_coord(asset_id).row()
            print(row_index)
            self.table_widget.removeRow(row_index)
            del self.asset_ids[asset_id]

    def show_comment(self, stage_row):
        self.view_comment_widget.show_comment(stage_row)

    def hide_comment(self):
        self.view_comment_widget.close()

    def move_comment(self):
        self.view_comment_widget.move_ui()

class view_comment_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(view_comment_widget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMinimumWidth(200)
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('black_round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.stage_state = QtWidgets.QLabel()
        self.stage_state.setObjectName('bold_label')
        self.main_layout.addWidget(self.stage_state)

        self.line_frame = QtWidgets.QFrame()
        self.line_frame.setFixedHeight(1)
        self.line_frame.setStyleSheet('background-color:rgba(255,255,255,20)')
        self.main_layout.addWidget(self.line_frame)

        self.stage_comment = tag_label.tag_label()
        self.main_layout.addWidget(self.stage_comment)

    def show_comment(self, stage_row):
        self.stage_state.setText(stage_row['state'].capitalize())
        self.stage_state.setStyleSheet(f"color:{ressources._states_colors_[stage_row['state']]};")
        self.stage_comment.setText(stage_row['tracking_comment'])
        gui_utils.move_ui(self, 20)
        self.show()
        self.adjustSize()

    def move_ui(self):
        gui_utils.move_ui(self, 20)

class asset_widget(QtWidgets.QWidget):
    def __init__(self, asset_row, preview_row, parent=None):
        super(asset_widget, self).__init__(parent)
        self.type = 'asset'
        self.asset_row = asset_row
        self.preview_row = preview_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,8,0)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedWidth(72)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName('production_manager_variant_frame')
        self.main_layout.addWidget(self.image_label)

        self.asset_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.asset_name_label)

    def fill_ui(self):
        self.asset_name_label.setText(self.asset_row['name'])

        image = ressources._no_preview_
        if self.preview_row['manual_override'] is None:
            if self.preview_row['preview_path'] is not None:
                image = self.preview_row['preview_path']
        else:
            image = self.preview_row['manual_override']
        self.image_label.setPixmap(QtGui.QIcon(image).pixmap(72, 40))

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
    show_comment_signal = pyqtSignal(dict)
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

    def connect_functions(self):
        self.state_label.state_signal.connect(self.state_signal.emit)
        self.state_label.enter.connect(self.show_comment)
        self.state_label.leave.connect(self.hide_comment)
        self.state_label.move_event.connect(self.move_comment.emit)
        self.user_image_label.assignment_signal.connect(self.assignment_signal.emit)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.color_frame = QtWidgets.QFrame()
        self.color_frame.setFixedWidth(4)
        self.main_layout.addWidget(self.color_frame)

        self.data_widget = QtWidgets.QWidget()
        self.data_widget.setObjectName('transparent_widget')
        self.data_layout = QtWidgets.QHBoxLayout()
        self.data_layout.setSpacing(6)
        self.data_layout.setContentsMargins(6,6,6,6)
        self.data_widget.setLayout(self.data_layout)
        self.main_layout.addWidget(self.data_widget)

        self.state_label = state_widget()
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_label.setMinimumHeight(22)
        self.data_layout.addWidget(self.state_label)

        self.user_image_label = assignment_widget()
        self.user_image_label.setFixedSize(QtCore.QSize(24,24))
        self.data_layout.addWidget(self.user_image_label)

        self.percent_label = QtWidgets.QLabel()
        self.data_layout.addWidget(self.percent_label)

    def show_comment(self):
        if self.stage_row['tracking_comment'] and self.stage_row['tracking_comment'] != '':
            self.show_comment_signal.emit(self.stage_row)

    def hide_comment(self):
        self.hide_comment_signal.emit(1)

    def fill_ui(self):
        self.color_frame.setStyleSheet('background-color:%s;'%ressources._stages_colors_[self.stage_row['name']])
        self.state_label.setText(self.stage_row['state'])
        self.state_label.setStyleSheet('#bold_label{background-color:%s;border-radius:13px;padding:6px;}'%ressources._states_colors_[self.stage_row['state']])
        self.user_image_label.setPixmap(self.users_images_dic[self.stage_row['assignment']])
        self.percent_label.setText(f"{int(self.stage_row['progress'])} %")

    def refresh(self, stage_row):
        self.stage_row = stage_row
        self.fill_ui()

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

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.states_menu_requested()

    def states_menu_requested(self):
        menu = gui_utils.QMenu(self)
        menu.addAction(QtGui.QIcon(ressources._state_todo_), 'todo')
        menu.addAction(QtGui.QIcon(ressources._state_wip_), 'wip')
        menu.addAction(QtGui.QIcon(ressources._state_done_), 'done')
        menu.addAction(QtGui.QIcon(ressources._state_error_), 'error')
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

class assignment_widget(QtWidgets.QLabel):

    assignment_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(assignment_widget, self).__init__(parent)

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
