# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger()

# Wizard gui modules
from wizard.gui import gui_utils

class custom_handler(QtCore.QObject, logging.Handler):

    log_record = pyqtSignal(tuple)

    def __init__(self, parent):
        super(custom_handler, self).__init__(parent)

    def emit(self, record):
        self.log_record.emit((record.levelname, self.format(record)))

class logging_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(logging_widget, self).__init__(parent)
        self.custom_handler = custom_handler(self)
        logger.addHandler(self.custom_handler)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.main_layout)
        self.log_label = gui_utils.ElidedLabel()
        self.main_layout.addWidget(self.log_label)

    def handle_record(self, record_tuple):
        level = record_tuple[0]
        record_msg = record_tuple[1]
        if level == 'INFO':
            self.log_label.setStyleSheet('color:white;')
        elif level == 'WARNING':
            self.log_label.setStyleSheet('color:#f79360;')
        elif level == 'ERROR':
            self.log_label.setStyleSheet('color:#f0605b;')
        self.log_label.setText(record_msg)

    def connect_functions(self):
        self.custom_handler.log_record.connect(self.handle_record)