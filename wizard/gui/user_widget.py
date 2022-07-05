# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard modules
from wizard.core import environment
from wizard.core import repository
from wizard.core import image
from wizard.vars import ressources

class user_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(user_widget, self).__init__(parent)
        user_row = repository.get_user_row_by_name(environment.get_user())
        self.old_level = user_row['level']
        self.old_icon = None
        self.is_first_comments_count = None
        self.is_first_work_time = None
        self.is_first_xp = None
        self.is_first_deaths = None
        self.first_refresh = 1
        self.build_ui()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.items_widget = QtWidgets.QWidget()
        self.items_widget.setObjectName('transparent_widget')
        self.items_layout = QtWidgets.QHBoxLayout()
        self.items_layout.setContentsMargins(0,0,0,0)
        self.items_layout.setSpacing(6)
        self.items_widget.setLayout(self.items_layout)
        self.main_layout.addWidget(self.items_widget)

        self.deaths_item_label = QtWidgets.QLabel()
        self.deaths_item_label.setPixmap(QtGui.QIcon(ressources._skull_item_icon_).pixmap(22))
        self.items_layout.addWidget(self.deaths_item_label)

        self.comment_item_label = QtWidgets.QLabel()
        self.comment_item_label.setPixmap(QtGui.QIcon(ressources._green_item_icon_).pixmap(22))
        self.items_layout.addWidget(self.comment_item_label)

        self.worker_item_label = QtWidgets.QLabel()
        self.worker_item_label.setPixmap(QtGui.QIcon(ressources._red_item_icon_).pixmap(22))
        self.items_layout.addWidget(self.worker_item_label)

        self.xp_item_label = QtWidgets.QLabel()
        self.xp_item_label.setPixmap(QtGui.QIcon(ressources._yellow_item_icon_).pixmap(22))
        self.items_layout.addWidget(self.xp_item_label)

        self.crown_label = QtWidgets.QLabel()
        self.items_layout.addWidget(self.crown_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.infos_widget.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(0)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.level_label = QtWidgets.QLabel('23')
        gui_utils.application_tooltip(self.level_label, "User level")
        self.infos_layout.addWidget(self.level_label)
        self.info_level_label = QtWidgets.QLabel('L.')
        gui_utils.application_tooltip(self.info_level_label, "User level")
        self.info_level_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.info_level_label)

        self.progress_bars_widget = QtWidgets.QWidget()
        self.progress_bars_widget.setObjectName('transparent_widget')
        self.progress_bars_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.progress_bars_layout = QtWidgets.QVBoxLayout()
        self.progress_bars_layout.setContentsMargins(0,0,0,0)
        self.progress_bars_layout.setSpacing(1)
        self.progress_bars_widget.setLayout(self.progress_bars_layout)
        self.main_layout.addWidget(self.progress_bars_widget)

        self.xp_progress_bar = gui_utils.QProgressBar()
        gui_utils.application_tooltip(self.xp_progress_bar, "User experience")
        self.xp_progress_bar.setObjectName('user_xp_progressBar')
        self.xp_progress_bar.setInvertedAppearance(1)
        self.xp_progress_bar.setFixedHeight(6)
        self.xp_progress_bar.setFixedWidth(100)
        self.xp_progress_bar.setTextVisible(0)
        self.progress_bars_layout.addWidget(self.xp_progress_bar)
        
        self.life_progress_bar = gui_utils.QProgressBar()
        gui_utils.application_tooltip(self.life_progress_bar, "User life")
        self.life_progress_bar.setObjectName('user_life_progressBar')
        self.life_progress_bar.setInvertedAppearance(1)
        self.life_progress_bar.setFixedHeight(6)
        self.life_progress_bar.setFixedWidth(100)
        self.life_progress_bar.setTextVisible(0)
        self.progress_bars_layout.addWidget(self.life_progress_bar)

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
        self.xp_progress_bar.setValue(user_row['xp'])
        self.life_progress_bar.setValue(user_row['life'])
        self.level_label.setText(str(user_row['level']))
        self.admin_badge_label.setVisible(user_row['administrator'])
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 28)
        self.profile_picture.setPixmap(pm)
        self.crown_check(user_row, user_rows)
        self.items_check(user_row, user_rows)

        if user_row['level'] != self.old_level:
            if user_row['level'] > self.old_level:
                gui_server.custom_popup(f"You are now level {user_row['level']}", 'Congratulation', ressources._congrats_icon_)
            else:
                gui_server.custom_popup(f"You are now level {user_row['level']}", 'You just lost a level, take care of your comments')

            self.old_level = user_row['level']
        self.first_refresh = 0

    def items_check(self, user_row, user_rows):
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
            self.xp_item_label.setVisible(1)
            if not self.is_first_xp and not (self.first_refresh):
                gui_server.custom_popup("You have earned so much experience !", 'Congratulation', ressources._yellow_item_icon_)
            self.is_first_xp = 1

        if user_row['id'] != deaths_dic[sorted(list(deaths_dic.keys()))[-1]]:
            self.deaths_item_label.setVisible(0)
            self.is_first_deaths = 0
        else:
            self.deaths_item_label.setVisible(1)
            if not self.is_first_deaths and not (self.first_refresh):
                gui_server.custom_popup("You are the one who die the most !", 'Try to comment your work more often', ressources._skull_item_icon_)
            self.is_first_deaths = 1

        if user_row['id'] != comments_dic[sorted(list(comments_dic.keys()))[-1]]:
            self.comment_item_label.setVisible(0)
            self.is_first_comments_count = 0
        else:
            self.comment_item_label.setVisible(1)
            if not self.is_first_comments_count and not (self.first_refresh):
                gui_server.custom_popup("You are really good at commenting !", 'Congratulation', ressources._green_item_icon_)
            self.is_first_comments_count = 1

        if user_row['id'] != work_time_dic[sorted(list(work_time_dic.keys()))[-1]]:
            self.worker_item_label.setVisible(0)
            self.is_first_work_time = 0
        else:
            self.worker_item_label.setVisible(1)
            if not self.is_first_work_time and not (self.first_refresh):
                gui_server.custom_popup("You worked so much time !", 'Congratulation', ressources._red_item_icon_)
            self.is_first_work_time = 1

    def crown_check(self, user_row, user_rows):
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
            self.crown_label.setVisible(1)
            self.crown_label.setPixmap(QtGui.QIcon(icon).pixmap(22))
            if icon != self.old_icon and not (self.first_refresh):
                gui_server.custom_popup(message, 'Congratulation', icon)
            self.old_icon = icon
        else:
            self.crown_label.setVisible(0)
    