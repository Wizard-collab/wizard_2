# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
import time
import logging
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import market_widget
from wizard.gui import inventory_widget
from wizard.gui import users_championship_widget
from wizard.gui import confirm_widget
from wizard.gui import attack_history_widget

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import artefacts
from wizard.core import tools
from wizard.vars import ressources
from wizard.vars import game_vars

logger = logging.getLogger(__name__)

class championship_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(championship_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard championship")

        user_row = repository.get_user_row_by_name(environment.get_user())
        self.old_level = user_row['level']
        self.old_icon = None

        self.modify_participation = True
        self.keeped_artefacts_dic = dict()
        self.coins = None
        self.is_first_comments_count = None
        self.is_first_work_time = None
        self.is_first_xp = None
        self.is_first_deaths = None
        self.first_refresh = 1

        self.refresh_thread = refresh_thread(self)
        self.refresh_thread.start()

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

        self.keeped_artefacts_frame = QtWidgets.QFrame()
        self.keeped_artefacts_frame.setObjectName('dark_round_frame')
        self.keeped_artefacts_layout = QtWidgets.QHBoxLayout()
        self.keeped_artefacts_layout.setContentsMargins(8,8,8,8)
        self.keeped_artefacts_frame.setLayout(self.keeped_artefacts_layout)
        self.user_header_layout.addWidget(self.keeped_artefacts_frame)

        self.items_frame = QtWidgets.QFrame()
        self.items_frame.setObjectName('dark_round_frame')
        self.items_layout = QtWidgets.QHBoxLayout()
        self.items_layout.setContentsMargins(8,8,8,8)
        self.items_frame.setLayout(self.items_layout)
        self.user_header_layout.addWidget(self.items_frame)

        self.deaths_item_label = QtWidgets.QLabel()
        self.deaths_item_label.setPixmap(QtGui.QIcon(ressources._skull_item_icon_).pixmap(25))
        self.items_layout.addWidget(self.deaths_item_label)

        self.comment_item_label = QtWidgets.QLabel()
        self.comment_item_label.setPixmap(QtGui.QIcon(ressources._green_item_icon_).pixmap(25))
        self.items_layout.addWidget(self.comment_item_label)

        self.worker_item_label = QtWidgets.QLabel()
        self.worker_item_label.setPixmap(QtGui.QIcon(ressources._red_item_icon_).pixmap(25))
        self.items_layout.addWidget(self.worker_item_label)

        self.xp_item_label = QtWidgets.QLabel()
        self.xp_item_label.setPixmap(QtGui.QIcon(ressources._yellow_item_icon_).pixmap(25))
        self.items_layout.addWidget(self.xp_item_label)

        self.crown_label = QtWidgets.QLabel()
        self.items_layout.addWidget(self.crown_label)

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

        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setIconSize(QtCore.QSize(22,22))
        self.main_layout.addWidget(self.tabs_widget)

        self.users_championship_widget = users_championship_widget.users_championship_widget()
        self.tabs_widget.addTab(self.users_championship_widget, QtGui.QIcon(ressources._gold_icon_), 'Kingdom')



        self.inventory_widget = inventory_widget.inventory_widget()
        self.tabs_widget.addTab(self.inventory_widget, QtGui.QIcon(ressources._purse_icon_), 'Inventory')
        self.market_widget = market_widget.market_widget()
        self.tabs_widget.addTab(self.market_widget, QtGui.QIcon(ressources._market_icon_), 'Market')

        self.attack_history_widget = attack_history_widget.attack_history_widget()
        self.tabs_widget.addTab(self.attack_history_widget, QtGui.QIcon(ressources._attacks_history_icon_), 'Attacks History')

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(6,6,6,6)
        self.footer_layout.setSpacing(20)
        self.main_layout.addLayout(self.footer_layout)

        self.participation_info_label = QtWidgets.QLabel()
        self.participation_info_label.setObjectName('orange_label')
        self.footer_layout.addWidget(self.participation_info_label)



        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.participation_checkbox = QtWidgets.QCheckBox("Participation")
        self.participation_checkbox.setObjectName('android_checkbox')
        self.footer_layout.addWidget(self.participation_checkbox)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.footer_layout.addWidget(self.refresh_label)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f" refresh : {refresh_time}s")

    def refresh(self):
        start_time = time.perf_counter()
        user_row = repository.get_user_row_by_name(environment.get_user())
        self.refresh_championship_participation(user_row)
        self.refresh_infos(user_row)
        self.market_widget.refresh()
        self.inventory_widget.refresh()
        self.users_championship_widget.refresh()
        self.attack_history_widget.refresh()
        self.refresh_items(user_row)
        self.refresh_keeped_artefacts(user_row)
        self.update_refresh_time(start_time)

    def refresh_championship_participation(self, user_row):
        self.modify_participation = False
        self.participation_checkbox.setChecked(user_row['championship_participation'])
        if not user_row['championship_participation']:
            self.participation_info_label.setText("You don't participate to championship. You can't attack or be attacked.")
        else:
            self.participation_info_label.setText("")
        self.modify_participation = True

    def refresh_infos(self, user_row):
        user_coins = user_row['coins']
        self.coins_amount.setText(str(user_coins))
        self.coins = user_coins
        self.level_amount.setText(str(user_row['level']))
        self.life_amount.setText(f"{user_row['life']}%")
        if user_row['level'] != self.old_level:
            if user_row['level'] > self.old_level:
                gui_server.custom_popup(f"You are now level {user_row['level']}", 'Congratulation', ressources._level_icon_)
            else:
                gui_server.custom_popup(f"You are now level {user_row['level']}", 'You just lost a level, take care of your comments', ressources._level_icon_)
            self.old_level = user_row['level']

    def refresh_keeped_artefacts(self, user_row):
        keeped_artefacts_dic = json.loads(user_row['keeped_artefacts'])
        for artefact in list(set(keeped_artefacts_dic.values())):
            if artefact not in self.keeped_artefacts_dic.keys():
                keeped_artefact_label = QtWidgets.QLabel()
                keeped_artefact_label.setPixmap(QtGui.QIcon(game_vars.artefacts_dic[artefact]['icon']).pixmap(25))
                self.keeped_artefacts_layout.addWidget(keeped_artefact_label)
                self.keeped_artefacts_dic[artefact] = keeped_artefact_label
        existing_artefacts_list = list(self.keeped_artefacts_dic.keys())
        for artefact in existing_artefacts_list:
            if artefact not in list(set(keeped_artefacts_dic.values())):
                self.remove_keeped_artefact(artefact)
        if len(self.keeped_artefacts_dic.keys()) == 0:
            self.keeped_artefacts_frame.setVisible(0)
        else:
            self.keeped_artefacts_frame.setVisible(1)

    def modify_championship_participation(self):
        if not self.modify_participation:
            return
        user_row = repository.get_user_row_by_name(environment.get_user())
        self.refresh_championship_participation(user_row)
        current_participation = user_row['championship_participation']
        if current_participation:
            self.confirm_widget = confirm_widget.confirm_widget(f"If you turn off your participation to the game, you won't be able to participate again within {tools.convert_seconds_to_string_time_with_days(game_vars._default_ban_time_)}.\nDo you want to continue ?", parent=self)
            if self.confirm_widget.exec_() != QtWidgets.QDialog.Accepted:
                return
        repository.modify_user_championship_participation(environment.get_user(), 1-current_participation)
        gui_server.refresh_ui()

    def remove_keeped_artefact(self, artefact):
        if artefact not in self.keeped_artefacts_dic.keys():
            return
        self.keeped_artefacts_dic[artefact].setParent(None)
        self.keeped_artefacts_dic[artefact].deleteLater()
        del self.keeped_artefacts_dic[artefact]
        gui_server.custom_popup(f"Inventory", f"{game_vars.artefacts_dic[artefact]['name']} is expired !", game_vars.artefacts_dic[artefact]['icon'])

    def connect_functions(self):
        self.tabs_widget.currentChanged.connect(self.tab_changed)
        self.refresh_thread.refresh_signal.connect(self.refresh)
        self.refresh_thread.refresh_signal.connect(gui_server.refresh_ui)
        self.participation_checkbox.stateChanged.connect(self.modify_championship_participation)

    def tab_changed(self):
        self.market_widget.refresh()
        self.inventory_widget.refresh()
        self.users_championship_widget.refresh()

    def refresh_items(self, user_row):
        user_rows = repository.get_users_list()
        self.items_check(user_row, user_rows)

    def items_check(self, user_row, user_rows):

        self.items_frame.setVisible(0)

        xp_dic = dict()
        comments_dic = dict()
        work_time_dic = dict()
        deaths_dic = dict()

        for row in user_rows:
            if row['total_xp'] not in xp_dic.keys():
                xp_dic[row['total_xp']] = row['id']
            if row['comments_count'] not in comments_dic.keys():
                comments_dic[row['comments_count']] = row['id']
            if row['work_time'] not in work_time_dic.keys():
                work_time_dic[row['work_time']] = row['id']
            if row['deaths'] not in deaths_dic.keys():
                deaths_dic[row['deaths']] = row['id']

        if user_row['id'] != xp_dic[sorted(list(xp_dic.keys()))[-1]]:
            self.xp_item_label.setVisible(0)
            self.is_first_xp = 0
        else:
            self.items_frame.setVisible(1)
            self.xp_item_label.setVisible(1)
            if not self.is_first_xp and not (self.first_refresh):
                gui_server.custom_popup("You have earned so much experience !", 'Congratulation', ressources._yellow_item_icon_)
            self.is_first_xp = 1

        if user_row['id'] != deaths_dic[sorted(list(deaths_dic.keys()))[-1]]:
            self.deaths_item_label.setVisible(0)
            self.is_first_deaths = 0
        else:
            self.items_frame.setVisible(1)
            self.deaths_item_label.setVisible(1)
            if not self.is_first_deaths and not (self.first_refresh):
                gui_server.custom_popup("You are the one who die the most !", 'Try to comment your work more often', ressources._skull_item_icon_)
            self.is_first_deaths = 1

        if user_row['id'] != comments_dic[sorted(list(comments_dic.keys()))[-1]]:
            self.comment_item_label.setVisible(0)
            self.is_first_comments_count = 0
        else:
            self.items_frame.setVisible(1)
            self.comment_item_label.setVisible(1)
            if not self.is_first_comments_count and not (self.first_refresh):
                gui_server.custom_popup("You are really good at commenting !", 'Congratulation', ressources._green_item_icon_)
            self.is_first_comments_count = 1

        if user_row['id'] != work_time_dic[sorted(list(work_time_dic.keys()))[-1]]:
            self.worker_item_label.setVisible(0)
            self.is_first_work_time = 0
        else:
            self.items_frame.setVisible(1)
            self.worker_item_label.setVisible(1)
            if not self.is_first_work_time and not (self.first_refresh):
                gui_server.custom_popup("You worked so much time !", 'Congratulation', ressources._red_item_icon_)
            self.is_first_work_time = 1

        icon = None
        message = None
        if user_row['id'] == user_rows[0]['id']:
            icon = ressources._gold_icon_
            message = "You just won the golden crown !"
        if len(user_rows)>=2:
            if (user_row['id'] ==  user_rows[1]['id']):
                icon = ressources._silver_icon_
                message = "You just won the silver crown !"
        if len(user_rows)>=3:
            if (user_row['id'] == user_rows[2]['id']):
                icon = ressources._bronze_icon_
                message = "You just won the bronze crown !"
        if icon is not None:
            self.items_frame.setVisible(1)
            self.crown_label.setVisible(1)
            self.crown_label.setPixmap(QtGui.QIcon(icon).pixmap(22))
            if icon != self.old_icon and not (self.first_refresh):
                gui_server.custom_popup(message, 'Congratulation', icon)
            self.old_icon = icon
        else:
            self.crown_label.setVisible(0)

class refresh_thread(QtCore.QThread):

    refresh_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(refresh_thread, self).__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            refresh_ui = 0
            if artefacts.check_keeped_artefacts_expiration():
                refresh_ui = 1
            if refresh_ui:
                self.refresh_signal.emit(1)
            for a in range(5):
                if not self.running:
                    break
                time.sleep(1)

    def stop(self):
        self.running = False