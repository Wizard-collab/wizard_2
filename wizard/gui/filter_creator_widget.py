# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard core modules
from wizard.core import user
from wizard.core import project
from wizard.core import repository
from wizard.vars import ressources
from wizard.vars import assets_vars

logger = logging.getLogger(__name__)

class filter_creator_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(filter_creator_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def showEvent(self, event):
        self.fill_ui()

    def connect_functions(self):
        self.domain_add_button.clicked.connect(self.add_domain)
        self.category_add_button.clicked.connect(self.add_category)
        self.asset_add_button.clicked.connect(self.add_asset)
        self.stage_add_button.clicked.connect(self.add_stage)
        self.data_add_button.clicked.connect(self.add_data)
        self.trash_button.clicked.connect(self.delete_selection)
        self.save_button.clicked.connect(self.apply)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.filter_name_lineEdit = QtWidgets.QLineEdit()
        self.filter_name_lineEdit.setPlaceholderText('Filter name')
        self.main_layout.addWidget(self.filter_name_lineEdit)

        self.filters_list = QtWidgets.QListWidget()
        self.filters_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.main_layout.addWidget(self.filters_list)

        self.trash_layout = QtWidgets.QHBoxLayout()
        self.trash_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.trash_layout)
        self.trash_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.trash_button = QtWidgets.QPushButton()
        self.trash_button.setFixedSize(30, 30)
        self.trash_button.setIcon(QtGui.QIcon(ressources._archive_icon_))
        self.trash_layout.addWidget(self.trash_button)

        self.combobox_layout = QtWidgets.QGridLayout()
        self.combobox_layout.setSpacing(4)
        self.combobox_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.combobox_layout)

        self.domain_label = QtWidgets.QLabel('Domains')
        self.domain_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.domain_comboBox = gui_utils.QComboBox()
        self.domain_add_button = QtWidgets.QPushButton()
        self.domain_add_button.setFixedSize(30,30)
        self.domain_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.combobox_layout.addWidget(self.domain_label, 0, 0)
        self.combobox_layout.addWidget(self.domain_comboBox, 0, 1)
        self.combobox_layout.addWidget(self.domain_add_button, 0, 2)

        self.category_label = QtWidgets.QLabel('Categories')
        self.category_comboBox = gui_utils.QComboBox()
        self.category_add_button = QtWidgets.QPushButton()
        self.category_add_button.setFixedSize(30,30)
        self.category_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.combobox_layout.addWidget(self.category_label, 1, 0)
        self.combobox_layout.addWidget(self.category_comboBox, 1, 1)
        self.combobox_layout.addWidget(self.category_add_button, 1, 2)

        self.asset_label = QtWidgets.QLabel('Assets')
        self.asset_comboBox = gui_utils.QComboBox()
        self.asset_add_button = QtWidgets.QPushButton()
        self.asset_add_button.setFixedSize(30,30)
        self.asset_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.combobox_layout.addWidget(self.asset_label, 2, 0)
        self.combobox_layout.addWidget(self.asset_comboBox, 2, 1)
        self.combobox_layout.addWidget(self.asset_add_button, 2, 2)

        self.stage_label = QtWidgets.QLabel('Stages')
        self.stage_comboBox = gui_utils.QComboBox()
        self.stage_add_button = QtWidgets.QPushButton()
        self.stage_add_button.setFixedSize(30,30)
        self.stage_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.combobox_layout.addWidget(self.stage_label, 3, 0)
        self.combobox_layout.addWidget(self.stage_comboBox, 3, 1)
        self.combobox_layout.addWidget(self.stage_add_button, 3, 2)

        self.data_label = QtWidgets.QLabel('Data')
        self.data_comboBox = gui_utils.QComboBox()
        self.data_add_button = QtWidgets.QPushButton()
        self.data_add_button.setFixedSize(30,30)
        self.data_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.combobox_layout.addWidget(self.data_label, 4, 0)
        self.combobox_layout.addWidget(self.data_comboBox, 4, 1)
        self.combobox_layout.addWidget(self.data_add_button, 4, 2)

        self.save_button = QtWidgets.QPushButton('Save')
        self.save_button.setObjectName('blue_button')
        self.main_layout.addWidget(self.save_button)

    def delete_selection(self):
        selected_items = self.filters_list.selectedItems()
        for item in selected_items:
            self.filters_list.takeItem(self.filters_list.row(item))
            del item

    def add_item(self, text):
        for item_index in range(self.filters_list.count()):
            item_text = self.filters_list.item(item_index).text()
            if text == item_text:
                return
        self.filters_list.addItem(text)

    def add_domain(self, domain):
        self.add_item(f"domain:{self.domain_comboBox.currentText()}")

    def add_category(self, category):
        self.add_item(f"category:{self.category_comboBox.currentText()}")

    def add_asset(self, asset):
        self.add_item(f"asset:{self.asset_comboBox.currentText()}")

    def add_stage(self, stage):
        self.add_item(f"stage:{self.stage_comboBox.currentText()}")

    def add_data(self, data):
        self.add_item(f"data:{self.data_comboBox.currentText()}")

    def fill_ui(self):
        for domain_row in project.get_domains():
            if domain_row['name'] == 'library':
                continue
            self.domain_comboBox.addItem(domain_row['name'])
            for category_row in project.get_domain_childs(domain_row['id']):
                self.category_comboBox.addItem(category_row['name'])
                for asset_row in project.get_category_childs(category_row['id']):
                    self.asset_comboBox.addItem(asset_row['name'])
        for stage in assets_vars._assets_stages_list_ + assets_vars._sequences_stages_list_:
            self.stage_comboBox.addItem(stage)
        for state in assets_vars._asset_states_list_:
            self.data_comboBox.addItem(state)
        for priority in assets_vars._priority_list_:
            self.data_comboBox.addItem(priority)
        for user_id in project.get_users_ids_list():
            user_name = repository.get_user_data(user_id, 'user_name')
            self.data_comboBox.addItem(user_name)

    def apply(self):
        filter_dic = dict()
        for item_index in range(self.filters_list.count()):
            item_text = self.filters_list.item(item_index).text()
            key = item_text.split(':')[0]
            data = item_text.split(':')[-1]
            if key not in filter_dic.keys():
                filter_dic[key] = []
            if data not in filter_dic[key]:
                filter_dic[key].append(data)
        filter_name = self.filter_name_lineEdit.text()