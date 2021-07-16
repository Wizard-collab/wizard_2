# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import gui_utils


class menu_widget(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(menu_widget, self).__init__(parent)
        self.function_request = None
        self.buttons = []
        self.build_ui()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName("menu_widget_frame")
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(1)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)
        self.setLayout(self.main_layout)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()

    def apply_round_corners(self, corner):
        if len(self.buttons) > 1:
            if corner == 'top-right':
                self.buttons[0].setStyleSheet('border-top-left-radius:10px')
                self.buttons[-1].setStyleSheet('border-bottom-right-radius:10px;border-bottom-left-radius:10px')
            elif corner == 'top-left':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px')
                self.buttons[-1].setStyleSheet('border-bottom-right-radius:10px;border-bottom-left-radius:10px')
            elif corner == 'bottom-right':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px;border-top-left-radius:10px')
                self.buttons[-1].setStyleSheet('border-bottom-left-radius:10px')
            elif corner == 'bottom-left':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px;border-top-left-radius:10px')
                self.buttons[-1].setStyleSheet('border-bottom-right-radius:10px')
        else:
            if corner == 'top-right':
                self.buttons[0].setStyleSheet('border-top-left-radius:10px;border-bottom-left-radius:10px;border-bottom-right-radius:10px')
            elif corner == 'top-left':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px;border-bottom-left-radius:10px;border-bottom-right-radius:10px')
            elif corner == 'bottom-right':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px;border-bottom-left-radius:10px;border-top-right-radius:10px')
            elif corner == 'bottom-left':
                self.buttons[0].setStyleSheet('border-top-right-radius:10px;border-bottom-right-radius:10px;border-top-right-radius:10px')


    def leaveEvent(self, event):
        self.reject()

    def set_function_name_and_close(self, function_name):
        self.function_name = function_name
        self.accept()

    def add_action(self, function_name, icon=None):
        pushButton = QtWidgets.QPushButton(function_name)
        pushButton.setObjectName('menu_widget_button')
        if icon is not None:
            pushButton.setIcon(QtGui.QIcon(icon))
            pushButton.setIconSize(QtCore.QSize(22,22))
        self.buttons.append(pushButton)
        self.frame_layout.addWidget(pushButton)
        pushButton.clicked.connect(self.close)
        pushButton.clicked.connect(lambda:self.set_function_name_and_close(function_name))
        return function_name