# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import time

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import repository
from wizard.core import image
from wizard.core import tools
from wizard.vars import ressources

class users_championship_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(users_championship_widget, self).__init__(parent)
        self.user_ids = dict()
        self.init_icons_dic()
        self.build_ui()

    def init_icons_dic(self):
        self.icons_dic = dict()
        self.icons_dic['life'] = QtGui.QIcon(ressources._heart_icon_)
        self.icons_dic['coins'] = QtGui.QIcon(ressources._coin_icon_)

    def build_ui(self):
        self.setObjectName('dark_widget')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget_no_hover')
        self.list_view.setColumnCount(9)
        self.list_view.setIconSize(QtCore.QSize(30,30))
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        self.list_view.setHeaderLabels(['Profile picture', 'User name', 'Level', 'Experience', 'Comments', 'Work time', 'Deaths', 'Life', 'Coins', 'Participation'])
        self.main_layout.addWidget(self.list_view)

    def refresh(self):
        if self.isVisible():
            all_user_rows = repository.get_users_list()
            indexes_dic = dict()
            xp_dic = dict()
            comments_dic = dict()
            work_time_dic = dict()
            deaths_dic = dict()
            if all_user_rows is not None:
                user_index = 0
                for user_row in all_user_rows:
                    if user_index not in indexes_dic.keys():
                        indexes_dic[user_index] = user_row['id']
                    if user_row['total_xp'] not in xp_dic.keys():
                        xp_dic[user_row['total_xp']] = user_row['id']
                    if user_row['comments_count'] not in comments_dic.keys():
                        comments_dic[user_row['comments_count']] = user_row['id']
                    if user_row['work_time'] not in work_time_dic.keys():
                        work_time_dic[user_row['work_time']] = user_row['id']
                    if user_row['deaths'] not in deaths_dic.keys():
                        deaths_dic[user_row['deaths']] = user_row['id']

                    if user_row['id'] not in self.user_ids.keys():
                        item = custom_user_tree_item(user_row, self.icons_dic, self.list_view.invisibleRootItem())
                        index = self.list_view.invisibleRootItem().indexOfChild(item)
                        self.list_view.invisibleRootItem().takeChild(index)
                        self.user_ids[user_row['id']] = item
                    else:
                        item = self.user_ids[user_row['id']]
                        item.user_row = user_row
                        item.fill_ui()
                        index = self.list_view.invisibleRootItem().indexOfChild(item)
                        self.list_view.invisibleRootItem().takeChild(index)
                    user_index += 1

            for index in indexes_dic.keys():
                item = self.user_ids[indexes_dic[index]]
                self.list_view.invisibleRootItem().insertChild(index, item)

            self.user_ids[all_user_rows[0]['id']].set_crown(1)
            if len(all_user_rows)>=2:
                self.user_ids[all_user_rows[1]['id']].set_crown(2)
            if len(all_user_rows)>=3:
                self.user_ids[all_user_rows[2]['id']].set_crown(3)

            first_xp_user_id = xp_dic[sorted(list(xp_dic.keys()))[-1]]
            self.user_ids[first_xp_user_id].set_xp_item()
            first_comment_user_id = comments_dic[sorted(list(comments_dic.keys()))[-1]]
            self.user_ids[first_comment_user_id].set_comment_item()
            first_worker_user_id = work_time_dic[sorted(list(work_time_dic.keys()))[-1]]
            self.user_ids[first_worker_user_id].set_work_time_item()
            first_deaths_user_id = deaths_dic[sorted(list(deaths_dic.keys()))[-1]]
            self.user_ids[first_deaths_user_id].set_death_item()

class custom_user_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, user_row, icons_dic, parent=None):
        super(custom_user_tree_item, self).__init__(parent)
        self.user_row = user_row
        self.icons_dic = icons_dic
        self.setup_ui()
        self.fill_ui()

    def setup_ui(self):
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)

    def set_crown(self, crown):
        if crown == 1:
            self.setIcon(2, QtGui.QIcon(ressources._gold_icon_))
        elif crown == 2:
            self.setIcon(2, QtGui.QIcon(ressources._silver_icon_))
        elif crown == 3:
            self.setIcon(2, QtGui.QIcon(ressources._bronze_icon_))

    def set_xp_item(self):
        self.setIcon(3, QtGui.QIcon(ressources._yellow_item_icon_))

    def set_comment_item(self):
        self.setIcon(4, QtGui.QIcon(ressources._green_item_icon_))

    def set_work_time_item(self):
        self.setIcon(5, QtGui.QIcon(ressources._red_item_icon_))

    def set_death_item(self):
        self.setIcon(6, QtGui.QIcon(ressources._skull_item_icon_))

    def fill_ui(self):
        user_icon = QtGui.QIcon()
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(self.user_row['profile_picture']), 'png', 30)
        user_icon.addPixmap(pm)
        self.setIcon(0, user_icon)
        self.setText(1, self.user_row['user_name'])
        self.setIcon(2, QtGui.QIcon())
        self.setText(2, str(self.user_row['level']))
        self.setIcon(3, QtGui.QIcon())
        self.setText(3, f"{str(self.user_row['total_xp'])}")
        self.setIcon(4, QtGui.QIcon())
        self.setText(4, f"{str(self.user_row['comments_count'])}")
        self.setIcon(5, QtGui.QIcon())
        string_time = tools.convert_seconds_to_string_time(float(self.user_row['work_time']))
        self.setText(5, string_time)
        self.setIcon(6, QtGui.QIcon())
        self.setText(6, f"{str(self.user_row['deaths'])}")
        self.setText(7, f"{str(self.user_row['life'])}%")
        self.setIcon(7, self.icons_dic['life'])
        self.setText(8, f"{str(self.user_row['coins'])}")
        self.setIcon(8, self.icons_dic['coins'])
        if self.user_row['championship_participation']:
            participation = 'Yes'
            self.setForeground(9, QtGui.QColor('#7ca657'))
        else:
            participation = 'No'
            self.setForeground(9, QtGui.QColor('#f0605b'))
        self.setText(9, participation)

