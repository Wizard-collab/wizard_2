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

"""
This module defines the `error_handler` class, which provides a graphical interface for handling errors in the Wizard application.
It includes functionality to display error messages, allow users to add additional details, and send error reports to support.
The module also contains a `main` function to initialize and display the error handler widget.

Classes:
    error_handler: A QWidget-based class for displaying and managing error messages.

Functions:
    main(): Initializes the application and displays the error handler widget.

Dependencies:
    - PyQt6.QtWidgets
    - PyQt6.QtCore
    - PyQt6.QtGui
    - os
    - sys
    - wizard.gui.app_utils
    - wizard.vars.ressources
    - wizard.core.support
    - wizard.core.environment
"""

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import sys

# Wizard gui modules
from wizard.gui import app_utils

# Wizard modules
from wizard.vars import ressources
from wizard.core import support
from wizard.core import environment


class error_handler(QtWidgets.QWidget):
    """
    error_handler is a QWidget-based class that provides a graphical interface for handling errors in the Wizard application.
    It displays the error message, allows the user to add additional details, and provides options to either close the window
    or send the error details to support.
    Attributes:
        error (str): The error message to be displayed in the error handler window.
        main_layout (QVBoxLayout): The main layout of the widget.
        header_widget (QWidget): The header section of the widget containing the title and crash icon.
        crash_image (QLabel): A label displaying the crash icon.
        header_content_widget (QWidget): A widget containing the title and informational text.
        title_label (QLabel): A label displaying the title of the error handler.
        info_label (QLabel): A label displaying additional information about the error.
        error_label (QTextEdit): A text edit widget displaying the error message.
        additionnal_message_field (QTextEdit): A text edit widget for the user to add additional details about the error.
        close_button (QPushButton): A button to close the error handler window.
        send_to_support_button (QPushButton): A button to send the error details to support.
    Methods:
        __init__(error, parent=None):
            Initializes the error_handler instance with the given error message and parent widget.
        connect_functions():
            Connects the buttons to their respective functions.
        send_to_support():
            Sends the error details and additional message to support and closes the window.
        build_ui():
            Builds the user interface of the error handler.
        closeEvent(event):
            Closes all application windows when the error handler is closed.
        showEvent(event):
            Centers the error handler window on the screen when it is shown.
        center():
            Centers the error handler window on the screen.
    """

    def __init__(self, error, parent=None):
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
        self.setMaximumWidth(600)
        self.setMaximumHeight(700)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('header_frame')
        self.header_widget.setStyleSheet(
            '#header_frame{background-color:rgba(119, 133, 222, 190);}')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.crash_image = QtWidgets.QLabel()
        self.crash_image.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.crash_image.setPixmap(QtGui.QIcon(
            ressources._crash_icon_).pixmap(60))
        self.header_layout.addWidget(self.crash_image)

        self.header_content_widget = QtWidgets.QWidget()
        self.header_content_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.header_content_widget.setObjectName('transparent_widget')
        self.header_content_layout = QtWidgets.QVBoxLayout()
        self.header_content_layout.setContentsMargins(0, 0, 0, 0)
        self.header_content_layout.setSpacing(3)
        self.header_content_widget.setLayout(self.header_content_layout)
        self.header_layout.addWidget(self.header_content_widget)

        self.title_label = QtWidgets.QLabel('Wizard has crashed !')
        self.title_label.setObjectName('title_label_2')
        self.header_content_layout.addWidget(self.title_label)

        self.info_label = QtWidgets.QLabel(
            'Please send this error to the support,\nThat way wizard will probably be more stable in the future')
        self.header_content_layout.addWidget(self.info_label)

        self.header_content_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.content_layout.addWidget(QtWidgets.QLabel('Here is the error :'))

        self.error_label = QtWidgets.QTextEdit()
        self.error_label.setText(self.error)
        self.error_label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.content_layout.addWidget(self.error_label)

        self.content_layout.addWidget(
            QtWidgets.QLabel('You can add some details :'))

        self.additionnal_message_field = QtWidgets.QTextEdit()
        self.content_layout.addWidget(self.additionnal_message_field)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

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
        # screen = QtWidgets.QGuiApplication.primaryScreen().screenNumber(QtWidgets.QGuiApplication.primaryScreen().cursor().pos())
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
        centerPoint = screen.geometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


def main():
    """
    The main function initializes the application, retrieves the error message
    from the command-line arguments, and displays the error handler widget.

    Steps:
    1. Initializes the QApplication instance using app_utils.get_app().
    2. Retrieves the error message passed as a command-line argument.
    3. Creates an instance of the error_handler widget with the error message.
    4. Displays the error handler widget.
    5. Starts the application's event loop and exits when the application is closed.
    """
    app = app_utils.get_app()  # Initialize the application
    # Retrieve the error message from command-line arguments
    error = sys.argv[1]
    error_handler_widget = error_handler(
        error)  # Create the error handler widget
    error_handler_widget.show()  # Display the error handler widget
    sys.exit(app.exec())  # Start the application's event loop


if __name__ == '__main__':
    main()
