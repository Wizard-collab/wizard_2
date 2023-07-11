# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
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

class market_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(market_widget, self).__init__(parent)
        self.artefacts = dict()
        self.build_ui()
        self.fill_ui()

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

    def fill_ui(self):
        for artefact, artefact_dic in game_vars.artefacts_dic.items():
            artefact_list_item = QtWidgets.QListWidgetItem('')
            artefact_widget = artefact_item(artefact, artefact_dic)
            self.artefacts_view.addItem(artefact_list_item)
            artefact_list_item.setSizeHint(artefact_widget.size())
            self.artefacts_view.setItemWidget(artefact_list_item, artefact_widget)
            self.artefacts[artefact] = artefact_widget

    def refresh(self):
        if not self.isVisible():
            return
        user_row = repository.get_user_row_by_name(environment.get_user())
        for artefact, widget in self.artefacts.items():
            widget.update_level(user_row['level'])
            widget.update_buy_button(user_row['coins'])

class artefact_item(QtWidgets.QFrame):
    def __init__(self, artefact, artefact_dic, parent=None):
        super(artefact_item, self).__init__(parent)
        self.artefact = artefact
        self.artefact_dic = artefact_dic
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setFixedSize(250, 120)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.artefact_icon = QtWidgets.QLabel()
        self.artefact_icon.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.artefact_icon.setPixmap(QtGui.QIcon(self.artefact_dic['icon']).pixmap(70))
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

        self.level_label = QtWidgets.QLabel(f"Level {self.artefact_dic['level']}")
        self.level_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.button_layout.addWidget(self.level_label)

        self.button_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.buy_button = QtWidgets.QPushButton(f"{self.artefact_dic['price']} | Buy")
        self.buy_button.setStyleSheet('padding:2px')
        self.buy_button.setIcon(QtGui.QIcon(ressources._coin_icon_))
        self.buy_button.setIconSize(QtCore.QSize(18,18))
        self.button_layout.addWidget(self.buy_button)

    def connect_functions(self):
        self.buy_button.clicked.connect(self.buy_artefact)

    def update_level(self, level):
        if level >= self.artefact_dic['level']:
            self.setEnabled(True)
            self.setStyleSheet('')
        else:
            self.setEnabled(False)
            self.setStyleSheet('color:gray')

    def update_buy_button(self, coins):
        if coins >= self.artefact_dic['price']:
            self.buy_button.setEnabled(True)
            self.buy_button.setStyleSheet('padding:2px')
        else:
            self.buy_button.setEnabled(False)
            self.buy_button.setStyleSheet('color:gray;padding:2px')

    def buy_artefact(self):
        artefacts.buy_artefact(self.artefact)
        gui_server.refresh_ui()
        gui_server.custom_popup(f"Market", f"You just bought {self.artefact_dic['name']} for {self.artefact_dic['price']} coins", ressources._market_icon_)
