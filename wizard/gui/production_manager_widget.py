# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import site
from wizard.core import project
from wizard.core import image
from wizard.vars import ressources
from wizard.vars import assets_vars

class production_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(production_manager_widget, self).__init__(parent)
        self.build_ui()
        self.users_ids = dict()
        self.asset_ids = dict()
        self.stage_ids = dict()
        self.variant_ids = dict()

    def build_ui(self):

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('production_manager_list_widget')
        self.list_view.setColumnCount(6)
        self.list_view.setIconSize(QtCore.QSize(30,30))
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.list_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.list_view.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.list_view.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.list_view.header().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.list_view.header().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.list_view.setHeaderLabels(['Asset', 'Modeling', 'Rigging', 'Grooming', 'Texturing', 'Shading'])
        self.main_layout.addWidget(self.list_view)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('tree_datas_label')
        self.main_layout.addWidget(self.refresh_label)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def refresh(self):
        start_time = time.time()

        asset_rows = project.get_all_assets() 
        stage_rows = project.get_all_stages()
        variant_rows = project.get_all_variants()

        for asset_row in asset_rows:
            if asset_row['id'] not in self.asset_ids.keys():
                self.asset_ids[asset_row['id']] = dict()
                self.asset_ids[asset_row['id']]['row'] = asset_row
                item = custom_asset_listWidgetItem(self.asset_ids[asset_row['id']]['row'], self.list_view.invisibleRootItem())
                self.asset_ids[asset_row['id']]['item'] = item

        for stage_row in stage_rows:
            if stage_row['id'] not in self.stage_ids.keys():
                self.stage_ids[stage_row['id']] = dict()
                self.stage_ids[stage_row['id']]['row'] = stage_row
                self.asset_ids[self.stage_ids[stage_row['id']]['row']['asset_id']]['item'].add_stage(self.stage_ids[stage_row['id']]['row'])
                self.stage_ids[stage_row['id']]['asset_item'] = self.asset_ids[self.stage_ids[stage_row['id']]['row']['asset_id']]['item']

        for variant_row in variant_rows:
            if variant_row['id'] not in self.variant_ids.keys():
                self.variant_ids[variant_row['id']] = dict()
                self.variant_ids[variant_row['id']]['row'] = variant_row
                self.stage_ids[self.variant_ids[variant_row['id']]['row']['stage_id']]['asset_item'].add_variant(self.variant_ids[variant_row['id']]['row'])

        self.update_refresh_time(start_time)

class custom_asset_listWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, asset_row, parent=None):
        super(custom_asset_listWidgetItem, self).__init__(parent)
        self.setText(0, asset_row['name'])
        self.stage_ids = dict()
        self.variant_ids = dict()

    def add_stage(self, stage_row):
        self.stage_ids[stage_row['id']] = dict()
        self.stage_ids[stage_row['id']]['row'] = stage_row
        widget = stage_widget(stage_row, self.treeWidget())
        self.stage_ids[stage_row['id']]['widget'] = widget
        index = assets_vars._assets_stages_list_.index(stage_row['name'])+1
        self.stage_ids[stage_row['id']]['index'] = index
        self.treeWidget().setItemWidget(self, index, widget)

    def add_variant(self, variant_row):
        widget = variant_widget(variant_row, self.treeWidget())
        widget.update_size.connect(self.update_size)
        stage_widget = self.stage_ids[variant_row['stage_id']]['widget']
        stage_widget.add_variant(widget)
        self.variant_ids[variant_row['id']] = dict()
        self.variant_ids[variant_row['id']]['row'] = variant_row
        self.variant_ids[variant_row['id']]['widget'] = widget

    def update_size(self):
        for stage_id in self.stage_ids:
            widget = self.stage_ids[stage_id]['widget']
            index = self.stage_ids[stage_id]['index']
            self.setSizeHint(index, widget.sizeHint())

class stage_widget(QtWidgets.QWidget):

    def __init__(self, stage_row, parent=None):
        super(stage_widget, self).__init__(parent)
        self.stage_row = stage_row
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(1,2,1,2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def add_variant(self, variant_widget):
        self.main_layout.insertWidget(self.main_layout.count() - 1, variant_widget)

class variant_widget(QtWidgets.QFrame):

    update_size = pyqtSignal(int)
    
    def __init__(self, variant_row, parent=None):
        super(variant_widget, self).__init__(parent)
        self.variant_row = variant_row
        self.build_ui()

    def showEvent(self, event):
        self.update_size.emit(1)
        self.fill_ui()

    def build_ui(self):
        self.setObjectName('production_manager_variant_frame')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QtWidgets.QLabel(self.variant_row['name']))

        self.datas_widget = QtWidgets.QFrame()
        #self.datas_widget.setObjectName('dark_widget')
        self.datas_widget.setStyleSheet('border-radius:19px;')
        print(self.datas_widget.size())
        self.datas_layout = QtWidgets.QHBoxLayout()
        self.datas_layout.setContentsMargins(5,5,5,5)
        self.datas_layout.setSpacing(8)
        self.datas_widget.setLayout(self.datas_layout)
        self.main_layout.addWidget(self.datas_widget)

        self.user_image_label = QtWidgets.QLabel()
        self.user_image_label.setFixedSize(QtCore.QSize(30,30))
        self.datas_layout.addWidget(self.user_image_label)

        self.state_label = QtWidgets.QLabel()
        self.state_label.setObjectName('bold_label')
        self.datas_layout.addWidget(self.state_label)

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

        self.percent_label = QtWidgets.QLabel()
        self.progress_bar_layout.addWidget(self.percent_label)

    def fill_ui(self):
        self.state_label.setText(self.variant_row['state'])
        user_image =  site.get_user_row_by_name(self.variant_row['assignment'], 'profile_picture')
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 30)
        self.user_image_label.setPixmap(pm)

        if self.variant_row['estimated_time'] is not None:
            percent = (float(self.variant_row['work_time'])/float(self.variant_row['estimated_time']))*100
            self.percent_label.setText(f"{str(int(percent))}%")
            if percent > 100:
                percent = 100
                if self.variant_row['state'] != 'done':
                    self.time_progress_bar.setStyleSheet('::chunk{background-color:#ff5d5d;}')
            else:
                self.time_progress_bar.setStyleSheet('::chunk{background-color:#ffad4d;}')
            if self.variant_row['state'] == 'done':
                self.time_progress_bar.setStyleSheet('::chunk{background-color:#95d859;}')
            self.time_progress_bar.setValue(percent)
        else:
            self.time_progress_bar.setValue(0)
            self.percent_label.setText("0%")
