# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import time

# Wizard modules
from wizard.core import tools
from wizard.core import repository
from wizard.core import image
from wizard.vars import ressources
from wizard.vars import game_vars

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils


class attack_history_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(attack_history_widget, self).__init__(parent)

        self.last_time = 0
        self.attack_ids = dict()
        self.users_images_dic = dict()

        self.build_ui()
        self.refresh_users_dic()
        self.connect_functions()

    def connect_functions(self):
        self.event_count_spinBox.valueChanged.connect(self.change_count)

    def change_count(self):
        self.clear_all_attack_events()
        self.refresh()

    def clear_all_attack_events(self):
        attack_event_ids = list(self.attack_ids.keys())
        for attack_id in attack_event_ids:
            self.remove_attack_event(attack_id)

    def remove_attack_event(self, attack_id):
        if attack_id in self.attack_ids.keys():
            self.attack_ids[attack_id]['widget'].setVisible(False)
            self.attack_ids[attack_id]['widget'].setParent(None)
            self.attack_ids[attack_id]['widget'].deleteLater()
            del self.attack_ids[attack_id]

    def refresh_users_dic(self):
        users_rows = repository.get_users_list()
        for user_row in users_rows:
            if user_row['user_name'] not in self.users_images_dic.keys():
                pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(
                    user_row['profile_picture']), 'png', 24)
                self.users_images_dic[user_row['user_name']] = pm

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.events_scrollArea = QtWidgets.QScrollArea()
        self.events_scrollArea.setObjectName('transparent_widget')
        self.events_scrollArea.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.events_scrollBar = self.events_scrollArea.verticalScrollBar()

        self.events_scrollArea_widget = QtWidgets.QWidget()
        self.events_scrollArea_widget.setObjectName('transparent_widget')
        self.events_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.events_scrollArea_layout.setContentsMargins(0, 4, 8, 4)
        self.events_scrollArea_layout.setSpacing(0)
        self.events_scrollArea_widget.setLayout(self.events_scrollArea_layout)

        self.events_content_widget = QtWidgets.QWidget()
        self.events_content_widget.setObjectName('transparent_widget')
        self.events_content_layout = QtWidgets.QVBoxLayout()
        self.events_content_layout.setContentsMargins(0, 0, 0, 0)
        self.events_content_layout.setSpacing(3)
        self.events_content_widget.setLayout(self.events_content_layout)
        self.events_scrollArea_layout.addWidget(self.events_content_widget)

        self.events_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.events_scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.events_scrollArea.setWidgetResizable(True)
        self.events_scrollArea.setWidget(self.events_scrollArea_widget)
        self.main_layout.addWidget(self.events_scrollArea)

        self.infos_frame = QtWidgets.QFrame()
        self.infos_frame.setObjectName('round_frame')
        self.infos_layout = QtWidgets.QHBoxLayout()
        # self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_frame.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_frame)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.infos_layout.addWidget(QtWidgets.QLabel('Show'))
        self.event_count_spinBox = QtWidgets.QSpinBox()
        self.event_count_spinBox.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.event_count_spinBox.setValue(10)
        self.event_count_spinBox.setRange(1, 10000000)
        self.event_count_spinBox.setFixedWidth(50)
        self.infos_layout.addWidget(self.event_count_spinBox)
        self.infos_layout.addWidget(QtWidgets.QLabel('events'))

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            300, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))

    def refresh(self):
        self.last_time = 0
        attack_rows = repository.get_all_attack_events()
        event_number = self.event_count_spinBox.value()
        for attack_row in attack_rows[-event_number:]:
            if attack_row['id'] not in self.attack_ids.keys():
                widget = attack_event_widget(attack_row, self.users_images_dic)
                self.attack_ids[attack_row['id']] = dict()
                self.attack_ids[attack_row['id']]['widget'] = widget
                self.attack_ids[attack_row['id']]['row'] = attack_row
                self.events_content_layout.addWidget(
                    self.attack_ids[attack_row['id']]['widget'])

                if attack_row['attack_date']-self.last_time > 350:
                    self.attack_ids[attack_row['id']]['widget'].add_time()
                self.last_time = attack_row['attack_date']


class attack_event_widget(QtWidgets.QFrame):
    def __init__(self, attack_row, users_images_dic, parent=None):
        super(attack_event_widget, self).__init__(parent)
        self.time_widget = None
        self.attack_row = attack_row
        self.users_images_dic = users_images_dic
        self.build_ui()
        self.fill_ui()

    def add_time(self):
        if self.time_widget == None:
            self.time_widget = time_widget(self.attack_row['attack_date'])
            self.overall_layout.insertWidget(0, self.time_widget)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.setObjectName('transparent_widget')
        self.overall_layout = QtWidgets.QVBoxLayout()
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(6)
        self.setLayout(self.overall_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.overall_layout.addWidget(self.main_widget)

        self.artefact_image_label = QtWidgets.QLabel()
        self.artefact_image_label.setFixedSize(40, 40)
        self.main_layout.addWidget(self.artefact_image_label)

        self.attacking_user_image = QtWidgets.QLabel()
        self.attacking_user_image.setFixedSize(24, 24)
        self.main_layout.addWidget(self.attacking_user_image)

        self.attacking_user_label = QtWidgets.QLabel()
        self.attacking_user_label.setObjectName('title_label_2')
        self.main_layout.addWidget(self.attacking_user_label)

        self.attack_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.attack_label)

        self.victim_user_image = QtWidgets.QLabel()
        self.victim_user_image.setFixedSize(24, 24)
        self.main_layout.addWidget(self.victim_user_image)

        self.victim_user_label = QtWidgets.QLabel()
        self.victim_user_label.setObjectName('title_label_2')
        self.main_layout.addWidget(self.victim_user_label)

        self.attack_info_label = QtWidgets.QLabel()
        self.attack_info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.attack_info_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def fill_ui(self):
        self.attacking_user_image.setPixmap(
            self.users_images_dic[self.attack_row['creation_user']])
        self.attacking_user_label.setText(self.attack_row['creation_user'])
        self.attack_info_label.setText(
            f"( {game_vars.artefacts_dic[self.attack_row['artefact']]['description']} )")
        self.attack_label.setText(
            f"used {game_vars.artefacts_dic[self.attack_row['artefact']]['name']} against")
        self.artefact_image_label.setPixmap(QtGui.QIcon(
            game_vars.artefacts_dic[self.attack_row['artefact']]['icon']).pixmap(40))
        self.victim_user_image.setPixmap(
            self.users_images_dic[self.attack_row['destination_user']])
        self.victim_user_label.setText(self.attack_row['destination_user'])


class time_widget(QtWidgets.QWidget):
    def __init__(self, time_float, parent=None):
        super(time_widget, self).__init__(parent)
        self.time_float = time_float
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        day, hour = tools.convert_time(self.time_float)
        self.day_label = QtWidgets.QLabel(
            f"{tools.time_ago_from_timestamp(self.time_float)} - ")
        self.day_label.setObjectName('gray_label')
        self.hour_label = QtWidgets.QLabel(hour)
        self.hour_label.setObjectName('bold_label')
        current_day, current_hour = tools.convert_time(time.time())
        if current_day != day:
            self.main_layout.addWidget(self.day_label)
        self.main_layout.addWidget(self.hour_label)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))
