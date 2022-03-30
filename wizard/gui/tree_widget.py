# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import time
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.core import user
from wizard.core import path_utils
from wizard.core import subtasks_library
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

        self.creation_items_visibility = user.user().get_creation_items_visibility()

        self.domain_ids=dict()
        self.category_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()
        self.creation_items=[]

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.icons_dic = dict()
        self.icons_dic['add'] = QtGui.QIcon(ressources._add_icon_small_)
        self.icons_dic['folder'] = QtGui.QIcon(ressources._folder_icon_small_)
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

        self.setFixedWidth(300)
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
        self.search_bar.setPlaceholderText('characters:Lola*grooming')
        self.search_layout.addWidget(self.search_bar)

        self.main_layout.addWidget(self.search_frame)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setObjectName('transparent_widget')
        self.tree.setAnimated(1)
        self.tree.setIconSize(QtCore.QSize(16, 16))
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.main_layout.addWidget(self.tree)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('tree_datas_label')
        self.main_layout.addWidget(self.refresh_label)

        self.data_label = QtWidgets.QLabel()
        self.data_label.setObjectName('tree_datas_label')
        self.main_layout.addWidget(self.data_label)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread = search_thread()
        self.search_thread.item_signal.connect(self.add_search_item)
        self.tree.itemDoubleClicked.connect(self.double_click)
        self.tree.currentItemChanged.connect(self.item_changed)
        self.tree.customContextMenuRequested.connect(self.context_menu_requested)

    def item_changed(self, item):
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
        user.user().set_creation_items_visibility(self.creation_items_visibility)

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

    def refresh(self, hard=None):
        start_time = time.time()
        if hard:
            self.init_tree()

        self.project_category_ids = []
        self.project_asset_ids = []
        self.project_stage_ids = []

        self.all_export_versions_stage_ids = project.get_all_export_versions('stage_id')
        self.all_variants_rows = project.get_all_variants()

        for domain_row in project.get_domains():
            self.add_domain(domain_row)
        for category_row in project.get_all_categories():
            self.add_category(category_row)
            self.project_category_ids.append(category_row['id'])
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
        for variant_row in self.all_variants_rows:
            self.stage_ids[variant_row['stage_id']].set_state_indicator(variant_row)

        self.apply_search()
        self.refresh_datas()
        if hard:
            self.get_context()
        self.update_creation_items_visibility()
        self.update_refresh_time(start_time)

    def update_creation_items_visibility(self):
        for creation_item in self.creation_items:
            creation_item.setHidden(not self.creation_items_visibility)

    def toggle_creation_items_visibility(self):
        self.creation_items_visibility = not self.creation_items_visibility
        self.update_creation_items_visibility()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
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
                self.add_creation_item(category_item, 'new', 'asset_creation')

    def add_asset(self, row):
        if row['category_id'] in self.category_ids.keys():
            if row['id'] not in self.asset_ids.keys():
                parent_widget = self.category_ids[row['category_id']]
                asset_item = custom_treeWidgetItem(parent_widget, 
                                                        instance_name = row['name'],
                                                        instance_type = 'asset',
                                                        instance_id = row['id'])
                asset_item.setIcon(0, self.icons_dic['folder'])
                asset_item.setText(0, row['name'])
                self.asset_ids[row['id']] = asset_item
                parent_widget.addChild(asset_item)
                domain_id = project.get_category_data(row['category_id'], 'domain_id')
                domain_name = project.get_domain_data(domain_id, 'name')
                self.add_creation_item(asset_item, 'new', 'stage_creation')

    def add_stage(self, row):
        if row['asset_id'] in self.asset_ids.keys():
            if row['id'] not in self.stage_ids.keys():
                parent_widget = self.asset_ids[row['asset_id']]
                stage_item = stage_treeWidgetItem( None,
                                                    instance_name = row['name'],
                                                    instance_id = row['id'],
                                                    instance_type = 'stage')
                stage_item.setText(0, row['name'])
                stage_item.setIcon(0, self.icons_dic['stage'][f"{row['name']}"])
                self.stage_ids[row['id']] = stage_item

                parent_widget.addChild(stage_item)

                stage_item.set_item_widget()
                self.remove_stage_creation_item(parent_widget)

    def remove_stage_creation_item(self, parent_widget):
        child_count = parent_widget.childCount()
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

    def toggle_all_visibility(self, visibility):
        for id in self.domain_ids.keys():
            self.domain_ids[id].setHidden(visibility)
        for id in self.category_ids.keys():
            self.category_ids[id].setHidden(visibility)
        for id in self.asset_ids.keys():
            self.asset_ids[id].setHidden(visibility)

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
        self.item_changed(item)

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
        if item.instance_type == 'category':
            search_text = f"{item.instance_name}:"
        elif item.instance_type == 'asset':
            category_item = self.category_ids[item.parent().instance_id]
            search_text = f"{category_item.instance_name}:{item.instance_name}"
        elif item.instance_type == 'stage':
            asset_item = self.asset_ids[item.parent().instance_id]
            category_item = self.category_ids[asset_item.parent().instance_id]
            search_text = f"{category_item.instance_name}:{asset_item.instance_name}*{item.instance_name}"
        if search_text != '':
            self.search_bar.setText(search_text)

    def apply_search(self):
        search = self.search_bar.text()
        self.search_asset(search)

    def search_asset(self, search):
        stage_filter = None
        if '*' in search:
            stage_filter = search.split('*')[-1]
            search = search.split('*')[0]
        self.filter_stage(stage_filter)
        if len(search) > 2:
            self.toggle_all_visibility(1)
            if ':' in search:
                category_string=search.split(':')[0]
                asset_string=search.split(':')[-1]
            else:
                category_string = None
                asset_string = search
            self.search_thread.update_search(category_string, asset_string)
        else:
            self.search_thread.running=False
            self.toggle_all_visibility(0)


    def double_click(self, item):
        new_stage_id = None
        new_asset_id = None
        new_category_id = None

        if item.instance_type == 'stage_creation':
            menu = gui_utils.QMenu()
            domain_name = item.parent().parent().parent().instance_name 
            for stage in assets_vars._stages_list_[domain_name]:
                action = menu.addAction(QtGui.QIcon(self.icons_dic['stage'][stage]), stage)
                action.name = stage
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                stage_name = action.name
                parent_id = item.instance_parent_id
                new_stage_id = assets.create_stage(stage_name, parent_id)
                if new_stage_id:
                    self.refresh()
                    gui_server.refresh_ui()

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
                    gui_server.refresh_ui()
        elif item.instance_type == 'category_creation':
            self.instance_creation_widget = instance_creation_widget(self, request_frames=None, title='Create category')
            if self.instance_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                category_name = self.instance_creation_widget.name_field.text()
                parent_id = item.instance_parent_id
                new_category_id = assets.create_category(category_name, parent_id)
                if new_category_id is not None:
                    self.refresh()
                    gui_server.refresh_ui()
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
        if item:
            if 'creation' not in item.instance_type:
                open_folder_action = menu.addAction(QtGui.QIcon(ressources._folder_icon_), 'Open folder')
            if 'creation' not in item.instance_type and item.instance_type != 'domain':
                archive_action = menu.addAction(QtGui.QIcon(ressources._archive_icon_), f'Archive {item.instance_type}')
                isolate_action = menu.addAction(QtGui.QIcon(ressources._isolate_icon_), f'Isolate {item.instance_type}')
            if 'creation' not in item.instance_type and item.instance_type == 'stage':
                menu.addSeparator()
                open_sandbox_folder_action = menu.addAction(QtGui.QIcon(ressources._sandbox_icon_), 'Open Sandbox folder')
                launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), f'Launch {item.instance_type} (Double click)')
        menu.addSeparator()

        creation_items_visibility_icon = ressources._uncheck_icon_
        if not self.creation_items_visibility:
            creation_items_visibility_icon = ressources._check_icon_

        hide_creation_items = menu.addAction(QtGui.QIcon(creation_items_visibility_icon), f'Hide creation items')

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

    def open_sandbox_folder(self, item):
        variant_id = project.get_stage_data(item.instance_id, 'default_variant_id')
        sandbox_path = path_utils.join(assets.get_variant_path(variant_id), '_SANDBOX')
        path_utils.startfile(sandbox_path)

    def archive_instance(self, item):
        self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)

        if item.instance_type == 'category':
            security_sentence = f"{environment.get_project_name()}/{item.instance_name}"
        elif item.instance_type == 'asset':
            category_name = project.get_category_data(project.get_asset_data(item.instance_id, 'category_id'), 'name')
            security_sentence = f"{environment.get_project_name()}/{category_name}/{item.instance_name}"
        elif item.instance_type== 'stage':
            asset_row = project.get_asset_data(project.get_stage_data(item.instance_id, 'asset_id'))
            category_name = project.get_category_data(asset_row['category_id'], 'name')
            security_sentence = f"{environment.get_project_name()}/{category_name}/{asset_row['name']}/{item.instance_name}"

        self.confirm_widget.set_security_sentence(security_sentence)
        if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
            success = None
            if item.instance_type == 'category':
                subtasks_library.archive_category(item.instance_id)
            elif item.instance_type == 'asset':
                subtasks_library.archive_asset(item.instance_id)
            elif item.instance_type== 'stage':
                subtasks_library.archive_stage(item.instance_id)

    def remove_category(self, id):
        item = self.category_ids[id]
        self.remove_creation_item(item)
        is_selected = item.isSelected()
        item.parent().removeChild(item)
        del self.category_ids[id]
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

    def add_search_item(self, ids_list):
        if ids_list[0] in self.domain_ids.keys():
            self.domain_ids[ids_list[0]].setHidden(0)
        if ids_list[1] in self.category_ids.keys():
            self.category_ids[ids_list[1]].setHidden(0)
        if ids_list[2] in self.asset_ids.keys():
            self.asset_ids[ids_list[2]].setHidden(0)

class custom_treeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, instance_name, instance_type, instance_id=None, parent_id=None):
        super(custom_treeWidgetItem, self ).__init__(parent)
        self.instance_name = instance_name
        self.instance_type = instance_type
        self.instance_id = instance_id
        self.instance_parent_id = parent_id

class stage_treeWidgetItem(custom_treeWidgetItem):
    def __init__(self, parent, instance_name, instance_type, instance_id=None, parent_id=None):
        super(stage_treeWidgetItem, self).__init__(parent, 
                                                instance_name, 
                                                instance_type,
                                                instance_id,
                                                parent_id)

        self.state_ids = dict()
        
        self.widget = QtWidgets.QWidget()
        self.widget.setStyleSheet('background:transparent;')
        self.widget_layout = QtWidgets.QHBoxLayout()
        self.widget_layout.setContentsMargins(2,2,2,2)
        self.widget.setLayout(self.widget_layout)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Fixed)
        self.widget_layout.addSpacerItem(self.spaceItem)
        self.spaceItem = QtWidgets.QSpacerItem(150,10,QtWidgets.QSizePolicy.Expanding)
        self.widget_layout.addSpacerItem(self.spaceItem)

    def set_item_widget(self):
        self.treeWidget().setItemWidget(self, 0, self.widget)

    def set_state_indicator(self, variant_row):
        if variant_row['id'] not in self.state_ids.keys():
            state_indicator = indicator(assets_vars._state_colors_dic_[variant_row['state']])
            self.widget_layout.addWidget(state_indicator)
            self.state_ids[variant_row['id']] = state_indicator
        else:
            self.state_ids[variant_row['id']].update(assets_vars._state_colors_dic_[variant_row['state']])

class indicator(QtWidgets.QFrame):
    def __init__(self, color):
        super(indicator, self).__init__()
        self.setFixedSize(8,8)
        self.setStyleSheet(f'background-color:{color};border-radius:4px;')

    def update(self, color):
        self.setStyleSheet(f'background-color:{color};border-radius:4px;')

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
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
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

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.category = None
        self.asset = None
        self.running = True

    def update_search(self, category=None, asset=None):
        self.running = False
        self.category = category
        self.asset = asset
        self.running = True
        self.start()

    def run(self):
        process=1
        parent_id = None
        if self.category and len(self.category)>2:
            category_id=project.get_category_data_by_name(self.category, 'id')
            if category_id:
                parent_id = category_id
        if self.category and not parent_id:
            process=None
        if process:
            assets_list = project.search_asset(self.asset, parent_id)
            for asset_row in assets_list:
                if not self.running:
                    break
                domain_id = project.get_category_data(project.get_asset_data(asset_row['id'], 'category_id'), 'domain_id')
                self.item_signal.emit([domain_id, asset_row['category_id'], asset_row['id']])

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = tree_widget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()