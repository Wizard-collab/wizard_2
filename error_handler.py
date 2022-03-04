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

class error_handler(QtWidgets.QWidget):
    def __init__(self, error, parent = None):
        super(error_handler, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Error handler")

        self.error = error
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.close_button.clicked.connect(self.close)
        self.send_to_support_button.clicked.connect(self.send_to_support)

    def send_to_support(self):
        additionnal_message = self.additionnal_message_field.toPlainText()
        support.send_log(self.error, 'crash', additionnal_message)
        self.close()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('header_frame')
        self.header_widget.setStyleSheet('#header_frame{background-color:rgba(119, 133, 222, 190);}')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.crash_image = QtWidgets.QLabel()
        self.crash_image.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.crash_image.setPixmap(QtGui.QIcon(ressources._crash_icon_).pixmap(60))
        self.header_layout.addWidget(self.crash_image)

        self.header_content_widget = QtWidgets.QWidget()
        self.header_content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.header_content_widget.setObjectName('transparent_widget')
        self.header_content_layout = QtWidgets.QVBoxLayout()
        self.header_content_layout.setContentsMargins(0,0,0,0)
        self.header_content_layout.setSpacing(3)
        self.header_content_widget.setLayout(self.header_content_layout)
        self.header_layout.addWidget(self.header_content_widget)

        self.title_label = QtWidgets.QLabel('Wizard has crashed !')
        self.title_label.setObjectName('title_label_2')
        self.header_content_layout.addWidget(self.title_label)

        self.info_label = QtWidgets.QLabel('Please send this error to the support,\nThat way wizard will probably be more stable in the future')
        self.header_content_layout.addWidget(self.info_label)

        self.header_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.content_layout.addWidget(QtWidgets.QLabel('Here is the error :'))

        self.error_frame = QtWidgets.QFrame()
        self.error_frame.setObjectName('error_handler_frame')
        self.error_layout = QtWidgets.QHBoxLayout()
        self.error_frame.setLayout(self.error_layout)
        self.content_layout.addWidget(self.error_frame)

        self.error_label = QtWidgets.QLabel(self.error)
        self.error_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.error_layout.addWidget(self.error_label)

        self.content_layout.addWidget(QtWidgets.QLabel('You can add some details :'))

        self.additionnal_message_field = QtWidgets.QTextEdit()
        self.content_layout.addWidget(self.additionnal_message_field)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.close_button = QtWidgets.QPushButton('Close')
        self.buttons_layout.addWidget(self.close_button)
        self.send_to_support_button = QtWidgets.QPushButton('Send to support')
        self.buttons_layout.addWidget(self.send_to_support_button)

    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()

    def showEvent(self, event):
        self.center()
        event.accept()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

def main():
    app = gui_utils.get_app()
    error = sys.argv[1]
    error_handler_widget = error_handler(error)
    error_handler_widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()