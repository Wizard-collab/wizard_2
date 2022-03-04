# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys
import logging

# Wizard gui modules
from wizard.gui import gui_utils

class custom_handler(QtCore.QObject, logging.Handler):

    log_record = pyqtSignal(tuple)

    def __init__(self, parent):
        super(custom_handler, self).__init__(parent)
        self.setFormatter(logging.Formatter('[%(name)-23.23s] %(message)s'))

    def emit(self, record):
        try:
            self.log_record.emit((record.levelname, self.format(record)))
        except RuntimeError:
            pass

class logging_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(logging_widget, self).__init__(parent)

        self.custom_handler = custom_handler(self)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.custom_handler)

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        gui_utils.application_tooltip(self, "See logs here")
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.setLayout(self.main_layout)
        self.log_label = gui_utils.ElidedLabel()
        self.main_layout.addWidget(self.log_label)

    def handle_record(self, record_tuple):
        level = record_tuple[0]
        record_msg = record_tuple[1]
        if record_msg != '\r\n' and record_msg != '\r' and record_msg != '\n':
            if level == 'INFO':
                self.log_label.setStyleSheet('color:#90d1f0;')
            elif level == 'STDOUT':
                self.log_label.setStyleSheet('color:rgb(215,215,215);')
            elif level == 'WARNING':
                self.log_label.setStyleSheet('color:#f79360;')
            elif level == 'ERROR':
                self.log_label.setStyleSheet('color:#f0605b;')
            record_msg = record_msg.replace('\n', ' ')
            record_msg = record_msg.replace('\r', ' ')
            self.log_label.setText(record_msg)

    def connect_functions(self):
        self.custom_handler.log_record.connect(self.handle_record)
