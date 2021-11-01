# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os

# Wizard modules
from wizard.vars import ressources

class image_viewer_widget(QtWidgets.QWidget):
    def __init__(self, image):
        super(image_viewer_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Image viewer")

        self.image = image
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.main_image_label = QtWidgets.QLabel()
        self.main_image_label.setPixmap(QtGui.QPixmap(self.image).scaled(1600,100,
                    QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        self.main_layout.addWidget(self.main_image_label)

    def showEvent(self, event):
        self.center()
        event.accept()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())