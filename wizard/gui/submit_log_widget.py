# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import sys

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.vars import ressources
from wizard.core import support
from wizard.core import environment

class submit_log_widget(QtWidgets.QWidget):
    def __init__(self, log, type, parent = None):
        super(submit_log_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Submit to support")

        self.log = log
        self.type = type
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.close_button.clicked.connect(self.close)
        self.send_to_support_button.clicked.connect(self.send_to_support)

    def send_to_support(self):
        additionnal_message = self.additionnal_message_field.toPlainText()
        support.send_log(self.log, self.type, additionnal_message)
        self.close()

    def build_ui(self):
        self.resize(450,400)
        self.setMaximumWidth(600)
        self.setMaximumHeight(700)
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QtWidgets.QLabel('Here is the log data :'))

        self.log_label = QtWidgets.QTextEdit()
        self.log_label.setText(self.log)
        self.log_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.main_layout.addWidget(self.log_label)

        self.main_layout.addWidget(QtWidgets.QLabel('Please add some details :'))

        self.additionnal_message_field = QtWidgets.QTextEdit()
        self.main_layout.addWidget(self.additionnal_message_field)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.close_button = QtWidgets.QPushButton('Close')
        self.buttons_layout.addWidget(self.close_button)
        self.send_to_support_button = QtWidgets.QPushButton('Send to support')
        self.buttons_layout.addWidget(self.send_to_support_button)

    def showEvent(self, event):
        self.center()
        event.accept()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
