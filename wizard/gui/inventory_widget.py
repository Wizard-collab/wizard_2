# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard modules
from wizard.core import repository
from wizard.core import environment
from wizard.core import artefacts
from wizard.vars import ressources
from wizard.vars import game_vars

class inventory_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(inventory_widget, self).__init__(parent)
        self.artefacts = dict()
        self.build_ui()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)
        self.artefacts_view = QtWidgets.QListView()
        self.artefacts_view = QtWidgets.QListWidget()
        self.artefacts_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.artefacts_view.setObjectName('market_icon_view')
        self.artefacts_view.setSpacing(4)
        self.artefacts_view.setMovement(QtWidgets.QListView.Static)
        self.artefacts_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.artefacts_view.setViewMode(QtWidgets.QListView.IconMode)
        self.artefacts_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.artefacts_view_scrollBar = self.artefacts_view.verticalScrollBar()
        self.main_layout.addWidget(self.artefacts_view)

    def refresh(self):
        if not self.isVisible():
            return
        user_row = repository.get_user_row_by_name(environment.get_user())
        artefacts_list = json.loads(user_row['artefacts'])
        artefacts_set = list(set(artefacts_list))
        for artefact in artefacts_set:
            if artefact not in self.artefacts.keys():
                artefact_list_item = QtWidgets.QListWidgetItem('')
                artefact_widget = artefact_item(artefact)
                self.artefacts_view.addItem(artefact_list_item)
                artefact_list_item.setSizeHint(artefact_widget.size())
                self.artefacts_view.setItemWidget(artefact_list_item, artefact_widget)
                self.artefacts[artefact] = dict()
                self.artefacts[artefact]['item'] = artefact_list_item
                self.artefacts[artefact]['widget'] = artefact_widget
            self.artefacts[artefact]['widget'].update_number(artefacts_list.count(artefact))
        existing_artefact_list = list(self.artefacts)
        for artefact in existing_artefact_list:
            if artefact not in artefacts_list:
                self.remove_item(artefact)

    def remove_item(self, artefact):
        if artefact not in self.artefacts.keys():
            return
        item = self.artefacts[artefact]['item']
        widget = self.artefacts[artefact]['widget']
        widget.setParent(None)
        widget.deleteLater()
        self.artefacts_view.takeItem(self.artefacts_view.row(item))
        del self.artefacts[artefact]

class artefact_item(QtWidgets.QFrame):
    def __init__(self, artefact, parent=None):
        super(artefact_item, self).__init__(parent)
        self.artefact = artefact
        self.artefact_dic = game_vars.artefacts_dic[artefact]
        self.number = 0
        self.build_ui()
        self.connect_functions()

    def update_number(self, number):
        self.number = number
        self.fill_ui()

    def fill_ui(self):
        self.number_label.setText(f"x{self.number}")

    def build_ui(self):
        icon = QtGui.QIcon(self.artefact_dic['icon'])
        self.setFixedSize(250, 110)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.artefact_icon = QtWidgets.QLabel()
        self.artefact_icon.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.artefact_icon.setPixmap(icon.pixmap(70))
        self.main_layout.addWidget(self.artefact_icon)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(2)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.artefact_name = QtWidgets.QLabel(self.artefact_dic['name'])
        self.artefact_name.setObjectName('title_label_2')
        self.content_layout.addWidget(self.artefact_name)

        self.info_label = QtWidgets.QLabel(self.artefact_dic['description'])
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('gray_label')
        self.content_layout.addWidget(self.info_label)

        self.type_label = QtWidgets.QLabel(self.artefact_dic['type'].capitalize())
        self.type_label.setStyleSheet('color:#f2c96b')
        self.type_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_layout.addWidget(self.type_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0,0,0,0)
        self.button_layout.setSpacing(0)
        self.content_layout.addLayout(self.button_layout)

        self.number_label = QtWidgets.QLabel()
        self.number_label.setObjectName('title_label_2')
        self.number_label.setStyleSheet('color:#f2c96b')
        self.button_layout.addWidget(self.number_label)

        self.button_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.use_button = QtWidgets.QPushButton(f"Use")
        self.use_button.setStyleSheet('padding:2px')
        self.use_button.setIcon(icon)
        self.use_button.setIconSize(QtCore.QSize(18,18))
        self.button_layout.addWidget(self.use_button)

    def connect_functions(self):
        self.use_button.clicked.connect(self.use_artefact)

    def use_artefact(self):
        artefacts.use_artefact(self.artefact, 'l.brunel')
        gui_server.refresh_ui()
        gui_server.custom_popup(f"Inventory", f"You just used {self.artefact_dic['name']} on {'l.brunel'}", ressources._purse_icon_)
