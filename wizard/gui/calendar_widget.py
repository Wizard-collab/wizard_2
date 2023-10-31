# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import calendarWidget
from wizard.gui import gui_utils

# Wizard core modules
from wizard.core import calendar_utils
from wizard.core import image
from wizard.core import project
from wizard.core import repository
from wizard.vars import ressources

class calendar_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendar_widget, self).__init__(parent)
        self.build_ui()
        self.init_users_images()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 20, 4)
            self.users_images_dic[user_row['user_name']] = pixmap

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.calendarWidget = calendarWidget.calendarWidget()
        self.main_layout.addWidget(self.calendarWidget)

    def refresh(self):
        all_stages = project.get_all_stages()
        for stage_row in all_stages:
            date = calendar_utils.timestamp_to_datetime(stage_row['creation_time'])
            duration = stage_row['estimated_time']/(3600*24)
            widget = item_widget(stage_row, self.users_images_dic)
            try:
                self.calendarWidget.add_item(date=date, duration=duration, color=ressources._stages_colors_[stage_row['name']], widget=widget)
            except:
                pass

class item_widget(QtWidgets.QWidget):
    def __init__(self, stage_row, users_images_dic, parent=None):
        super(item_widget, self).__init__(parent)
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        self.user_image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.user_image_label)
        self.stage_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.stage_name_label)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def fill_ui(self):
        self.stage_name_label.setText(self.stage_row['string'])
        self.user_image_label.setPixmap(self.users_images_dic[self.stage_row['assignment']])