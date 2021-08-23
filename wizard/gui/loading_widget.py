# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import environment

class loading_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(loading_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.build_ui()

    def build_ui(self):
        self.setMaximumSize(QtCore.QSize(400,300))
        self.setMinimumSize(QtCore.QSize(400,300))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('loading_widget_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setContentsMargins(10,10,10,10)
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.info_label = QtWidgets.QLabel(f'Loading {environment.get_project_name()}...')
        self.info_label.setObjectName('bold_label')
        self.frame_layout.addWidget(self.info_label)
