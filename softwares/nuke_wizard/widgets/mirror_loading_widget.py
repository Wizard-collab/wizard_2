# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
from PySide2 import QtWidgets, QtCore, QtGui
import logging

class mirror_loading_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(mirror_loading_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.title_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.main_layout.addWidget(self.progress_bar)

        self.infos_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.infos_label)

    def set_title(self, title):
        self.title_label.setText(title)
        QtWidgets.QApplication.processEvents()

    def set_info(self, info):
        self.infos_label.setText(info)
        QtWidgets.QApplication.processEvents()

    def set_progress(self, progress):
        self.progress_bar.setValue(int(progress))
        QtWidgets.QApplication.processEvents()
