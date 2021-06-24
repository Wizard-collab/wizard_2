# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import environment
from wizard.core import site
from wizard.core import image

class user_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(user_widget, self).__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(90,90)
        self.main_layout.addWidget(self.profile_picture)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)

        self.infos_layout.addWidget(QtWidgets.QLabel('Experience'))
        self.xp_progress_bar = QtWidgets.QProgressBar()
        self.xp_progress_bar.setFixedHeight(6)
        self.xp_progress_bar.setTextVisible(0)
        self.infos_layout.addWidget(self.xp_progress_bar)
        self.infos_layout.addWidget(QtWidgets.QLabel('Life'))
        self.life_progress_bar = QtWidgets.QProgressBar()
        self.life_progress_bar.setFixedHeight(6)
        self.life_progress_bar.setTextVisible(0)
        self.infos_layout.addWidget(self.life_progress_bar)

        self.badges_widget = QtWidgets.QWidget()
        self.badges_layout = QtWidgets.QHBoxLayout()
        self.badges_layout.setContentsMargins(0,0,0,0)
        self.badges_widget.setLayout(self.badges_layout)
        self.badges_layout.addWidget(QtWidgets.QLabel('Level '))
        self.level_label = QtWidgets.QLabel('23')
        self.badges_layout.addWidget(self.level_label)
        self.badges_layout.addSpacerItem(QtWidgets.QSpacerItem(150,10,QtWidgets.QSizePolicy.Expanding))
        self.admin_badge_label = QtWidgets.QLabel('O')
        self.badges_layout.addWidget(self.admin_badge_label)
        self.infos_layout.addWidget(self.badges_widget)

        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

    def refresh(self):
        user_row = site.get_user_row_by_name(environment.get_user())
        self.xp_progress_bar.setValue(user_row['xp'])
        self.life_progress_bar.setValue(user_row['life'])
        self.level_label.setText(str(user_row['level']))
        self.admin_badge_label.setVisible(user_row['administrator'])
        self.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(user_row['profile_picture']))

    def round_image(self, label, image_bytes):
        label.Antialiasing = True
        label.radius = 45
        label.target = QtGui.QPixmap(label.size())
        label.target.fill(QtCore.Qt.transparent)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_bytes, 'png')
        pixmap = pixmap.scaled(
            90, 90, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
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