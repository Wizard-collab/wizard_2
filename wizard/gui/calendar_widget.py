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
from wizard.vars import assets_vars
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
            self.users_images_dic[user_row['user_name']] = image.convert_str_data_to_image_bytes(user_image)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.calendarWidget = calendarWidget.calendarWidget()
        self.main_layout.addWidget(self.calendarWidget)

    def refresh(self):
        all_domains = project.get_domains()
        for domain_row in all_domains:
            if domain_row['name'] == assets_vars._library_:
                continue
            categories = project.get_domain_childs(domain_row['id'])
            for category_row in categories:
                assets = project.get_category_childs(category_row['id'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    for stage_row in stages:
                        date = calendar_utils.timestamp_to_datetime(stage_row['creation_time'])
                        duration = stage_row['estimated_time']/(3600*24)
                        text = f"{category_row['name']} | {asset_row['name']}"
                        widget = item_widget(stage_row, text, self.users_images_dic)
                        try:
                            self.calendarWidget.add_item(date=date, duration=duration, color=ressources._stages_colors_[stage_row['name']], widget=widget)
                        except:
                            pass

class item_widget(QtWidgets.QWidget):
    def __init__(self, stage_row, text, users_images_dic, parent=None):
        super(item_widget, self).__init__(parent)
        self.stage_row = stage_row
        self.text = text
        self.users_images_dic = users_images_dic
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)
        
        self.stage_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.stage_label)

        self.user_image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.user_image_label)

        self.name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.state_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.state_label)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_images_size()

    def fill_ui(self):
        self.name_label.setText(self.text)
        self.state_label.setText(self.stage_row['state'])
        self.update_images_size()

    def update_images_size(self):
        pixmap = gui_utils.mask_image(self.users_images_dic[self.stage_row['assignment']], 'png', self.height(), 4)
        self.user_image_label.setPixmap(pixmap)
        pixmap = QtGui.QIcon(ressources._stage_icons_dic_[self.stage_row['name']]).pixmap(self.height())
        self.stage_label.setPixmap(pixmap)
