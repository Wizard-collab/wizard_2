# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
import time
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import market_widget
from wizard.gui import inventory_widget
from wizard.gui import users_championship_widget

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import artefacts
from wizard.vars import ressources
from wizard.vars import game_vars

class championship_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(championship_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard championship")

        self.keeped_artefacts_dic = dict()
        self.coins = None

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
        self.resize(1000, 600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.user_header = QtWidgets.QWidget()
        self.user_header_layout = QtWidgets.QHBoxLayout()
        self.user_header.setLayout(self.user_header_layout)
        self.main_layout.addWidget(self.user_header)

        self.title = QtWidgets.QLabel("Championship")
        self.title.setObjectName('title_label')
        self.user_header_layout.addWidget(self.title)

        self.user_header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.keeped_artefacts_layout = QtWidgets.QHBoxLayout()
        self.keeped_artefacts_layout.setContentsMargins(0,0,0,0)
        self.keeped_artefacts_layout.setSpacing(2)
        self.user_header_layout.addLayout(self.keeped_artefacts_layout)

        self.life_frame = QtWidgets.QFrame()
        self.life_frame.setObjectName('dark_round_frame')
        self.life_layout = QtWidgets.QHBoxLayout()
        self.life_layout.setContentsMargins(8,8,8,8)
        self.life_frame.setLayout(self.life_layout)
        self.user_header_layout.addWidget(self.life_frame)
        self.life_icon = QtWidgets.QLabel()
        self.life_icon.setFixedSize(25,25)
        self.life_icon.setPixmap(QtGui.QIcon(ressources._heart_icon_).pixmap(25))
        self.life_layout.addWidget(self.life_icon)
        self.life_amount = QtWidgets.QLabel()
        self.life_amount.setObjectName('title_label_2')
        self.life_layout.addWidget(self.life_amount)

        self.level_frame = QtWidgets.QFrame()
        self.level_frame.setObjectName('dark_round_frame')
        self.level_layout = QtWidgets.QHBoxLayout()
        self.level_layout.setContentsMargins(8,8,8,8)
        self.level_frame.setLayout(self.level_layout)
        self.user_header_layout.addWidget(self.level_frame)
        self.level_icon = QtWidgets.QLabel()
        self.level_icon.setFixedSize(25,25)
        self.level_icon.setPixmap(QtGui.QIcon(ressources._level_icon_).pixmap(25))
        self.level_layout.addWidget(self.level_icon)
        self.level_amount = QtWidgets.QLabel()
        self.level_amount.setObjectName('title_label_2')
        self.level_layout.addWidget(self.level_amount)

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

        self.users_championship_widget = users_championship_widget.users_championship_widget()
        self.tabs_widget.addTab(self.users_championship_widget, QtGui.QIcon(ressources._gold_icon_), 'Kingdom')

        self.inventory_widget = inventory_widget.inventory_widget()
        self.tabs_widget.addTab(self.inventory_widget, QtGui.QIcon(ressources._purse_icon_), 'Inventory')
        self.market_widget = market_widget.market_widget()
        self.tabs_widget.addTab(self.market_widget, QtGui.QIcon(ressources._market_icon_), 'Market')

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(6,6,6,6)
        self.main_layout.addLayout(self.footer_layout)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.footer_layout.addWidget(self.refresh_label)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def refresh(self):
        start_time = time.perf_counter()
        self.refresh_infos()
        self.market_widget.refresh()
        self.inventory_widget.refresh()
        self.users_championship_widget.refresh()
        self.refresh_keeped_artefacts()
        self.update_refresh_time(start_time)

    def refresh_infos(self):
        user_row = repository.get_user_row_by_name(environment.get_user())
        user_coins = user_row['coins']
        if self.coins is not None:
            if user_coins > self.coins:
                gui_server.custom_popup(f"Inventory", f"You just earned {user_coins-self.coins} coins", ressources._coin_icon_)
            if user_coins < self.coins:
                gui_server.custom_popup(f"Inventory", f"You just lost {self.coins-user_coins} coins", ressources._coin_icon_)
        self.coins_amount.setText(str(user_coins))
        self.coins = user_coins
        self.level_amount.setText(str(user_row['level']))
        self.life_amount.setText(f"{user_row['life']}%")

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
        self.users_championship_widget.refresh()
