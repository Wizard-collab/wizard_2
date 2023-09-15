# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import json

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import image
from wizard.vars import ressources
from wizard.vars import game_vars

class user_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(user_widget, self).__init__(parent)
        self.items = dict()
        self.keeped_artefacts = []
        self.build_ui()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.items_widget = QtWidgets.QFrame()
        self.items_widget.setObjectName('dark_round_frame')
        self.items_layout = QtWidgets.QHBoxLayout()
        self.items_layout.setContentsMargins(8,2,8,2)
        self.items_layout.setSpacing(6)
        self.items_widget.setLayout(self.items_layout)
        self.main_layout.addWidget(self.items_widget)

        self.level_widget = QtWidgets.QFrame()
        self.level_widget.setObjectName('dark_round_frame')
        self.level_layout = QtWidgets.QHBoxLayout()
        self.level_layout.setContentsMargins(8,2,8,2)
        self.level_layout.setSpacing(3)
        self.level_widget.setLayout(self.level_layout)
        self.main_layout.addWidget(self.level_widget)

        self.level_icon = QtWidgets.QLabel()
        self.level_icon.setFixedSize(22,22)
        self.level_icon.setPixmap(QtGui.QIcon(ressources._level_icon_).pixmap(22))
        self.level_layout.addWidget(self.level_icon)
        self.level_label = QtWidgets.QLabel('0')
        gui_utils.application_tooltip(self.level_label, "User level")
        self.level_layout.addWidget(self.level_label)

        self.coins_widget = QtWidgets.QFrame()
        self.coins_widget.setObjectName('dark_round_frame')
        self.coins_layout = QtWidgets.QHBoxLayout()
        self.coins_layout.setContentsMargins(8,2,8,2)
        self.coins_layout.setSpacing(3)
        self.coins_widget.setLayout(self.coins_layout)
        self.main_layout.addWidget(self.coins_widget)

        self.coins_icon = QtWidgets.QLabel()
        self.coins_icon.setFixedSize(22,22)
        self.coins_icon.setPixmap(QtGui.QIcon(ressources._coin_icon_).pixmap(22))
        self.coins_layout.addWidget(self.coins_icon)
        self.coins_label = QtWidgets.QLabel('0')
        gui_utils.application_tooltip(self.coins_label, "User coins")
        self.coins_layout.addWidget(self.coins_label)

        self.life_widget = QtWidgets.QFrame()
        self.life_widget.setObjectName('dark_round_frame')
        self.life_layout = QtWidgets.QHBoxLayout()
        self.life_layout.setContentsMargins(8,2,8,2)
        self.life_layout.setSpacing(3)
        self.life_widget.setLayout(self.life_layout)
        self.main_layout.addWidget(self.life_widget)

        self.life_icon = QtWidgets.QLabel()
        self.life_icon.setFixedSize(22,22)
        self.life_icon.setPixmap(QtGui.QIcon(ressources._heart_icon_).pixmap(22))
        self.life_layout.addWidget(self.life_icon)
        self.life_label = QtWidgets.QLabel('100%')
        gui_utils.application_tooltip(self.life_label, "User life")
        self.life_layout.addWidget(self.life_label)

        self.admin_badge_label = QtWidgets.QLabel()
        gui_utils.application_tooltip(self.admin_badge_label, "Admin badge")
        self.admin_badge_label.setPixmap(QtGui.QIcon(ressources._admin_badge_).pixmap(22))
        self.main_layout.addWidget(self.admin_badge_label)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(28,28)
        self.main_layout.addWidget(self.profile_picture)

    def refresh(self):
        user_rows = repository.get_users_list()
        user_row = repository.get_user_row_by_name(environment.get_user())
        #self.xp_progress_bar.setValue(user_row['xp'])
        self.life_label.setText(f"{user_row['life']}%")
        self.coins_label.setText(str(user_row['coins']))
        self.level_label.setText(str(user_row['level']))
        self.admin_badge_label.setVisible(user_row['administrator'])
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 28, custom_radius=14)
        self.profile_picture.setPixmap(pm)
        self.refresh_crown(user_row, user_rows)
        self.refresh_keeped_artefacts(user_row)

    def refresh_keeped_artefacts(self, user_row):
        keeped_artefacts_dic = json.loads(user_row['keeped_artefacts'])
        for artefact in list(set(keeped_artefacts_dic.values())):
            if artefact in self.keeped_artefacts:
                continue
            self.add_item(artefact, game_vars.artefacts_dic[artefact]['icon'])
            self.keeped_artefacts.append(artefact)
        for artefact in self.keeped_artefacts:
            if artefact not in list(set(keeped_artefacts_dic.values())):
                self.remove_item(artefact)
                self.keeped_artefacts.remove(artefact)

    def refresh_crown(self, user_row, user_rows):
        if user_row['id'] == user_rows[0]['id']:
            self.add_item('crown', ressources._gold_icon_)
            return
        if len(user_rows)>=2:
            if (user_row['id'] ==  user_rows[1]['id']):
                self.add_item('crown', ressources._silver_icon_)
                return
        if len(user_rows)>=3:
            if (user_row['id'] == user_rows[2]['id']):
                self.add_item('crown', ressources._bronze_icon_)
                return
        self.remove_item('crown')

    def add_item(self, name, icon):
        if name not in self.items.keys():
            label = QtWidgets.QLabel()
            self.items[name] = label
            self.items_layout.addWidget(self.items[name])
        self.items[name].setPixmap(QtGui.QIcon(icon).pixmap(22))

    def remove_item(self, name):
        if name not in self.items.keys():
            return
        self.items[name].setParent(None)
        self.items[name].deleteLater()
        del self.items[name]
    