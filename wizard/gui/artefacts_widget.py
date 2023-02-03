# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import market_widget
from wizard.gui import inventory_widget

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import artefacts
from wizard.vars import ressources
from wizard.vars import game_vars

class artefacts_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(artefacts_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard artefacts")

        self.keeped_artefacts_dic = dict()

        self.build_ui()
        self.connect_functions()

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

    def build_ui(self):
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.user_header = QtWidgets.QWidget()
        self.user_header_layout = QtWidgets.QHBoxLayout()
        self.user_header.setLayout(self.user_header_layout)
        self.main_layout.addWidget(self.user_header)

        self.title = QtWidgets.QLabel("Artefacts")
        self.title.setObjectName('title_label')
        self.user_header_layout.addWidget(self.title)

        self.user_header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.keeped_artefacts_layout = QtWidgets.QHBoxLayout()
        self.keeped_artefacts_layout.setContentsMargins(0,0,0,0)
        self.keeped_artefacts_layout.setSpacing(2)
        self.user_header_layout.addLayout(self.keeped_artefacts_layout)

        self.purse_frame = QtWidgets.QFrame()
        self.purse_frame.setObjectName('dark_round_frame')
        self.purse_layout = QtWidgets.QHBoxLayout()
        self.purse_layout.setContentsMargins(8,8,8,8)
        self.purse_frame.setLayout(self.purse_layout)
        self.user_header_layout.addWidget(self.purse_frame)
        self.purse_icon = QtWidgets.QLabel()
        self.purse_icon.setFixedSize(25,25)
        self.purse_icon.setPixmap(QtGui.QIcon(ressources._coin_icon_).pixmap(25))
        self.purse_layout.addWidget(self.purse_icon)
        self.coins_amount = QtWidgets.QLabel()
        self.coins_amount.setObjectName('title_label_2')
        self.purse_layout.addWidget(self.coins_amount)

        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setIconSize(QtCore.QSize(22,22))
        self.main_layout.addWidget(self.tabs_widget)

        self.inventory_widget = inventory_widget.inventory_widget()
        self.tabs_widget.addTab(self.inventory_widget, QtGui.QIcon(ressources._purse_icon_), 'Inventory')
        self.market_widget = market_widget.market_widget()
        self.tabs_widget.addTab(self.market_widget, QtGui.QIcon(ressources._market_icon_), 'Market')
        
    def refresh(self):
        user_row = repository.get_user_row_by_name(environment.get_user())
        self.coins_amount.setText(str(user_row['coins']))
        self.market_widget.refresh()
        self.inventory_widget.refresh()
        self.refresh_keeped_artefacts()

    def refresh_keeped_artefacts(self):
        artefacts.check_artefacts_expiration()
        user_row = repository.get_user_row_by_name(environment.get_user())
        keeped_artefacts_dic = json.loads(user_row['keeped_artefacts'])
        for artefact in list(set(keeped_artefacts_dic.values())):
            if artefact not in self.keeped_artefacts_dic.keys():
                keeped_artefact_label = QtWidgets.QLabel()
                keeped_artefact_label.setPixmap(QtGui.QIcon(game_vars.artefacts_dic[artefact]['icon']).pixmap(30))
                self.keeped_artefacts_layout.addWidget(keeped_artefact_label)
                self.keeped_artefacts_dic[artefact] = keeped_artefact_label
        existing_artefacts_list = list(self.keeped_artefacts_dic.keys())
        for artefact in existing_artefacts_list:
            if artefact not in list(set(keeped_artefacts_dic.values())):
                self.remove_keeped_artefact(artefact)

    def remove_keeped_artefact(self, artefact):
        if artefact not in self.keeped_artefacts_dic.keys():
            return
        self.keeped_artefacts_dic[artefact].setParent(None)
        self.keeped_artefacts_dic[artefact].deleteLater()
        del self.keeped_artefacts_dic[artefact]
        gui_server.custom_popup(f"Inventory", f"{game_vars.artefacts_dic[artefact]['name']} is expired !", game_vars.artefacts_dic[artefact]['icon'])

    def connect_functions(self):
        self.tabs_widget.currentChanged.connect(self.tab_changed)

    def tab_changed(self):
        self.market_widget.refresh()
        self.inventory_widget.refresh()
