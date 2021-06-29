# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import environment
from wizard.core import site
from wizard.core import image
from wizard.vars import ressources

class user_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(user_widget, self).__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(70,70)
        self.main_layout.addWidget(self.profile_picture)

        self.infos_frame = QtWidgets.QFrame()
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(10)
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.infos_layout.addWidget(QtWidgets.QLabel(environment.get_user()))

        #self.info_xp_label = QtWidgets.QLabel('Experience')
        #self.info_xp_label.setObjectName('gray_label')
        #self.infos_layout.addWidget(self.info_xp_label)
        self.xp_progress_bar = QtWidgets.QProgressBar()
        self.xp_progress_bar.setObjectName('user_xp_progressBar')
        self.xp_progress_bar.setFixedHeight(6)
        self.xp_progress_bar.setTextVisible(0)
        self.infos_layout.addWidget(self.xp_progress_bar)
        #self.info_life_label = QtWidgets.QLabel('Life')
        #self.info_life_label.setObjectName('gray_label')
        #self.infos_layout.addWidget(self.info_life_label)
        self.life_progress_bar = QtWidgets.QProgressBar()
        self.life_progress_bar.setObjectName('user_life_progressBar')
        self.life_progress_bar.setFixedHeight(6)
        self.life_progress_bar.setTextVisible(0)
        self.infos_layout.addWidget(self.life_progress_bar)

        self.badges_frame = QtWidgets.QFrame()
        self.badges_layout = QtWidgets.QHBoxLayout()
        self.badges_layout.setContentsMargins(0,0,0,0)
        self.badges_frame.setLayout(self.badges_layout)
        self.admin_badge_label = QtWidgets.QLabel()
        self.admin_badge_label.setPixmap(QtGui.QPixmap(ressources._admin_badge_).scaled(
            18, 18, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        self.badges_layout.addWidget(self.admin_badge_label)
        self.badges_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding))

        self.info_level_label = QtWidgets.QLabel('Level ')
        self.info_level_label.setObjectName('gray_label')
        self.badges_layout.addWidget(self.info_level_label)
        self.level_label = QtWidgets.QLabel('23')
        self.badges_layout.addWidget(self.level_label)

        self.infos_layout.addWidget(self.badges_frame)
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.infos_frame.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_frame)

    def refresh(self):
        user_row = site.get_user_row_by_name(environment.get_user())
        self.xp_progress_bar.setValue(user_row['xp'])
        self.life_progress_bar.setValue(user_row['life'])
        self.level_label.setText(str(user_row['level']))
        self.admin_badge_label.setVisible(user_row['administrator'])
        self.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(user_row['profile_picture']))

    def round_image(self, label, image_bytes):
        label.Antialiasing = True
        label.radius = 35
        label.target = QtGui.QPixmap(label.size())
        label.target.fill(QtCore.Qt.transparent)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_bytes, 'png')
        pixmap = pixmap.scaled(
            70, 70, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        painter = QtGui.QPainter(label.target)
        if label.Antialiasing:
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            0, 0, label.width(), label.height(), label.radius, label.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        label.setPixmap(label.target)