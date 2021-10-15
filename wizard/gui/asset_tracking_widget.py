# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources
from wizard.vars import assets_vars

# Wizard gui modules
from wizard.gui import gui_server

class asset_tracking_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(asset_tracking_widget, self).__init__(parent)

        self.variant_id = None
        self.variant_row = None
        self.users_ids = dict()

        self.apply_assignment_modification = None
        self.apply_state_modification = None

        self.build_ui()
        self.refresh_users_dic()
        self.connect_functions()

    def refresh_users_dic(self):
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            if user_id not in self.users_ids.keys():
                self.users_ids[user_id] = site.get_user_data(user_id, 'user_name')
                self.assignment_comboBox.addItem(self.users_ids[user_id])

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.setup_widget = QtWidgets.QFrame()
        self.setup_widget.setObjectName('asset_tracking_event_frame')
        self.setup_layout = QtWidgets.QHBoxLayout()
        self.setup_layout.setSpacing(6)
        self.setup_widget.setLayout(self.setup_layout)
        self.main_layout.addWidget(self.setup_widget)

        self.assignment_comboBox = QtWidgets.QComboBox()
        self.assignment_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.setup_layout.addWidget(self.assignment_comboBox)

        self.state_comboBox = QtWidgets.QComboBox()
        self.state_comboBox.setIconSize(QtCore.QSize(14,14))
        self.state_comboBox.setFixedWidth(100)
        self.state_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.setup_layout.addWidget(self.state_comboBox)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_todo_), assets_vars._asset_state_todo_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_wip_), assets_vars._asset_state_wip_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_done_), assets_vars._asset_state_done_ )
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_error_), assets_vars._asset_state_error_)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(300,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def change_variant(self, variant_id):
        self.variant_id = variant_id
        self.refresh()

    def refresh(self):
        if self.variant_id is not None:
            self.variant_row = project.get_variant_data(self.variant_id)
        else:
            self.variant_row = None
        self.refresh_state()
        self.refresh_users_dic()
        self.refresh_user()

    def refresh_user(self):
        self.apply_assignment_modification = None
        if self.variant_row is not None:
            if self.variant_row['assignment'] is not None:
                self.assignment_comboBox.setCurrentText(self.variant_row['assignment'])
            else:
                self.assignment_comboBox.setCurrentText('Assign user')
        else:
            self.assignment_comboBox.setCurrentText('Assign user')
        self.apply_assignment_modification = 1

    def refresh_state(self):
        self.apply_state_modification = None
        if self.variant_row is not None:
            self.state_comboBox.setCurrentText(self.variant_row['state'])
        else:
            self.state_comboBox.setCurrentText('todo')
        self.apply_state_modification = 1

    def modify_state(self, state):
        if self.variant_id is not None:
            if self.apply_state_modification:
                assets.modify_variant_state(self.variant_id, state)
                gui_server.refresh_ui()

    def modify_assignment(self, user_name):
        if self.variant_id is not None:
            if self.apply_assignment_modification:
                assets.modify_variant_assignment(self.variant_id, user_name)
                gui_server.refresh_ui()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.modify_state)
        self.assignment_comboBox.currentTextChanged.connect(self.modify_assignment)
