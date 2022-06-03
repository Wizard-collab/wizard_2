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

stages_colors = dict()
stages_colors['modeling'] = 'rgba(255,81,81,ALPHA)'
stages_colors['rigging'] = 'rgba(81,255,121,ALPHA)'
stages_colors['grooming'] = 'rgba(255,209,81,ALPHA)'
stages_colors['texturing'] = 'rgba(81,90,255,ALPHA)'
stages_colors['shading'] = 'rgba(214,81,255,ALPHA)'

stages_colors['layout'] = 'rgba(255,81,81,ALPHA)'
stages_colors['animation'] = 'rgba(81,255,121,ALPHA)'
stages_colors['cfx'] = 'rgba(255,209,81,ALPHA)'
stages_colors['fx'] = 'rgba(55,220,255,ALPHA)'
stages_colors['camera'] = 'rgba(255,138,44,ALPHA)'
stages_colors['lighting'] = 'rgba(214,81,255,ALPHA)'
stages_colors['compositing'] = 'rgba(81,90,255,ALPHA)'

class production_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(production_manager_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Production manager - {environment.get_project_name()}")
        self.logging_widget = logging_widget.logging_widget()

        self.build_ui()
        self.search_thread = search_thread()
        self.users_ids = dict()
        self.asset_ids = dict()
        self.stage_ids = dict()
        self.variant_ids = dict()
        self.update_categories = True
        self.update_assets = True
        self.domain = None
        self.category = None
        self.domain_ids = []
        self.category_ids = []
        self.selection = []

        self.connect_functions()

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.assets_signal.connect(self.add_search_assets)
        self.search_thread.variants_signal.connect(self.add_search_variants)
        self.domain_comboBox.currentTextChanged.connect(self.refresh_categories)
        self.category_comboBox.currentTextChanged.connect(self.refresh_assets)
        self.select_all_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+A'), self)
        self.select_all_sc.activated.connect(self.select_all)
        self.list_view.clicked.connect(self.deselect_all)
        self.refresh_ui_button.clicked.connect(gui_server.refresh_team_ui)

    def apply_search(self):
        search = self.search_bar.text()
        self.update_search(search)

    def update_search(self, text):
        if text != '':
            asset = ''
            stage = ''
            assignment = ''
            state = ''
            text = text.replace(' ', '')
            searchs = text.split('&')
            for item in searchs:
                if self.domain == 'assets':
                    if 'asset:' in item:
                        asset = item.replace('asset:', '')
                if self.domain == 'sequences':
                    if 'shot:' in item:
                        asset = item.replace('shot:', '')
                if 'user:' in item:
                    assignment = item.replace('user:', '')
                if 'state:' in item:
                    state = item.replace('state:', '')
                if 'stage:' in item:
                    stage = item.replace('stage:', '')
            self.hide_columns(stage)
            self.search_thread.update_search(asset=asset, assignment=assignment, state=state)
        else:
            self.unhide_all()

    def hide_columns(self, stage):
        if stage != '':
            for domain_stage in self.stages_list:
                if stage in domain_stage:
                    self.list_view.setColumnHidden(self.stages_list.index(domain_stage)+2, 0)
                else:
                    self.list_view.setColumnHidden(self.stages_list.index(domain_stage)+2, 1)
        else:
            for domain_stage in self.stages_list:
                self.list_view.setColumnHidden(self.stages_list.index(domain_stage)+2, 0)
        self.refresh_infos()

    def unhide_all(self):
        asset_ids = list(self.asset_ids.keys())
        for asset_id in asset_ids:
            if asset_id in self.asset_ids.keys():
                self.asset_ids[asset_id]['item'].setHidden(0)
        variant_ids = list(self.variant_ids.keys())
        for variant_id in variant_ids:
            if variant_id in self.variant_ids.keys():
                self.variant_ids[variant_id]['widget'].setVisible(1)
        for stage in self.stages_list:
            self.list_view.setColumnHidden(self.stages_list.index(stage)+1, 0)
        self.refresh_infos()

    def add_search_assets(self, assets_list):
        asset_ids = self.asset_ids.keys()
        for asset_id in asset_ids:
            self.asset_ids[asset_id]['item'].setHidden(1-(asset_id in assets_list))
        self.refresh_infos()

    def add_search_variants(self, variants_list):
        variant_ids = list(self.variant_ids.keys())
        for variant_id in variant_ids:
            self.variant_ids[variant_id]['widget'].setVisible(variant_id in variants_list)
        self.refresh_infos()

    def build_ui(self):
        self.setMinimumWidth(1500)
        self.setMinimumHeight(1000)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QFrame()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.domain_comboBox = gui_utils.QComboBox()
        self.header_layout.addWidget(self.domain_comboBox)
        self.category_comboBox = gui_utils.QComboBox()
        self.category_comboBox.setMinimumHeight(32)
        self.header_layout.addWidget(self.category_comboBox)

        self.search_bar = gui_utils.search_bar(red=36, green=36, blue=43, alpha=255)
        self.header_layout.addWidget(self.search_bar)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.list_view = custom_list_view(self)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('production_manager_list_widget')
        self.list_view.setIconSize(QtCore.QSize(30,30))
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.main_layout.addWidget(self.list_view)

        self.footer_widget = QtWidgets.QFrame()
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setSpacing(6)
        self.footer_widget.setLayout(self.footer_layout)
        self.main_layout.addWidget(self.footer_widget)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(QtCore.QSize(22,22))
        self.icon_label.setPixmap(QtGui.QIcon(ressources._info_icon_).pixmap(22))
        self.footer_layout.addWidget(self.icon_label)

        self.footer_layout.addWidget(self.logging_widget)
        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.footer_layout.addWidget(self.refresh_label)

        self.selection_info_label = QtWidgets.QLabel()
        self.footer_layout.addWidget(self.selection_info_label)

        self.refresh_ui_button = QtWidgets.QPushButton()
        self.refresh_ui_button.setFixedSize(QtCore.QSize(30, 30))
        gui_utils.application_tooltip(self.refresh_ui_button, "Manually refresh the ui")
        self.refresh_ui_button.setIcon(QtGui.QIcon(ressources._refresh_icon_))
        self.footer_layout.addWidget(self.refresh_ui_button)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def refresh(self):
        if self.isVisible():
            start_time = time.time()
            self.refresh_domains()
            self.update_refresh_time(start_time)

    def refresh_domains(self):
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
                self.update_header()
            domain_id = project.get_domain_by_name(current_domain, 'id')
            category_rows = project.get_domain_childs(domain_id)
            for category_row in category_rows:
                if category_row['id'] not in self.category_ids:
                    self.category_comboBox.addItem(category_row['name'])
                    self.category_ids.append(category_row['id'])
            self.update_assets = True
            self.refresh_assets()

    def update_header(self):
        if self.domain == 'assets':
            self.stages_list = assets_vars._assets_stages_list_
            self.headers_label_list = ['Asset', 'Preview']+self.stages_list
        elif self.domain == 'sequences':
            self.stages_list = assets_vars._sequences_stages_list_
            self.headers_label_list = ['Shot', 'Preview']+self.stages_list

        self.list_view.setColumnCount(len(self.stages_list)+2)
        self.list_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.list_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.list_view.setHeaderLabels(self.headers_label_list)

        for stage in self.stages_list:
            self.list_view.header().setSectionResizeMode(self.stages_list.index(stage)+2, QtWidgets.QHeaderView.Stretch)

    def clear_assets(self):
        self.asset_ids = dict()
        self.stage_ids = dict()
        self.variant_ids = dict()
        self.list_view.clear()

    def refresh_assets(self):
        if self.update_assets:
            current_category = self.category_comboBox.currentText()
            if current_category != self.category:
                self.clear_assets()
                self.category = current_category
            category_id = project.get_category_data_by_name(current_category, 'id')

            asset_rows = project.get_category_childs(category_id) 
            assets_preview_rows = project.get_all_assets_preview()
            
            assets_preview = dict()
            for assets_preview_row in assets_preview_rows:
                assets_preview[assets_preview_row['asset_id']] = assets_preview_row

            stage_rows = project.get_all_stages()
            variant_rows = project.get_all_variants()

            for asset_row in asset_rows:
                if asset_row['id'] not in self.asset_ids.keys():
                    self.asset_ids[asset_row['id']] = dict()
                    self.asset_ids[asset_row['id']]['row'] = asset_row
                    self.asset_ids[asset_row['id']]['preview_row'] = assets_preview[asset_row['id']]
                    item = custom_asset_listWidgetItem(self.asset_ids[asset_row['id']]['row'],
                                                            self.asset_ids[asset_row['id']]['preview_row'],
                                                            self.domain,
                                                            self.list_view.invisibleRootItem())
                    self.asset_ids[asset_row['id']]['item'] = item
                    self.asset_ids[asset_row['id']]['widget'] = item.widget
                    self.asset_ids[asset_row['id']]['widget'].clicked.connect(self.select_asset)
                else:
                    if self.asset_ids[asset_row['id']]['row'] != asset_row:
                        self.asset_ids[asset_row['id']]['item'].refresh_asset(asset_row)
                        self.asset_ids[asset_row['id']]['row'] = asset_row
                    if self.asset_ids[asset_row['id']]['preview_row'] != assets_preview[asset_row['id']]:
                        self.asset_ids[asset_row['id']]['item'].refresh_asset_preview(assets_preview[asset_row['id']])
                        self.asset_ids[asset_row['id']]['preview_row'] = assets_preview[asset_row['id']]


            for stage_row in stage_rows:
                if stage_row['asset_id'] in self.asset_ids.keys():
                    if stage_row['id'] not in self.stage_ids.keys():
                        self.stage_ids[stage_row['id']] = dict()
                        self.stage_ids[stage_row['id']]['row'] = stage_row
                        self.asset_ids[self.stage_ids[stage_row['id']]['row']['asset_id']]['item'].add_stage(self.stage_ids[stage_row['id']]['row'], self.stages_list)
                        self.stage_ids[stage_row['id']]['asset_item'] = self.asset_ids[self.stage_ids[stage_row['id']]['row']['asset_id']]['item']

            for variant_row in variant_rows:
                if variant_row['stage_id'] in self.stage_ids.keys():
                    if variant_row['id'] not in self.variant_ids.keys():
                        self.variant_ids[variant_row['id']] = dict()
                        self.variant_ids[variant_row['id']]['row'] = variant_row
                        variant_widget = self.stage_ids[self.variant_ids[variant_row['id']]['row']['stage_id']]['asset_item'].add_variant(self.variant_ids[variant_row['id']]['row'])
                        self.variant_ids[variant_row['id']]['item'] = self.stage_ids[self.variant_ids[variant_row['id']]['row']['stage_id']]['asset_item']
                        variant_widget.clicked.connect(self.select)
                        variant_widget.modify_state_signal.connect(self.modify_selection_state)
                        variant_widget.modify_assignment_signal.connect(self.modify_selection_assignment)
                        self.variant_ids[variant_row['id']]['widget'] = variant_widget
                    else:
                        if variant_row != self.variant_ids[variant_row['id']]['row']:
                            self.variant_ids[variant_row['id']]['row'] = variant_row
                            self.stage_ids[self.variant_ids[variant_row['id']]['row']['stage_id']]['asset_item'].refresh_variant(self.variant_ids[variant_row['id']]['row'])
            self.apply_search()
            self.refresh_infos()

    def refresh_infos(self):
        variant_ids = list(self.variant_ids.keys())
        visible_items_count = 0
        visible_selected_items_count = 0
        for variant_id in variant_ids:
            if self.variant_ids[variant_id]['widget'].isVisible():
                visible_items_count += 1
                if variant_id in self.selection:
                    visible_selected_items_count += 1
        self.selection_info_label.setText(f'{str(visible_selected_items_count)} selected/{str(visible_items_count)} items')

    def select_asset(self, asset_id):
        if asset_id in self.asset_ids.keys():
            self.select(list(self.asset_ids[asset_id]['item'].variant_ids.keys()))

    def select_all(self):
        self.selection = list(self.variant_ids.keys())
        self.refresh_selection()

    def deselect_all(self):
        self.clear_selection()
        self.refresh_selection()

    def select(self, variant_ids):
        modifier = QtWidgets.QApplication.keyboardModifiers()
        if modifier != QtCore.Qt.ShiftModifier and modifier != QtCore.Qt.ControlModifier:
            self.clear_selection()
        if modifier == QtCore.Qt.ControlModifier:
            for variant_id in variant_ids:
                if variant_id in self.selection:
                    self.selection.remove(variant_id)
        else:
            self.selection += variant_ids
        self.refresh_selection()

    def refresh_selection(self):
        variant_ids = list(self.variant_ids.keys())
        for variant_id in variant_ids:
            self.variant_ids[variant_id]['widget'].set_selected(selected=(variant_id in self.selection))
        self.refresh_infos()

    def clear_selection(self):
        self.selection = []

    def modify_selection_state(self, state):
        variant_ids = list(self.variant_ids.keys())
        for variant_id in variant_ids:
            if variant_id in self.selection:
                if (self.variant_ids[variant_id]['row']['state'] != state) and (self.variant_ids[variant_id]['widget'].isVisible()):
                    assets.modify_variant_state(variant_id, state)
        gui_server.refresh_team_ui()

    def modify_selection_assignment(self, assignment):
        variant_ids = list(self.variant_ids.keys())
        for variant_id in variant_ids:
            if variant_id in self.selection:
                if (self.variant_ids[variant_id]['row']['assignment'] != assignment) and (self.variant_ids[variant_id]['widget'].isVisible()):
                    assets.modify_variant_assignment(variant_id, assignment)
        gui_server.refresh_team_ui()

class custom_list_view(QtWidgets.QTreeWidget):

    clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super(custom_list_view, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        self.clicked.emit(1)

class custom_asset_listWidgetItem(QtWidgets.QTreeWidgetItem, QtCore.QObject):

    def __init__(self, asset_row, preview_row, domain, parent=None):
        super(custom_asset_listWidgetItem, self).__init__(parent)
        self.stage_ids = dict()
        self.variant_ids = dict()
        self.asset_row = asset_row
        self.preview_row = preview_row
        self.domain = domain
        self.widget = asset_widget(self.asset_row, self.domain)
        self.image_widget = image_widget(self.preview_row)
        self.treeWidget().setItemWidget(self, 0, self.widget)
        self.treeWidget().setItemWidget(self, 1, self.image_widget)

    def refresh_asset(self, asset_row):
        self.asset_row = asset_row
        self.widget.refresh_asset(self.asset_row)

    def refresh_asset_preview(self, preview_row):
        self.preview_row = preview_row
        self.image_widget.refresh_asset_preview(self.preview_row)

    def add_stage(self, stage_row, stage_list):
        self.stage_ids[stage_row['id']] = dict()
        self.stage_ids[stage_row['id']]['row'] = stage_row
        widget = stage_widget(stage_row, self.treeWidget())
        self.stage_ids[stage_row['id']]['widget'] = widget
        index = stage_list.index(stage_row['name'])+2
        self.stage_ids[stage_row['id']]['index'] = index
        self.treeWidget().setItemWidget(self, index, widget)

    def add_variant(self, variant_row):
        widget = variant_widget(variant_row,
                                self.stage_ids[variant_row['stage_id']]['row']['name'],
                                self.treeWidget())
        stage_widget = self.stage_ids[variant_row['stage_id']]['widget']
        stage_widget.add_variant(widget)
        self.variant_ids[variant_row['id']] = dict()
        self.variant_ids[variant_row['id']]['row'] = variant_row
        self.variant_ids[variant_row['id']]['widget'] = widget
        return widget

    def refresh_variant(self, variant_row):
        self.variant_ids[variant_row['id']]['widget'].refresh(variant_row)

class image_widget(QtWidgets.QWidget):
    def __init__(self, preview_row, parent=None):
        super(image_widget, self).__init__(parent)
        self.preview_row = preview_row
        self.build_ui()
        self.fill_ui()

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

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(1,1,1,1)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName('production_manager_variant_frame')
        self.main_layout.addWidget(self.image_label)

    def refresh_asset_preview(self, preview_row):
        self.preview_row = preview_row
        self.fill_ui()

    def fill_ui(self):
        image = ressources._no_preview_
        if self.preview_row['manual_override'] is None:
            if self.preview_row['preview_path'] is not None:
                image = self.preview_row['preview_path']
        else:
            image = self.preview_row['manual_override']
        self.image_label.setPixmap(QtGui.QIcon(image).pixmap(132, 80))

class asset_widget(QtWidgets.QWidget):

    clicked = pyqtSignal(int)

    def __init__(self, asset_row, domain, parent=None):
        super(asset_widget, self).__init__(parent)
        self.asset_row = asset_row
        self.domain = domain
        self.build_ui()
        self.fill_ui()

    def mouseReleaseEvent(self, event):
        self.clicked.emit(self.asset_row['id'])

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(1,1,1,1)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('production_manager_variant_frame')
        self.main_frame_layout = QtWidgets.QVBoxLayout()
        self.main_frame_layout.setContentsMargins(6,6,6,6)
        self.main_frame_layout.setSpacing(4)
        self.main_frame.setLayout(self.main_frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.main_frame_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.asset_name_label = QtWidgets.QLabel()
        self.asset_name_label.setObjectName('bold_label')
        self.asset_name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.main_frame_layout.addWidget(self.asset_name_label)

        if self.domain == 'sequences':
            self.frame_range_widget = QtWidgets.QWidget()
            self.frame_range_widget.setObjectName('transparent_widget')
            self.frame_range_layout = QtWidgets.QHBoxLayout()
            self.frame_range_layout.setContentsMargins(0,0,0,0)
            self.frame_range_layout.setSpacing(4)
            self.frame_range_widget.setLayout(self.frame_range_layout)
            self.main_frame_layout.addWidget(self.frame_range_widget)
            self.in_frame_label = QtWidgets.QLabel()
            self.in_frame_label.setObjectName('gray_label')
            self.in_frame_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.frame_range_layout.addWidget(self.in_frame_label)
            self.out_frame_label = QtWidgets.QLabel()
            self.out_frame_label.setObjectName('gray_label')
            self.out_frame_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.frame_range_layout.addWidget(self.out_frame_label)
            
        self.main_frame_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def refresh_asset(self, asset_row):
        self.asset_row = asset_row
        self.fill_ui()

    def fill_ui(self):
        self.asset_name_label.setText(self.asset_row['name'])
        if self.domain == 'sequences':
            self.in_frame_label.setText(str(self.asset_row['inframe']))
            self.out_frame_label.setText(str(self.asset_row['outframe']))

class stage_widget(QtWidgets.QWidget):

    def __init__(self, stage_row, parent=None):
        super(stage_widget, self).__init__(parent)
        self.stage_row = stage_row
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(1,1,1,1)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def add_variant(self, variant_widget):
        self.main_layout.insertWidget(self.main_layout.count() - 1, variant_widget)

class variant_widget(QtWidgets.QFrame):

    clicked = pyqtSignal(list)
    modify_state_signal = pyqtSignal(str)
    modify_assignment_signal = pyqtSignal(str)

    def __init__(self, variant_row, stage, parent=None):
        super(variant_widget, self).__init__(parent)
        self.variant_row = variant_row
        self.stage = stage
        self.selected = False
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def refresh(self, variant_row):
        self.variant_row = variant_row
        self.fill_ui()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.show_context_menu()
        elif event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit([self.variant_row['id']])

    def show_context_menu(self):
        menu = gui_utils.QMenu(self)
        launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), 'Launch work environment')
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == launch_action:
                self.launch()

    def launch(self):
        work_env_id = project.get_variant_data(self.variant_row['id'], 'default_work_env_id')
        work_versions_ids = project.get_work_versions(work_env_id, 'id')
        if work_versions_ids is not None:
            if len(work_versions_ids) >= 1:
                launch.launch_work_version(work_versions_ids[-1])
                gui_server.refresh_team_ui()
            else:
                logger.warning('No version to launch')
        else:
            logger.warning('No version to launch')

    def set_selected(self, selected=True):
        self.selected = selected
        if selected:
            self.setStyleSheet('#production_manager_variant_frame{background-color:%s;}'%stages_colors[self.stage].replace('ALPHA', str(120)))
        else:
            self.setStyleSheet('''#production_manager_variant_frame{background-color:%s;}
                                #production_manager_variant_frame:hover{background-color:%s;}'''%(stages_colors[self.stage].replace('ALPHA', str(40)),
                                                                                                    stages_colors[self.stage].replace('ALPHA', str(60))))

    def build_ui(self):
        self.setObjectName('production_manager_variant_frame')
        self.setStyleSheet('''#production_manager_variant_frame{background-color:%s;}
                                #production_manager_variant_frame:hover{background-color:%s;}'''%(stages_colors[self.stage].replace('ALPHA', str(40)),
                                                                                                    stages_colors[self.stage].replace('ALPHA', str(60))))
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QtWidgets.QLabel(self.variant_row['name']))

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.datas_widget = QtWidgets.QFrame()
        self.datas_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.datas_widget.setMinimumHeight(36)
        self.datas_widget.setObjectName('production_manager_state_frame')
        self.datas_layout = QtWidgets.QHBoxLayout()
        self.datas_layout.setContentsMargins(3,3,8,3)
        self.datas_layout.setSpacing(3)
        self.datas_widget.setLayout(self.datas_layout)
        self.content_layout.addWidget(self.datas_widget)

        self.user_image_label = QtWidgets.QLabel()
        self.user_image_label.setFixedSize(QtCore.QSize(30,30))
        self.datas_layout.addWidget(self.user_image_label)

        self.modify_assignment_button = QtWidgets.QPushButton()
        self.modify_assignment_button.setObjectName('dropdown_button')
        self.modify_assignment_button.setFixedSize(QtCore.QSize(14,14))
        self.datas_layout.addWidget(self.modify_assignment_button)

        self.state_label = QtWidgets.QLabel()
        self.state_label.setObjectName('bold_label')
        self.datas_layout.addWidget(self.state_label)

        self.modify_state_button = QtWidgets.QPushButton()
        self.modify_state_button.setObjectName('dropdown_button')
        self.modify_state_button.setFixedSize(QtCore.QSize(14,14))
        self.datas_layout.addWidget(self.modify_state_button)

        self.comment_label = QtWidgets.QLabel()
        self.content_layout.addWidget(self.comment_label)
        
        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.progress_bar_widget = QtWidgets.QWidget()
        self.progress_bar_widget.setObjectName('transparent_widget')
        self.progress_bar_layout = QtWidgets.QHBoxLayout()
        self.progress_bar_layout.setContentsMargins(0,0,0,0)
        self.progress_bar_layout.setSpacing(4)
        self.progress_bar_widget.setLayout(self.progress_bar_layout)
        self.main_layout.addWidget(self.progress_bar_widget)

        self.time_progress_bar = QtWidgets.QProgressBar()
        self.time_progress_bar.setMaximumHeight(6)
        self.progress_bar_layout.addWidget(self.time_progress_bar)

    def fill_ui(self):
        self.state_label.setText(self.variant_row['state'])
        if self.variant_row['tracking_comment'] is not None:
            self.comment_label.setText(self.variant_row['tracking_comment'])
        user_image =  repository.get_user_row_by_name(self.variant_row['assignment'], 'profile_picture')
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 30)
        self.user_image_label.setPixmap(pm)

        if self.variant_row['state'] == 'todo':
            color = '#3a3a41'
        elif self.variant_row['state'] == 'wip':
            color = '#ffbc6d'
        elif self.variant_row['state'] == 'done':
            color = '#a6db76'
        elif self.variant_row['state'] == 'error':
            color = '#e66f6f'
        self.datas_widget.setStyleSheet('#production_manager_state_frame{background-color:%s;}'%color)

        if self.variant_row['estimated_time'] is not None:
            percent = (float(self.variant_row['work_time'])/float(self.variant_row['estimated_time']))*100
            self.time_progress_bar.setValue(percent)
            if percent > 100:
                percent = 100
                if self.variant_row['state'] != 'done':
                    self.time_progress_bar.setStyleSheet('::chunk{background-color:#ff5d5d;}')
            else:
                self.time_progress_bar.setStyleSheet('::chunk{background-color:#ffad4d;}')
            if self.variant_row['state'] == 'done':
                self.time_progress_bar.setStyleSheet('::chunk{background-color:#95d859;}')
                self.time_progress_bar.setValue(100)
        else:
            self.time_progress_bar.setValue(0)
            if self.variant_row['state'] == 'done':
                self.time_progress_bar.setStyleSheet('::chunk{background-color:#95d859;}')
                self.time_progress_bar.setValue(100)

    def connect_functions(self):
        self.modify_state_button.clicked.connect(self.states_menu_requested)
        self.modify_assignment_button.clicked.connect(self.users_menu_requested)

    def states_menu_requested(self, point):
        if not self.selected:
            self.clicked.emit([self.variant_row['id']])
        menu = gui_utils.QMenu(self)
        menu.addAction(QtGui.QIcon(ressources._state_todo_), 'todo')
        menu.addAction(QtGui.QIcon(ressources._state_wip_), 'wip')
        menu.addAction(QtGui.QIcon(ressources._state_done_), 'done')
        menu.addAction(QtGui.QIcon(ressources._state_error_), 'error')
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.modify_state(action.text())

    def users_menu_requested(self, point):
        if not self.selected:
            self.clicked.emit([self.variant_row['id']])
        users_actions = []
        menu = gui_utils.QMenu(self)
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            user_row = repository.get_user_data(user_id)
            icon = QtGui.QIcon()
            pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 22)
            icon.addPixmap(pm)
            menu.addAction(icon, user_row['user_name'])
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.modify_assignment(action.text())

    def modify_state(self, state):
        self.modify_state_signal.emit(state)

    def modify_assignment(self, user_name):
        self.modify_assignment_signal.emit(user_name)

class search_thread(QtCore.QThread):

    assets_signal = pyqtSignal(list)
    variants_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(search_thread, self).__init__(parent)
        self.asset_string = ''
        self.assignment_string = ''
        self.state_string = ''
        self.running = False

    def run(self):

        assets_list = []
        variants_list = []

        if self.running:
            if self.asset_string != '':
                asset_ids = project.search_asset(self.asset_string, column='id')
                for asset_id in asset_ids:
                    if not self.running:
                        break
                    assets_list.append(asset_id)

            combined_variant_ids = []

            if self.assignment_string != '':
                variant_ids = project.search_variant_by_column_data(('assignment', self.assignment_string), column='id')
                for variant_id in variant_ids:
                    if not self.running:
                        break
                    if self.state_string != '':
                        combined_variant_ids.append(variant_id)
                    else:
                        variants_list.append(variant_id)

            if self.state_string != '':
                variant_ids = project.search_variant_by_column_data(('state', self.state_string), column='id')
                for variant_id in variant_ids:
                    if not self.running:
                        break
                    if (self.assignment_string != '') and (variant_id in combined_variant_ids):
                        variants_list.append(variant_id)
                    elif (self.assignment_string != '') and (variant_id not in combined_variant_ids):
                        pass
                    else:
                        variants_list.append(variant_id)

        if self.asset_string != '':
            self.assets_signal.emit(assets_list)
        if self.assignment_string != '' or self.state_string != '':
            self.variants_signal.emit(variants_list)

    def update_search(self, asset='', assignment='', state=''):
        self.asset_string = asset
        self.assignment_string = assignment
        self.state_string = state
        self.running = True
        self.start()

    def stop(self):
        self.running = False
