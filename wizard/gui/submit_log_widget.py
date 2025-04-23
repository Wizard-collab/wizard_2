# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import sys

# Wizard modules
from wizard.vars import ressources
from wizard.core import support


class submit_log_widget(QtWidgets.QWidget):
    def __init__(self, log, type, parent=None):
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
        self.resize(450, 400)
        self.setMaximumWidth(600)
        self.setMaximumHeight(700)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QtWidgets.QLabel('Here is the log data :'))

        self.log_label = QtWidgets.QTextEdit()
        self.log_label.setText(self.log)
        self.log_label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.main_layout.addWidget(self.log_label)

        self.main_layout.addWidget(
            QtWidgets.QLabel('Please add some details :'))

        self.additionnal_message_field = QtWidgets.QTextEdit()
        self.main_layout.addWidget(self.additionnal_message_field)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.close_button = QtWidgets.QPushButton('Close')
        self.buttons_layout.addWidget(self.close_button)
        self.send_to_support_button = QtWidgets.QPushButton('Send to support')
        self.buttons_layout.addWidget(self.send_to_support_button)

    def showEvent(self, event):
        self.center()
        event.accept()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
        centerPoint = screen.geometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
