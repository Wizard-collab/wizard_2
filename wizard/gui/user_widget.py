# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import all_users_widget

# Wizard modules
from wizard.core import environment
from wizard.core import site
from wizard.core import image
from wizard.vars import ressources

class user_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(user_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

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

        self.crown_label = QtWidgets.QLabel()
        self.items_layout.addWidget(self.crown_label)

        self.ranking_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.ranking_button, "Wizard cup")
        self.ranking_button.setFixedSize(28,28)
        self.ranking_button.setIcon(QtGui.QIcon(ressources._ranking_icon_))
        #self.items_layout.addWidget(self.ranking_button)

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
        user_row = site.get_user_row_by_name(environment.get_user())
        self.xp_progress_bar.setValue(user_row['xp'])
        self.life_progress_bar.setValue(user_row['life'])
        self.level_label.setText(str(user_row['level']))
        self.admin_badge_label.setVisible(user_row['administrator'])
        gui_utils.round_image(self.profile_picture,
                                image.convert_str_data_to_image_bytes(user_row['profile_picture']),
                                28)
        self.crown_check(user_row)

    def connect_functions(self):
        self.ranking_button.clicked.connect(self.show_all_user_widget)

    def show_all_user_widget(self):
        self.all_users_widget = all_users_widget.all_users_widget()
        self.all_users_widget.toggle()

    def crown_check(self, user_row):
        user_rows = site.get_users_list()
        icon = None
        if user_row['id'] == user_rows[0]['id']:
            icon = ressources._gold_icon_
        if len(user_rows)>=2:
            if (user_row['id'] ==  user_rows[1]['id']):
                icon = ressources._silver_icon_
        if len(user_rows)>=3:
            if (user_row['id'] == user_rows[2]['id']):
                icon = ressources._bronze_icon_
        if icon is not None:
            self.crown_label.setVisible(1)
            self.crown_label.setPixmap(QtGui.QIcon(icon).pixmap(22))
        else:
            self.crown_label.setVisible(0)
    