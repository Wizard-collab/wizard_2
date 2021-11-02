# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.vars import ressources

class estimation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(estimation_widget, self).__init__(parent)
        self.hours = 6
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)

    def connect_functions(self):
        self.close_pushButton.clicked.connect(self.reject)
        self.enter_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        self.enter_sc.activated.connect(self.apply)

    def apply(self):
        self.hours = self.hours_spinBox.value()
        self.accept()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QHBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.hours_spinBox = QtWidgets.QSpinBox()
        self.hours_spinBox.setRange(1, 200)
        self.hours_spinBox.setValue(6)
        self.hours_spinBox.setButtonSymbols(2)
        self.frame_layout.addWidget(self.hours_spinBox)

        self.hours_label = QtWidgets.QLabel('hours')
        self.frame_layout.addWidget(self.hours_label)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_pushButton = QtWidgets.QPushButton()
        self.close_pushButton.setObjectName('window_decoration_button')
        self.close_pushButton.setIcon(QtGui.QIcon(ressources._close_icon_))
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)