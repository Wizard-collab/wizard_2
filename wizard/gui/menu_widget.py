# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal


class menu_widget(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(menu_widget, self).__init__(parent)
        self.function_request = None
        self.build_ui()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)
        self.move_ui()

    def build_ui(self):
    	self.main_layout = QtWidgets.QVBoxLayout()
    	self.setLayout(self.main_layout)

    def leaveEvent(self, event):
        self.reject()

    def move_ui(self):
        win_size = (self.frameSize().width(), self.frameSize().height())
        posx = QtGui.QCursor.pos().x() - 10
        posy = int(QtGui.QCursor.pos().y()) - win_size[1] + 10
        self.move(posx, posy)

    def set_function_name_and_close(self, function_name):
    	self.function_name = function_name
    	self.accept()

    def add_action(self, function_name):
        pushButton = QtWidgets.QPushButton(function_name)
        self.main_layout.addWidget(pushButton)
        pushButton.clicked.connect(self.close)
        pushButton.clicked.connect(lambda:self.set_function_name_and_close(function_name))
        return function_name