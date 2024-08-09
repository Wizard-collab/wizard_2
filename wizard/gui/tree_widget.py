# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import time
import os
import copy
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging
import traceback

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.core import user
from wizard.core import path_utils
from wizard.core import subtasks_library
from wizard.core import repository
from wizard.core import tools
from wizard.core import stats
from wizard.core import image
from wizard.vars import user_vars
from wizard.vars import assets_vars
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import confirm_widget
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class tree_widget(QtWidgets.QFrame):

    stage_changed_signal = pyqtSignal(object)
    launch_stage_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(tree_widget, self).__init__(parent)

        self.creation_items_visibility = 1
        self.assignment_visibility = 1
        self.state_visibility = 1
        self.priority_visibility = 1
        self.color_visibility = 0
        self.progress_visibility = 1

        self.domain_ids=dict()
        self.category_ids=dict()
        self.assets_groups_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()
        self.creation_items=[]

        self.users_icons_dic = dict()

        self.build_ui()
        self.connect_functions()

    def refresh_users_icons_dic(self):
        for user_row in repository.get_users_list():
            if user_row['user_name'] not in self.users_icons_dic.keys():
                user_icon = QtGui.QIcon()
                pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 16)
                user_icon.addPixmap(pm)
                self.users_icons_dic[user_row['user_name']] = user_icon

    def build_ui(self):
        self.icons_dic = dict()
        self.icons_dic['add'] = QtGui.QIcon(ressources._add_icon_small_)
        self.icons_dic['folder'] = QtGui.QIcon(ressources._folder_icon_small_)
        self.icons_dic['assets_groups'] = QtGui.QIcon(ressources._assets_group_icon_)
        self.icons_dic['domain'] = dict()
        self.icons_dic['domain']['assets'] = QtGui.QIcon(ressources._assets_icon_)
        self.icons_dic['domain']['library'] = QtGui.QIcon(ressources._library_icon_)
        self.icons_dic['domain']['sequences'] = QtGui.QIcon(ressources._sequences_icon_)
        self.icons_dic['stage'] = dict()
        self.icons_dic['stage']['modeling'] = QtGui.QIcon(ressources._modeling_icon_)
        self.icons_dic['stage']['rigging'] = QtGui.QIcon(ressources._rigging_icon_)
        self.icons_dic['stage']['grooming'] = QtGui.QIcon(ressources._grooming_icon_)
        self.icons_dic['stage']['texturing'] = QtGui.QIcon(ressources._texturing_icon_)
        self.icons_dic['stage']['shading'] = QtGui.QIcon(ressources._shading_icon_)
        self.icons_dic['stage']['layout'] = QtGui.QIcon(ressources._layout_icon_)
        self.icons_dic['stage']['animation'] = QtGui.QIcon(ressources._animation_icon_)
        self.icons_dic['stage']['cfx'] = QtGui.QIcon(ressources._cfx_icon_)
        self.icons_dic['stage']['fx'] = QtGui.QIcon(ressources._fx_icon_)
        self.icons_dic['stage']['lighting'] = QtGui.QIcon(ressources._lighting_icon_)
        self.icons_dic['stage']['camera'] = QtGui.QIcon(ressources._camera_icon_)
        self.icons_dic['stage']['compositing'] = QtGui.QIcon(ressources._compositing_icon_)
        self.icons_dic['stage']['custom'] = QtGui.QIcon(ressources._custom_icon_)
        self.icons_dic['stage']['camrig'] = QtGui.QIcon(ressources._camera_rig_icon_)
        self.icons_dic['priority'] = dict()
        for priority in assets_vars._priority_list_:
            self.icons_dic['priority'][priority] = QtGui.QIcon(ressources._priority_icons_list_[priority])

        self.setMinimumWidth(330)
        self.resize(330, self.height())
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.search_frame = QtWidgets.QFrame()
        self.search_layout = QtWidgets.QHBoxLayout()
        self.search_layout.setContentsMargins(0,0,0,0)
        self.search_layout.setSpacing(8)
        self.search_frame.setLayout(self.search_layout)

        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific item")
        self.search_bar.setPlaceholderText('characters&Lola&grooming')
        self.search_layout.addWidget(self.search_bar)

        self.main_layout.addWidget(self.search_frame)

        self.data_label = QtWidgets.QLabel()
        self.data_label.setObjectName('tree_datas_label')
        self.main_layout.addWidget(self.data_label)

        self.tree = tree()
        self.tree.setObjectName('delegate_tree')

        self.tree.setAnimated(0)
        self.tree.setColumnCount(5)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().resizeSection(0, 190)
        self.tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tree.header().resizeSection(1, 16)
        self.tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(2, 16)
        self.tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(3, 32)
        self.tree.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tree.header().resizeSection(4, 52)
        self.tree.header().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tree.setIconSize(QtCore.QSize(16, 16))
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree.setAlternatingRowColors(True)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.tree)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('tree_datas_label')
        self.main_layout.addWidget(self.refresh_label)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread = search_thread()
        self.search_thread.item_signal.connect(self.add_search_item)
        self.tree.itemDoubleClicked.connect(self.double_click)
        self.tree.itemSelectionChanged.connect(self.item_changed)
        self.tree.customContextMenuRequested.connect(self.context_menu_requested)
        self.tree.move_asset_to_assets_group.connect(self.move_asset_to_assets_group)
        self.tree.remove_asset_from_assets_group.connect(self.remove_asset_from_assets_group)

    def item_changed(self):
        item = self.tree.currentItem()
        if item:
            if item.instance_type == 'stage':
                self.stage_changed_signal.emit(item.instance_id)
            else:
                self.stage_changed_signal.emit(None)
        else:
            self.stage_changed_signal.emit(None)

    def init_tree(self):
        self.set_context()
        self.domain_ids=dict()
        self.category_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()
        self.tree.clear()

    def set_context(self):
        context_dic = dict()
        context_dic['creation_items_visibility'] = self.creation_items_visibility
        context_dic['assignment_visibility'] = self.assignment_visibility
        context_dic['state_visibility'] = self.state_visibility
        context_dic['priority_visibility'] = self.priority_visibility
        context_dic['color_visibility'] = self.color_visibility
        context_dic['progress_visibility'] = self.progress_visibility
        context_dic['expanded_domains'] = []
        context_dic['expanded_categories'] = []
        context_dic['expanded_assets'] = []
        context_dic['selected_instance'] = None
        context_dic['search_string'] = self.search_bar.text()
        for domain_id in self.domain_ids.keys():
            if self.domain_ids[domain_id].isExpanded():
                context_dic['expanded_domains'].append(domain_id)
        for category_id in self.category_ids.keys():
            if self.category_ids[category_id].isExpanded():
                context_dic['expanded_categories'].append(category_id)
        for asset_id in self.asset_ids.keys():
            if self.asset_ids[asset_id].isExpanded():
                context_dic['expanded_assets'].append(asset_id)
        selected_item = self.tree.currentItem()
        if selected_item:
            if 'creation' not in selected_item.instance_type:
                context_dic['selected_instance'] = (selected_item.instance_type,
                                                            selected_item.instance_id)
        user.user().add_context(user_vars._tree_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._tree_context_)
        if context_dic is not None and context_dic != dict():
            for id in context_dic['expanded_domains']:
                if id in self.domain_ids.keys():
                    self.domain_ids[id].setExpanded(1)
            for id in context_dic['expanded_categories']:
                if id in self.category_ids.keys():
                    self.category_ids[id].setExpanded(1)
            for id in context_dic['expanded_assets']:
                if id in self.asset_ids.keys():
                    self.asset_ids[id].setExpanded(1)
            if context_dic['selected_instance']:
                if context_dic['selected_instance'][0] == 'domain':
                    if context_dic['selected_instance'][1] in self.domain_ids.keys():
                        self.focus_on_item(self.domain_ids[context_dic['selected_instance'][1]])
                if context_dic['selected_instance'][0] == 'category':
                    if context_dic['selected_instance'][1] in self.category_ids.keys():
                        self.focus_on_item(self.category_ids[context_dic['selected_instance'][1]])
                if context_dic['selected_instance'][0] == 'asset':
                    if context_dic['selected_instance'][1] in self.asset_ids.keys():
                        self.focus_on_item(self.asset_ids[context_dic['selected_instance'][1]])
                if context_dic['selected_instance'][0] == 'stage':
                    if context_dic['selected_instance'][1] in self.stage_ids.keys():
                        self.focus_on_item(self.stage_ids[context_dic['selected_instance'][1]])
            self.search_bar.setText(context_dic['search_string'])
            self.apply_search()
            self.creation_items_visibility = context_dic['creation_items_visibility']
            self.state_visibility = context_dic['state_visibility']
            if 'assignment_visibility' in context_dic.keys():
                self.assignment_visibility = context_dic['assignment_visibility']
            if 'priority_visibility' in context_dic.keys():
                self.priority_visibility = context_dic['priority_visibility']
            if 'color_visibility' in context_dic.keys():
                self.color_visibility = context_dic['color_visibility']
            if 'progress_visibility' in context_dic.keys():
                self.color_visibility = context_dic['progress_visibility']
            self.update_creation_items_visibility()
            self.update_columns_visibility()
            self.update_color_visibility()

    def refresh(self, hard=None):
        start_time = time.perf_counter()
        if hard:
            self.init_tree()

        self.refresh_users_icons_dic()

        self.project_category_ids = []
        self.project_assets_groups_ids = []
        self.project_asset_ids = []
        self.project_stage_ids = []

        for domain_row in project.get_domains():
            self.add_domain(domain_row)
        for category_row in project.get_all_categories():
            self.add_category(category_row)
            self.project_category_ids.append(category_row['id'])
        for group_row in project.get_all_assets_groups():
            self.add_assets_group(group_row)
            self.project_assets_groups_ids.append(group_row['id'])
        for asset_row in project.get_all_assets():
            self.add_asset(asset_row)
            self.project_asset_ids.append(asset_row['id'])
        for stage_row in project.get_all_stages():
            self.add_stage(stage_row)
            self.project_stage_ids.append(stage_row['id'])

        stage_ids = list(self.stage_ids.keys())
        for id in stage_ids:
            if id not in self.project_stage_ids:
                self.remove_stage(id)  
        asset_ids = list(self.asset_ids.keys())
        for id in asset_ids:
            if id not in self.project_asset_ids:
                self.remove_asset(id)     
        category_ids = list(self.category_ids.keys())
        for id in category_ids:
            if id not in self.project_category_ids:
                self.remove_category(id)
        assets_groups_ids = list(self.assets_groups_ids.keys())
        for id in assets_groups_ids:
            if id not in self.project_assets_groups_ids:
                self.remove_assets_group(id)
        
        for domain_id in self.domain_ids.keys():
            self.sort_domain_children(domain_id)
        for category_id in self.category_ids.keys():
            self.sort_category_children(category_id)
        for asset_group_id in self.assets_groups_ids.keys():
            self.sort_asset_group_children(asset_group_id)
        for asset_id in self.asset_ids.keys():
            self.sort_asset_children(asset_id)

        assets_progresses, categories_progresses, domains_progresses = stats.get_all_progresses()
        for asset_id in assets_progresses.keys():
            self.asset_ids[asset_id].progress_indicator.set_progress(assets_progresses[asset_id])
        for category_id in categories_progresses.keys():
            self.category_ids[category_id].progress_indicator.set_progress(categories_progresses[category_id])
        for domain_id in domains_progresses.keys():
            self.domain_ids[domain_id].progress_indicator.set_progress(domains_progresses[domain_id])

        self.apply_search()
        self.refresh_datas()
        if hard:
            self.get_context()
        self.update_creation_items_visibility()
        self.update_color_visibility()
        self.update_refresh_time(start_time)

    def move_asset_to_assets_group(self, tuple):
        project.add_asset_to_assets_group(tuple[0], tuple[1])
        gui_server.refresh_team_ui()

    def remove_asset_from_assets_group(self, asset_id):
        project.remove_asset_from_assets_group(asset_id)
        gui_server.refresh_team_ui()

    def sort_domain_children(self, domain_id):
        if self.domain_ids[domain_id].instance_name == 'assets':
            return
        names_dic = dict()
        names = []
        creation_item = None
        for child_index in range(self.domain_ids[domain_id].childCount()):
            item = self.domain_ids[domain_id].child(child_index)
            if item.instance_type == 'category_creation':
                item.setText(50, str(0))
                continue
            names_dic[item.instance_name] = item
            names.append(item.instance_name)
        names = tools.natural_sort(names)
        for name in names:
            names_dic[name].setText(50, str(names.index(name)).zfill(10))
        self.domain_ids[domain_id].sortChildren(50, QtCore.Qt.AscendingOrder)

    def sort_category_children(self, category_id):
        names_dic = dict()
        names = []
        creation_item = None
        for child_index in range(self.category_ids[category_id].childCount()):
            item = self.category_ids[category_id].child(child_index)
            if item.instance_type == 'asset_creation':
                item.setText(50, str(0))
                continue
            names_dic[item.instance_name] = item
            names.append(item.instance_name)
        names = tools.natural_sort(names)
        for name in names:
            names_dic[name].setText(50, str(names.index(name)).zfill(10))
        self.category_ids[category_id].sortChildren(50, QtCore.Qt.AscendingOrder)

    def sort_asset_group_children(self, asset_group_id):
        names_dic = dict()
        names = []
        creation_item = None
        for child_index in range(self.assets_groups_ids[asset_group_id].childCount()):
            item = self.assets_groups_ids[asset_group_id].child(child_index)
            names_dic[item.instance_name] = item
            names.append(item.instance_name)
        names = tools.natural_sort(names)
        for name in names:
            names_dic[name].setText(50, str(names.index(name)).zfill(10))
        self.assets_groups_ids[asset_group_id].sortChildren(50, QtCore.Qt.AscendingOrder)

    def sort_asset_children(self, asset_id):
        names_dic = dict()
        names = []
        creation_item = None
        for child_index in range(self.asset_ids[asset_id].childCount()):
            item = self.asset_ids[asset_id].child(child_index)
            if item.instance_type == 'stage_creation':
                item.setText(50, str(0))
                continue
            names_dic[item.instance_name] = item
            names.append(item.instance_name)
        order_list = [x for x in assets_vars._all_stages_ if x in names]
        names = sorted(names, key=lambda x: order_list.index(x))
        for name in names:
            names_dic[name].setText(50, str(names.index(name)).zfill(10))
        self.asset_ids[asset_id].sortChildren(50, QtCore.Qt.AscendingOrder)

    def update_columns_visibility(self):
        self.tree.setColumnHidden(1, not self.assignment_visibility)
        self.tree.setColumnHidden(2, not self.state_visibility)
        self.tree.setColumnHidden(3, not self.priority_visibility)
        self.tree.setColumnHidden(4, not self.progress_visibility)

    def toggle_assignment_visibility(self):
        self.assignment_visibility = not self.assignment_visibility
        self.update_columns_visibility()

    def toggle_state_visibility(self):
        self.state_visibility = not self.state_visibility
        self.update_columns_visibility()

    def toggle_priority_visibility(self):
        self.priority_visibility = not self.priority_visibility
        self.update_columns_visibility()

    def toggle_progress_visibility(self):
        self.progress_visibility = not self.progress_visibility
        self.update_columns_visibility()

    def toggle_color_visibility(self):
        self.color_visibility = not self.color_visibility
        self.update_color_visibility()

    def update_creation_items_visibility(self):
        for creation_item in self.creation_items:
            creation_item.setHidden(not self.creation_items_visibility)

    def toggle_creation_items_visibility(self):
        self.creation_items_visibility = not self.creation_items_visibility
        self.update_creation_items_visibility()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def refresh_datas(self):
        text = f"{len(self.category_ids.keys())} categories, {len(self.asset_ids.keys())} assets, {len(self.stage_ids.keys())} stages"
        self.data_label.setText(text)

    def add_domain(self, row):
        if row['id'] not in self.domain_ids.keys():
            domain_item = custom_treeWidgetItem(self.tree.invisibleRootItem(), 
                                                    instance_name = row['name'],
                                                    instance_type = 'domain',
                                                    instance_id = row['id'])
            
            domain_item.setIcon(0, self.icons_dic['domain'][f"{row['name']}"])
            domain_item.setText(0, row['name'])
            domain_item.add_progress_indicator()
            self.domain_ids[row['id']] = domain_item
            self.tree.addTopLevelItem(domain_item)
            if row['id'] != 1:
                self.add_creation_item(domain_item, 'new', 'category_creation')

    def add_category(self, row):
        if row['domain_id'] in self.domain_ids.keys():
            if row['id'] not in self.category_ids.keys():
                parent_widget = self.domain_ids[row['domain_id']]
                category_item = custom_treeWidgetItem(parent_widget, 
                                                        instance_name = row['name'],
                                                        instance_type = 'category',
                                                        instance_id = row['id'])
                category_item.setIcon(0, self.icons_dic['folder'])
                category_item.setText(0, row['name'])
                self.category_ids[row['id']] = category_item
                parent_widget.addChild(category_item)
                category_item.add_indicators()
                self.add_creation_item(category_item, 'new', 'asset_creation')
            else:
                self.category_ids[row['id']].state_indicator.clear_states()
                self.category_ids[row['id']].priority_indicator.clear_priorities()

    def add_assets_group(self, row):
        if row['category_id'] in self.category_ids.keys():
            if row['id'] not in self.assets_groups_ids.keys():
                parent_widget = self.category_ids[row['category_id']]
                assets_group_item = custom_treeWidgetItem(parent_widget, 
                                                        instance_name = row['name'],
                                                        instance_type = 'assets_group',
                                                        instance_id = row['id'])
                assets_group_item.setIcon(0, self.icons_dic['assets_groups'])
                assets_group_item.setText(0, row['name'])
                self.assets_groups_ids[row['id']] = assets_group_item
                parent_widget.addChild(assets_group_item)
                assets_group_item.add_indicators()
            else:
                self.assets_groups_ids[row['id']].state_indicator.clear_states()
                self.assets_groups_ids[row['id']].priority_indicator.clear_priorities()

    def add_asset(self, row):
        if row['category_id'] in self.category_ids.keys():
            if row['id'] not in self.asset_ids.keys():
                if row['assets_group_id']:
                    parent_widget = self.assets_groups_ids[row['assets_group_id']]
                else:
                    parent_widget = self.category_ids[row['category_id']]
                asset_item = custom_treeWidgetItem(parent_widget, 
                                                        instance_name = row['name'],
                                                        instance_type = 'asset',
                                                        instance_id = row['id'])
                asset_item.setIcon(0, self.icons_dic['folder'])
                asset_item.setText(0, row['name'])
                self.asset_ids[row['id']] = asset_item
                parent_widget.addChild(asset_item)
                asset_item.add_indicators()
                domain_id = project.get_category_data(row['category_id'], 'domain_id')
                domain_name = project.get_domain_data(domain_id, 'name')
                self.add_creation_item(asset_item, 'new', 'stage_creation')
            else:
                self.asset_ids[row['id']].state_indicator.clear_states()
                self.asset_ids[row['id']].priority_indicator.clear_priorities()

                if row['assets_group_id']:
                    parent_widget = self.assets_groups_ids[row['assets_group_id']]
                else:
                    parent_widget = self.category_ids[row['category_id']]

                if parent_widget != self.asset_ids[row['id']].parent():
                    self.move_asset(self.asset_ids[row['id']], parent_widget)
            #self.asset_ids[row['id']].progress_indicator.set_progress()

    def update_color_visibility(self):
        for domain_id in self.domain_ids.keys():
            domain_item = self.domain_ids[domain_id]
            if self.color_visibility:
                self.tree.set_background_color(domain_item, 0, ressources._domains_colors_[domain_item.instance_name], opacity=110)
                self.tree.set_background_color(domain_item, 1, ressources._domains_colors_[domain_item.instance_name], opacity=110)
                self.tree.set_background_color(domain_item, 2, ressources._domains_colors_[domain_item.instance_name], opacity=110)
                self.tree.set_background_color(domain_item, 3, ressources._domains_colors_[domain_item.instance_name], opacity=110)
                self.tree.set_background_color(domain_item, 4, ressources._domains_colors_[domain_item.instance_name], opacity=110)
            else:
                self.tree.set_background_color(domain_item, 0, None)
                self.tree.set_background_color(domain_item, 1, None)
                self.tree.set_background_color(domain_item, 2, None)
                self.tree.set_background_color(domain_item, 3, None)
                self.tree.set_background_color(domain_item, 4, None)
        for category_id in self.category_ids.keys():
            category_item = self.category_ids[category_id]
            parent_widget = category_item.parent()
            if self.color_visibility:
                self.tree.set_background_color(category_item, 0, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(category_item, 1, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(category_item, 2, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(category_item, 3, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(category_item, 4, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
            else:
                self.tree.set_background_color(category_item, 0, None)
                self.tree.set_background_color(category_item, 1, None)
                self.tree.set_background_color(category_item, 2, None)
                self.tree.set_background_color(category_item, 3, None)
                self.tree.set_background_color(category_item, 4, None)
        for asset_id in self.asset_ids.keys():
            asset_item = self.asset_ids[asset_id]
            parent_widget = asset_item.parent()
            if parent_widget.instance_type == 'assets_group':
                parent_widget = parent_widget.parent()
            domain_widget = parent_widget.parent()
            if self.color_visibility:
                self.tree.set_background_color(asset_item, 0, ressources._domains_colors_[domain_widget.instance_name], opacity=40)
                self.tree.set_background_color(asset_item, 1, ressources._domains_colors_[domain_widget.instance_name], opacity=40)
                self.tree.set_background_color(asset_item, 2, ressources._domains_colors_[domain_widget.instance_name], opacity=40)
                self.tree.set_background_color(asset_item, 3, ressources._domains_colors_[domain_widget.instance_name], opacity=40)
                self.tree.set_background_color(asset_item, 4, ressources._domains_colors_[domain_widget.instance_name], opacity=40)
            else:
                self.tree.set_background_color(asset_item, 0, None)
                self.tree.set_background_color(asset_item, 1, None)
                self.tree.set_background_color(asset_item, 2, None)
                self.tree.set_background_color(asset_item, 3, None)
                self.tree.set_background_color(asset_item, 4, None)
        for assets_group_id in self.assets_groups_ids.keys():
            assets_group_item = self.assets_groups_ids[assets_group_id]
            category_item = assets_group_item.parent()
            parent_widget = category_item.parent()
            if self.color_visibility:
                self.tree.set_background_color(assets_group_item, 0, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(assets_group_item, 1, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(assets_group_item, 2, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(assets_group_item, 3, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
                self.tree.set_background_color(assets_group_item, 4, ressources._domains_colors_[parent_widget.instance_name], opacity=80)
            else:
                self.tree.set_background_color(assets_group_item, 0, None)
                self.tree.set_background_color(assets_group_item, 1, None)
                self.tree.set_background_color(assets_group_item, 2, None)
                self.tree.set_background_color(assets_group_item, 3, None)
                self.tree.set_background_color(assets_group_item, 4, None)

    def move_asset(self, item, new_parent):
        item.parent().takeChild(item.parent().indexOfChild(item))
        new_parent.addChild(item)
        item.add_indicators()
        for i in range(item.childCount()):
            item.child(i).add_indicators()

    def add_stage(self, row):
        if row['asset_id'] in self.asset_ids.keys():
            if row['id'] not in self.stage_ids.keys():
                parent_widget = self.asset_ids[row['asset_id']]
                stage_item = custom_treeWidgetItem( None,
                                                    instance_name = row['name'],
                                                    instance_id = row['id'],
                                                    instance_type = 'stage')
                stage_item.setText(0, row['name'])
                stage_item.setIcon(0, self.icons_dic['stage'][f"{row['name']}"])
                self.stage_ids[row['id']] = stage_item

                parent_widget.addChild(stage_item)
                stage_item.add_indicators()

                self.remove_stage_creation_item(parent_widget)
            self.stage_ids[row['id']].state_indicator.set_state(row['state'])
            self.stage_ids[row['id']].priority_indicator.set_priority(row['priority'])
            self.stage_ids[row['id']].setIcon(1, self.users_icons_dic[row['assignment']])
            self.stage_ids[row['id']].progress_indicator.set_progress(row['progress'])
            if row['state'] in ['error', 'rtk']:
                self.stage_ids[row['id']].parent().state_indicator.add_state(row['state'])
                self.stage_ids[row['id']].parent().parent().state_indicator.add_state(row['state'])
                if self.stage_ids[row['id']].parent().parent().instance_type == 'assets_group':
                    self.stage_ids[row['id']].parent().parent().parent().state_indicator.add_state(row['state'])
            if row['priority'] != assets_vars._priority_normal_:
                self.stage_ids[row['id']].parent().priority_indicator.add_priority(row['priority'])
                self.stage_ids[row['id']].parent().parent().priority_indicator.add_priority(row['priority'])
                if self.stage_ids[row['id']].parent().parent().instance_type == 'assets_group':
                    self.stage_ids[row['id']].parent().parent().parent().priority_indicator.add_priority(row['priority'])


    def remove_stage_creation_item(self, parent_widget):
        child_count = parent_widget.childCount()
        great_parent = parent_widget.parent()
        if great_parent.instance_type == 'assets_group':
            domain_name = great_parent.parent().parent().instance_name
        else:
            domain_name = parent_widget.parent().parent().instance_name
        if child_count == len(assets_vars._stages_list_[domain_name]) + 1:
            for i in range(child_count):
                if parent_widget.child(i).instance_type == 'stage_creation':
                    self.creation_items.remove(parent_widget.child(i))
                    parent_widget.takeChild(i)
                    break

    def remove_creation_item(self, parent_widget):
        child_count = parent_widget.childCount()
        for i in range(child_count):
            if (parent_widget.child(i).instance_type == 'stage_creation') or\
                    (parent_widget.child(i).instance_type == 'asset_creation'):
                self.creation_items.remove(parent_widget.child(i))
                parent_widget.takeChild(i)
                break

    def add_creation_item(self, parent_widget, text, item_type, use_index=False):
        creation_item = custom_treeWidgetItem( None,
                                                instance_name = text,
                                                instance_id = None,
                                                instance_type = item_type,
                                                parent_id=parent_widget.instance_id)
        creation_item.setIcon(0, self.icons_dic['add'])
        creation_item.setText(0, text)
        creation_item.setForeground(0, QtGui.QBrush(QtGui.QColor('gray')))
        self.creation_items.append(creation_item)

        if use_index is None:
            parent_widget.addChild(creation_item)
        else:
            parent_widget.insertChild(use_index, creation_item)

    def reduce_all(self):
        for id in self.domain_ids.keys():
            self.domain_ids[id].setExpanded(0)
        for id in self.category_ids.keys():
            self.category_ids[id].setExpanded(0)
        for id in self.asset_ids.keys():
            self.asset_ids[id].setExpanded(0)
        for id in self.assets_groups_ids.keys():
            self.assets_groups_ids[id].setExpanded(0)

    def toggle_all_visibility(self, visibility):
        for id in self.domain_ids.keys():
            self.domain_ids[id].setHidden(visibility)
        for id in self.category_ids.keys():
            self.category_ids[id].setHidden(visibility)
        for id in self.asset_ids.keys():
            self.asset_ids[id].setHidden(visibility)
        for id in self.stage_ids.keys():
            self.stage_ids[id].setHidden(visibility)
        for id in self.assets_groups_ids.keys():
            self.assets_groups_ids[id].setHidden(visibility)

    def filter_stage(self, string):
        if not string or len(string)<2:
            for id in self.asset_ids.keys():
                for i in range(self.asset_ids[id].childCount()):
                    if self.asset_ids[id].child(i) not in self.creation_items:
                        self.asset_ids[id].child(i).setHidden(0)
        else:
            for id in self.asset_ids.keys():
                for i in range(self.asset_ids[id].childCount()):
                    if string not in self.asset_ids[id].child(i).instance_name:
                        self.asset_ids[id].child(i).setHidden(1)
                    else:
                        self.asset_ids[id].child(i).setHidden(0)

    def focus_on_item(self, item, expand=None):
        self.tree.scrollToItem(item)
        self.tree.setCurrentItem(item)
        if expand is not None:
            item.setExpanded(expand)
        self.item_changed()#item)

    def focus_instance(self, instance_tuple):
        instance_type = instance_tuple[0]
        instance_id = instance_tuple[1]
        if instance_type == 'category':
            if instance_id in self.category_ids.keys():
                self.focus_on_item(self.category_ids[instance_id])
        if instance_type == 'asset':
            if instance_id in self.asset_ids.keys():
                self.focus_on_item(self.asset_ids[instance_id])
        if instance_type == 'stage':
            if instance_id in self.stage_ids.keys():
                self.focus_on_item(self.stage_ids[instance_id])
        if instance_type == 'variant':
            stage_id = project.get_variant_data(instance_id, 'stage_id')
            if stage_id in self.stage_ids.keys():
                self.focus_on_item(self.stage_ids[stage_id])

    def isolate_item(self, item):
        search_text = ''
        if item.instance_type == 'assets_group':
            search_text = f"{item.instance_name}"
        if item.instance_type == 'category':
            search_text = f"{item.instance_name}/"
        elif item.instance_type == 'asset':
            if item.parent().instance_type == 'assets_group':
                category_item = self.category_ids[item.parent().parent().instance_id]
            else:
                category_item = self.category_ids[item.parent().instance_id]
            search_text = f"{category_item.instance_name}/{item.instance_name}"
        elif item.instance_type == 'stage':
            asset_item = self.asset_ids[item.parent().instance_id]
            if asset_item.parent().instance_type == 'assets_group':
                category_item = self.category_ids[asset_item.parent().parent().instance_id]
            else:
                category_item = self.category_ids[asset_item.parent().instance_id]
            search_text = f"{category_item.instance_name}/{asset_item.instance_name}/{item.instance_name}"
        if search_text != '':
            self.search_bar.setText(search_text)

    def apply_search(self):
        search = self.search_bar.text()
        self.search_asset(search)

    def search_asset(self, search):
        if len(search) > 0:
            self.toggle_all_visibility(1)
            self.reduce_all()
            self.search_thread.update_search(search)
        else:
            self.search_thread.running=False
            self.toggle_all_visibility(0)

    def double_click(self, item):
        new_stage_id = None
        new_asset_id = None
        new_category_id = None

        if item.instance_type == 'stage_creation':
            existing_stages = project.get_asset_childs(item.instance_parent_id, 'name')
            menu = gui_utils.QMenu()
            domain_item = item.parent().parent().parent() 
            if domain_item.instance_type != 'domain':
                domain_item=domain_item.parent()
            domain_name = domain_item.instance_name 
            for stage in assets_vars._stages_list_[domain_name]:
                if stage not in existing_stages:
                    action = menu.addAction(QtGui.QIcon(self.icons_dic['stage'][stage]), stage)
                    action.name = stage
            action = menu.addAction(QtGui.QIcon(ressources._guess_icon_), 'Create all stages')
            action.name = 'create_all'
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                parent_id = item.instance_parent_id
                if action.name in assets_vars._stages_list_[domain_name]:
                    new_stage_id = assets.create_stage(action.name, parent_id)
                    if new_stage_id:
                        self.refresh()
                        gui_server.refresh_team_ui()
                else:
                    if action.name == 'create_all':
                        for stage_name in assets_vars._stages_list_[domain_name]:
                            if stage_name not in existing_stages:
                                assets.create_stage(stage_name, parent_id)
                        self.refresh()
                        gui_server.refresh_team_ui()

        elif item.instance_type == 'asset_creation':
            self.instance_creation_widget = instance_creation_widget(self, title='Create asset')
            if self.instance_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                asset_name = self.instance_creation_widget.name_field.text()
                inframe = self.instance_creation_widget.inframe
                outframe = self.instance_creation_widget.outframe
                preroll = self.instance_creation_widget.preroll
                postroll = self.instance_creation_widget.postroll
                parent_id = item.instance_parent_id
                new_asset_id = assets.create_asset(asset_name, parent_id, inframe, outframe, preroll, postroll)
                if new_asset_id is not None:
                    self.refresh()
                    gui_server.refresh_team_ui()
        elif item.instance_type == 'category_creation':
            self.instance_creation_widget = instance_creation_widget(self, request_frames=None, title='Create category')
            if self.instance_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                category_name = self.instance_creation_widget.name_field.text()
                parent_id = item.instance_parent_id
                new_category_id = assets.create_category(category_name, parent_id)
                if new_category_id is not None:
                    self.refresh()
                    gui_server.refresh_team_ui()
        elif item.instance_type == 'stage':
            self.launch_stage_signal.emit(1)

        if new_stage_id:
            if new_stage_id in self.stage_ids.keys():
                self.focus_on_item(self.stage_ids[new_stage_id], expand=1)
        if new_asset_id:
            if new_asset_id in self.asset_ids.keys():
                self.focus_on_item(self.asset_ids[new_asset_id], expand=1)
        if new_category_id:
            if new_category_id in self.category_ids.keys():
                self.focus_on_item(self.category_ids[new_category_id], expand=1)

    def context_menu_requested(self, point):
        menu = gui_utils.QMenu(self)
        
        item = self.tree.itemAt(point)
        reduce_all_action = menu.addAction(QtGui.QIcon(ressources._reduce_icon_), 'Reduce all')
        launch_action = None
        archive_action = None
        isolate_action = None
        open_folder_action = None
        open_sandbox_folder_action = None
        create_assets_group_action = None
        edit_frame_range_action = None
        expand_all_children_action = None
        if item:
            if 'creation' not in item.instance_type:
                open_folder_action = menu.addAction(QtGui.QIcon(ressources._folder_icon_), 'Open folder')
            if 'creation' not in item.instance_type and item.instance_type != 'domain':
                archive_action = menu.addAction(QtGui.QIcon(ressources._archive_icon_), f'Archive {item.instance_type}')
                isolate_action = menu.addAction(QtGui.QIcon(ressources._isolate_icon_), f'Isolate {item.instance_type}')
            if 'creation' not in item.instance_type and item.instance_type == 'asset':
                edit_frame_range_action = menu.addAction(QtGui.QIcon(ressources._tool_frame_range_), f'Edit frame range')
            if 'creation' not in item.instance_type and item.instance_type == 'stage':
                menu.addSeparator()
                open_sandbox_folder_action = menu.addAction(QtGui.QIcon(ressources._sandbox_icon_), 'Open Sandbox folder')
                launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), f'Launch {item.instance_type} (Double click)')
            if 'creation' not in item.instance_type and item.instance_type == 'category':
                create_assets_group_action = menu.addAction(QtGui.QIcon(ressources._assets_group_icon_), f'Create assets group')
            if 'creation' not in item.instance_type and item.instance_type in ['category', 'domain', 'assets_group']:
                expand_all_children_action = menu.addAction(QtGui.QIcon(ressources._expand_icon_), f'Expand all children')


        menu.addSeparator()

        creation_items_visibility_icon = ressources._uncheck_icon_
        if self.creation_items_visibility:
            creation_items_visibility_icon = ressources._check_icon_

        assignment_visibility_icon = ressources._uncheck_icon_
        if self.assignment_visibility:
            assignment_visibility_icon = ressources._check_icon_

        state_visibility_icon = ressources._uncheck_icon_
        if self.state_visibility:
            state_visibility_icon = ressources._check_icon_

        priority_visibility_icon = ressources._uncheck_icon_
        if self.priority_visibility:
            priority_visibility_icon = ressources._check_icon_

        progress_visibility_icon = ressources._uncheck_icon_
        if self.progress_visibility:
            progress_visibility_icon = ressources._check_icon_

        color_visibility_icon = ressources._uncheck_icon_
        if self.color_visibility:
            color_visibility_icon = ressources._check_icon_

        hide_creation_items = menu.addAction(QtGui.QIcon(creation_items_visibility_icon), f'Creation items')
        hide_assignment = menu.addAction(QtGui.QIcon(assignment_visibility_icon), f'Assignment')
        hide_state = menu.addAction(QtGui.QIcon(state_visibility_icon), f'State')
        hide_priority = menu.addAction(QtGui.QIcon(priority_visibility_icon), f'Priority')
        hide_progress = menu.addAction(QtGui.QIcon(progress_visibility_icon), f'Progress')
        hide_colors = menu.addAction(QtGui.QIcon(color_visibility_icon), f'Color')

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == archive_action:
                self.archive_instance(item)
            elif action == open_folder_action:
                self.open_folder(item)
            elif action == reduce_all_action:
                self.reduce_all()
            elif action == launch_action:
                self.launch_stage_signal.emit(1)
            elif action == isolate_action:
                self.isolate_item(item)
            elif action == open_sandbox_folder_action:
                self.open_sandbox_folder(item)
            elif action == hide_creation_items:
                self.toggle_creation_items_visibility()
            elif action == hide_assignment:
                self.toggle_assignment_visibility()
            elif action == hide_state:
                self.toggle_state_visibility()
            elif action == hide_priority:
                self.toggle_priority_visibility()
            elif action == hide_progress:
                self.toggle_progress_visibility()
            elif action == hide_colors:
                self.toggle_color_visibility()
            elif action == edit_frame_range_action:
                self.edit_frame_range(item)
            elif action == create_assets_group_action:
                self.create_assets_group(item)
            elif action == expand_all_children_action:
                self.expand_all_children(item)

    def expand_all_children(self, item):
        item.setExpanded(True)
        for i in range(item.childCount()):
            child = item.child(i)
            self.expand_all_children(child)

    def open_folder(self, item):
        if item.instance_type == 'domain':
            path = assets.get_domain_path(item.instance_id)
        elif item.instance_type == 'category':
            path = assets.get_category_path(item.instance_id)
        elif item.instance_type == 'asset':
            path = assets.get_asset_path(item.instance_id)
        elif item.instance_type== 'stage':
            path = assets.get_stage_path(item.instance_id)
        if path_utils.isdir(path):
            path_utils.startfile(path)
        else:
            logger.error(f"{path} not found")

    def create_assets_group(self, item):
        if item.instance_type != 'category':
            return
        category_id = item.instance_id
        self.assets_group_creation_widget = assets_group_creation_widget(title='Create assets group')
        if self.assets_group_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
            assets_group_name = self.assets_group_creation_widget.name_field.text()
            if project.create_assets_group(assets_group_name, category_id):
                gui_server.refresh_team_ui()
                return 1

    def open_sandbox_folder(self, item):
        variant_id = project.get_stage_data(item.instance_id, 'default_variant_id')
        sandbox_path = path_utils.join(assets.get_variant_path(variant_id), '_SANDBOX')
        path_utils.startfile(sandbox_path)

    def archive_instance(self, item):
        if not repository.is_admin():
            return
        self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
        
        security_sentence = f"{item.instance_name}"
        if item.instance_type == 'category':
            security_sentence = f"{environment.get_project_name()}/{item.instance_name}"

        self.confirm_widget.set_security_sentence(security_sentence)
        if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
            success = None
            if item.instance_type == 'category':
                subtasks_library.archive_category(item.instance_id)
            elif item.instance_type == 'asset':
                subtasks_library.archive_asset(item.instance_id)
            elif item.instance_type== 'stage':
                subtasks_library.archive_stage(item.instance_id)
            elif item.instance_type== 'assets_group':
                project.remove_assets_group(item.instance_id)
                gui_server.refresh_team_ui()

    def edit_frame_range(self, item):
        if item.instance_type == 'asset':
            self.edit_frame_range_widget = edit_frame_range_widget(asset_id=item.instance_id)
            self.edit_frame_range_widget.exec_()

    def remove_category(self, id):
        item = self.category_ids[id]
        self.remove_creation_item(item)
        is_selected = item.isSelected()
        item.parent().removeChild(item)
        del self.category_ids[id]
        if is_selected:
            self.tree.clearSelection()

    def remove_assets_group(self, id):
        item = self.assets_groups_ids[id]
        parent = item.parent()
        for child in range(item.childCount()):
            child_item = item.child(child)
            move_asset(child_item, parent)
        is_selected = item.isSelected()
        item.parent().removeChild(item)
        del self.assets_groups_ids[id]
        if is_selected:
            self.tree.clearSelection()

    def remove_asset(self, id):
        item = self.asset_ids[id]
        self.remove_creation_item(item)
        is_selected = item.isSelected()
        item.parent().removeChild(item)
        del self.asset_ids[id]
        if is_selected:
            self.tree.clearSelection()

    def remove_stage(self, id):
        item = self.stage_ids[id]
        is_selected = item.isSelected()
        parent_item = item.parent()
        parent_item.removeChild(item)

        stage_creation_presence = None
        child_count = parent_item.childCount()
        for i in range(child_count):
            if parent_item.child(i).instance_type == 'stage_creation':
                stage_creation_presence = True
                break
        if not stage_creation_presence:
            self.add_creation_item(parent_item, 'new', 'stage_creation', use_index=0)

        del self.stage_ids[id]
        if is_selected:
            self.tree.clearSelection()

    def add_search_item(self, instance_tuple):
        instance_type = instance_tuple[0]
        instance_id = instance_tuple[1]
        if instance_type == 'stage':
            if instance_id in self.stage_ids.keys():
                self.stage_ids[instance_id].setHidden(0)
                self.stage_ids[instance_id].parent().setHidden(0)
                self.stage_ids[instance_id].parent().setExpanded(1)
                self.stage_ids[instance_id].parent().parent().setHidden(0)
                self.stage_ids[instance_id].parent().parent().setExpanded(1)
                self.stage_ids[instance_id].parent().parent().parent().setExpanded(1)
                self.stage_ids[instance_id].parent().parent().parent().setHidden(0)
                if self.stage_ids[instance_id].parent().parent().instance_type == 'assets_group':
                    self.stage_ids[instance_id].parent().parent().parent().parent().setExpanded(1)
                    self.stage_ids[instance_id].parent().parent().parent().parent().setHidden(0)
        elif instance_type == 'assets_group':
            if instance_id in self.assets_groups_ids.keys():
                self.assets_groups_ids[instance_id].setHidden(0)
                self.assets_groups_ids[instance_id].setExpanded(1)
                self.assets_groups_ids[instance_id].parent().setHidden(0)
                self.assets_groups_ids[instance_id].parent().setExpanded(1)
                self.assets_groups_ids[instance_id].parent().parent().setHidden(0)
                self.assets_groups_ids[instance_id].parent().parent().setExpanded(1)
                self.unhideAllDescendants(self.assets_groups_ids[instance_id])

    def unhideAllDescendants(self, item):
        if item is not None:
            item.setHidden(0)
            item.setExpanded(1)
            for i in range(item.childCount()):
                childItem = item.child(i)
                self.unhideAllDescendants(childItem)

class custom_treeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, instance_name, instance_type, instance_id=None, parent_id=None):
        super(custom_treeWidgetItem, self ).__init__(parent)

        self.setForeground(2, QtGui.QBrush(QtGui.QColor('gray')))

        self.instance_name = instance_name
        self.instance_type = instance_type
        self.instance_id = instance_id
        self.instance_parent_id = parent_id

    def add_indicators(self):
        self.state_indicator = state_indicator()
        self.treeWidget().setItemWidget(self, 2, self.state_indicator)
        self.priority_indicator = priority_indicator()
        self.treeWidget().setItemWidget(self, 3, self.priority_indicator)
        self.add_progress_indicator()

    def add_progress_indicator(self):
        self.progress_indicator = progress_indicator()
        self.treeWidget().setItemWidget(self, 4, self.progress_indicator)

class progress_indicator(QtWidgets.QWidget):
    def __init__(self):
        super(progress_indicator, self).__init__()
        self.setFixedWidth(35)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        self.progress_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.progress_label)

    def set_progress(self, progress):
        self.progress_label.setText(f"{progress}%")

class state_indicator(QtWidgets.QWidget):
    def __init__(self):
        super(state_indicator, self).__init__()
        self.setFixedWidth(18)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        self.states = []
        self.indicators = dict()

    def update_indicators(self):
        for state in self.states:
            if state in self.indicators.keys():
                continue
            indicator_frame = QtWidgets.QFrame()
            indicator_frame.setFixedSize(8,8)
            indicator_frame.setStyleSheet(f'background-color:{ressources._states_colors_[state]};border-radius:4px;')
            self.main_layout.addWidget(indicator_frame)
            self.indicators[state] = indicator_frame
        current_states = list(self.indicators.keys())
        for current_state in current_states:
            if current_state not in self.states:
                self.indicators[current_state].setParent(None)
                self.indicators[current_state].setVisible(False)
                self.indicators[current_state].deleteLater()
                del self.indicators[current_state]

    def set_state(self, state):
        self.states = [state]
        self.update_indicators()

    def add_state(self, state):
        if state in self.states:
            return
        self.states.append(state)
        self.update_indicators()

    def clear_states(self):
        self.states = []
        self.update_indicators()

class priority_indicator(QtWidgets.QWidget):
    def __init__(self):
        super(priority_indicator, self).__init__()
        self.setFixedWidth(32)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        self.priorities = []
        self.indicators = dict()

    def update_indicators(self):
        for priority in self.priorities:
            if priority in self.indicators.keys():
                continue
            indicator_label = QtWidgets.QLabel()
            indicator_label.setPixmap(QtGui.QIcon(ressources._priority_icons_list_[priority]).pixmap(18))
            self.main_layout.addWidget(indicator_label)
            self.indicators[priority] = indicator_label
        current_priorities = list(self.indicators.keys())
        for current_priority in current_priorities:
            if current_priority not in self.priorities:
                self.indicators[current_priority].setParent(None)
                self.indicators[current_priority].setVisible(False)
                self.indicators[current_priority].deleteLater()
                del self.indicators[current_priority]

    def set_priority(self, priority):
        self.priorities = [priority]
        self.update_indicators()

    def add_priority(self, priority):
        if priority in self.priorities:
            return
        self.priorities.append(priority)
        self.update_indicators()

    def clear_priorities(self):
        self.priorities = []
        self.update_indicators()

class instance_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, request_frames=1, title=''):
        super(instance_creation_widget, self).__init__(parent)
        self.request_frames = request_frames
        self.inframe = 100
        self.outframe = 220
        self.preroll = 100
        self.postroll = 0
        self.title = title
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.name_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#instance_creation_frame{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.title_label = QtWidgets.QLabel(self.title)
        self.close_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.frange_frame = QtWidgets.QFrame()
        self.frange_layout = QtWidgets.QHBoxLayout()
        self.frange_layout.setContentsMargins(0,0,0,0)
        self.frange_layout.setSpacing(6)
        self.frange_frame.setLayout(self.frange_layout)

        frange_label = QtWidgets.QLabel("Frame range")
        frange_label.setStyleSheet('color:gray;')
        self.frange_layout.addWidget(frange_label)

        self.preroll_spinBox = QtWidgets.QSpinBox()
        self.preroll_spinBox.setObjectName('gray_label')
        self.preroll_spinBox.setRange(0, 1000000)
        self.preroll_spinBox.setValue(100)
        self.preroll_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.preroll_spinBox)

        self.inframe_spinBox = QtWidgets.QSpinBox()
        self.inframe_spinBox.setRange(-100000, 219)
        self.inframe_spinBox.setValue(100)
        self.inframe_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.inframe_spinBox)

        self.outframe_spinBox = QtWidgets.QSpinBox()
        self.outframe_spinBox.setRange(101, 100000)
        self.outframe_spinBox.setValue(220)
        self.outframe_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.outframe_spinBox)

        self.postroll_spinBox = QtWidgets.QSpinBox()
        self.postroll_spinBox.setObjectName('gray_label')
        self.postroll_spinBox.setRange(0, 1000000)
        self.postroll_spinBox.setValue(0)
        self.postroll_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.postroll_spinBox)

        self.frame_layout.addWidget(self.frange_frame)

        if not self.request_frames:
            self.frange_frame.setVisible(0)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def update_range(self):
        self.inframe = self.inframe_spinBox.value()
        self.outframe = self.outframe_spinBox.value()
        self.preroll = self.preroll_spinBox.value()
        self.postroll = self.postroll_spinBox.value()
        self.inframe_spinBox.setRange(-100000, self.outframe-1)
        self.outframe_spinBox.setRange(self.inframe+1, 100000)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.inframe_spinBox.valueChanged.connect(self.update_range)
        self.outframe_spinBox.valueChanged.connect(self.update_range)
        self.preroll_spinBox.valueChanged.connect(self.update_range)
        self.postroll_spinBox.valueChanged.connect(self.update_range)
        self.close_pushButton.clicked.connect(self.reject)

class assets_group_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, title=''):
        super(assets_group_creation_widget, self).__init__(parent)
        self.title = title
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.name_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#instance_creation_frame{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.title_label = QtWidgets.QLabel(self.title)
        self.close_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)

class edit_frame_range_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, asset_id=None):
        super(edit_frame_range_widget, self).__init__(parent)
        self.asset_id = asset_id
        self.build_ui()
        self.load_old_range()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def load_old_range(self):
        asset_row = project.get_asset_data(self.asset_id)
        self.inframe_spinBox.setValue(asset_row['inframe'])
        self.outframe_spinBox.setValue(asset_row['outframe'])
        self.preroll_spinBox.setValue(asset_row['preroll'])
        self.postroll_spinBox.setValue(asset_row['postroll'])

    def connect_functions(self):
        self.accept_button.clicked.connect(self.edit_frame_range)
        self.close_pushButton.clicked.connect(self.reject)

    def edit_frame_range(self):
        inframe = self.inframe_spinBox.value()
        outframe = self.outframe_spinBox.value()
        preroll = self.preroll_spinBox.value()
        postroll = self.postroll_spinBox.value()
        if outframe <= inframe:
            logger.warning("Can't set an outframe inferior to an inframe")
            return
        if assets.modify_asset_frame_range(self.asset_id, inframe, outframe, preroll, postroll):
            self.accept()

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#instance_creation_frame{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.title_label = QtWidgets.QLabel("Edit frame range")
        self.close_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.frange_frame = QtWidgets.QFrame()
        self.frange_layout = QtWidgets.QHBoxLayout()
        self.frange_layout.setContentsMargins(0,0,0,0)
        self.frange_layout.setSpacing(6)
        self.frange_frame.setLayout(self.frange_layout)

        frange_label = QtWidgets.QLabel("Frame range")
        frange_label.setStyleSheet('color:gray;')
        self.frange_layout.addWidget(frange_label)

        self.preroll_spinBox = QtWidgets.QSpinBox()
        self.preroll_spinBox.setObjectName('gray_label')
        self.preroll_spinBox.setRange(0, 1000000)
        self.preroll_spinBox.setValue(100)
        self.preroll_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.preroll_spinBox)

        self.inframe_spinBox = QtWidgets.QSpinBox()
        self.inframe_spinBox.setRange(-100000, 100000)
        self.inframe_spinBox.setValue(100)
        self.inframe_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.inframe_spinBox)

        self.outframe_spinBox = QtWidgets.QSpinBox()
        self.outframe_spinBox.setRange(-1000000, 100000)
        self.outframe_spinBox.setValue(220)
        self.outframe_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.outframe_spinBox)

        self.postroll_spinBox = QtWidgets.QSpinBox()
        self.postroll_spinBox.setObjectName('gray_label')
        self.postroll_spinBox.setRange(0, 1000000)
        self.postroll_spinBox.setValue(0)
        self.postroll_spinBox.setButtonSymbols(2)
        self.frange_layout.addWidget(self.postroll_spinBox)

        self.frame_layout.addWidget(self.frange_frame)

        self.accept_button = QtWidgets.QPushButton('Modify')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.category = None
        self.asset = None
        self.running = True

    def update_search(self, string):
        self.running = False
        self.string = string
        self.running = True
        self.start()

    def run(self):
        all_stages = project.get_all_stages()
        keywords_sets = self.string.split('+') 
        for keywords_set in keywords_sets:
            keywords = keywords_set.split('&') 
            for stage_row in all_stages:

                stage_row_cp = copy.deepcopy(stage_row)

                del stage_row_cp['id']
                del stage_row_cp['creation_time']
                del stage_row_cp['creation_user']
                del stage_row_cp['work_time']
                del stage_row_cp['progress']
                del stage_row_cp['estimated_time']
                del stage_row_cp['default_variant_id']
                del stage_row_cp['asset_id']
                del stage_row_cp['domain_id']

                values = list(stage_row_cp.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.item_signal.emit(('stage', stage_row['id']))

            all_assets_groups = project.get_all_assets_groups()
            for assets_group_row in all_assets_groups:

                assets_group_row_cp = copy.deepcopy(assets_group_row)

                del assets_group_row_cp['id']
                del assets_group_row_cp['creation_time']
                del assets_group_row_cp['creation_user']
                del assets_group_row_cp['color']
                del assets_group_row_cp['category_id']

                values = list(assets_group_row_cp.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.item_signal.emit(('assets_group', assets_group_row['id']))

class ColoredItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColoredItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        color_data = index.data(QtCore.Qt.UserRole + 1)
        opacity = index.data(QtCore.Qt.UserRole + 2)
        if color_data:
            selected_color = QtGui.QColor(color_data)
            selected_color.setAlpha(int(opacity*2))
            hover_color = QtGui.QColor(color_data)
            hover_color.setAlpha(int(opacity*1.4))
            color = QtGui.QColor(color_data)
            color.setAlpha(opacity)
        else:
            selected_color = QtGui.QColor(255, 255, 255, 30)
            hover_color = QtGui.QColor(255, 255, 255, 10)
            color = QtGui.QColor(255, 255, 255, 0)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        if option.state & QtWidgets.QStyle.State_Selected and option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setBrush(QtGui.QBrush(selected_color))
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setBrush(QtGui.QBrush(hover_color))
        elif option.state & QtWidgets.QStyle.State_Selected:
            painter.setBrush(QtGui.QBrush(selected_color))
        else:
            painter.setBrush(QtGui.QBrush(color))
        view = option.widget
        if view is not None:
            visible_columns = []
            for col in range(view.model().columnCount()):
                if not view.isColumnHidden(col):
                    visible_columns.append(col)
        if len(visible_columns) == 1:
            painter.drawRoundedRect(option.rect, 4, 4)
        elif index.column() == visible_columns[0]:
            rect = QtCore.QRectF(option.rect)
            left_path = QtGui.QPainterPath()
            left_path.addRoundedRect(rect.adjusted(0, 0, -rect.width() + 4*2, 0), 4, 4)
            right_path = QtGui.QPainterPath()
            right_path.addRoundedRect(rect.adjusted(4, 0, 0, 0), 0, 0)
            path = left_path + right_path
            painter.drawPath(path)
        elif index.column() not in [visible_columns[0], visible_columns[-1]]:
            painter.drawRoundedRect(option.rect, 0, 0)
        elif index.column() == visible_columns[-1]:
            rect = QtCore.QRectF(option.rect)
            left_path = QtGui.QPainterPath()
            left_path.addRoundedRect(rect.adjusted(0, 0, -4, 0), 0, 0)
            right_path = QtGui.QPainterPath()
            right_path.addRoundedRect(rect.adjusted(rect.width(), 0, -rect.width() + 4*2, 0), 4, 4)
            path = left_path + right_path
            painter.drawPath(path)
        super(ColoredItemDelegate, self).paint(painter, option, index)

class tree(QtWidgets.QTreeWidget):

    move_asset_to_assets_group = pyqtSignal(tuple)
    remove_asset_from_assets_group = pyqtSignal(int)

    def __init__(self, parent=None):
        super(tree, self).__init__(parent)
        self.setItemDelegate(ColoredItemDelegate(self))
        self._dragroot = self.itemRootIndex()

    def set_background_color(self, item, column, color, opacity=255):
        # Set the background color for the specified column using a custom role
        item.setData(column, QtCore.Qt.UserRole + 1, color)
        item.setData(column, QtCore.Qt.UserRole + 2, opacity)

    def itemRootIndex(self, item=None):
        root = self.invisibleRootItem()
        while item is not None:
            item = item.parent()
            if item is not None:
                root = item
        return QtCore.QPersistentModelIndex(
            self.indexFromItem(root))

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item.instance_type != 'asset':
            return
        self._dragroot = self.itemRootIndex(item)
        super(tree, self).startDrag(supportedActions)

    def dragEnterEvent(self, event):
        self._drag_event(event, True)

    def dragMoveEvent(self, event):
        self._drag_event(event, False)

    def _drag_event(self, event, enter=True):
        items = []
        disable = False
        item = self.itemAt(event.pos())
        asset_item = self.currentItem()
        if item is not None:
            if item.instance_type not in ['assets_group', 'category']:
                disable = True
            elif item.instance_type in ['assets_group']:
                asset_item_category_parent = asset_item.parent()
                if asset_item_category_parent.instance_type != 'category':
                    asset_item_category_parent = asset_item_category_parent.parent()
                item_category_parent = item.parent()
                if asset_item_category_parent != item_category_parent:
                    disable = True
                else:
                    disable = False
            elif item.instance_type in ['category']:
                asset_item_category_parent = asset_item.parent()
                if asset_item_category_parent.instance_type != 'category':
                    asset_item_category_parent = asset_item_category_parent.parent()
                if asset_item_category_parent != item:
                    disable = True
                else:
                    disable = False

        if disable:
            self.setDropIndicatorShown(True)
            parent = item.parent()
            if parent is None:
                parent=self.invisibleRootItem()
            for item in item, parent:
                if item is not None:
                    flags = item.flags()
                    item.setFlags(flags & ~QtCore.Qt.ItemIsDropEnabled)
                    items.append((item, flags))
        else:
            self.setDropIndicatorShown(False)

        if enter:
            QtWidgets.QTreeWidget.dragEnterEvent(self, event)
        else:
            QtWidgets.QTreeWidget.dragMoveEvent(self, event)
        for item, flags in items:
            item.setFlags(flags)

    def dropEvent(self, event):
        if isinstance(event.source(), tree):
            destination_assets_group_item = self.itemAt(event.pos())
            asset_item = self.currentItem()
            if not asset_item:
                return
            if asset_item.instance_type != 'asset':
                return
            if not destination_assets_group_item:
                return
            if destination_assets_group_item.instance_type not in ['assets_group', 'category']:
                return
            if destination_assets_group_item.instance_type == 'category':
                self.remove_asset_from_assets_group.emit(asset_item.instance_id)
                return
            self.move_asset_to_assets_group.emit((asset_item.instance_id, destination_assets_group_item.instance_id))

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = tree_widget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()