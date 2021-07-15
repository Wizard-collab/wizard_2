# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger()

# Wizard gui modules
from wizard.gui import logging_widget

class console_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(console_widget, self).__init__(parent)

        self.custom_handler = logging_widget.custom_handler(self)
        logger.addHandler(self.custom_handler)

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.console_viewer = QtWidgets.QTextEdit()
        self.console_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.console_viewer)

    def connect_functions(self):
        self.streamHandler = streamHandler()
        sys.stdout = self.streamHandler
        #sys.stderr = self.streamHandler
        self.streamHandler.stream.connect(self.handle_record)
        self.custom_handler.log_record.connect(self.handle_record)

    def handle_record(self, record_tuple):
        level = record_tuple[0]
        record_msg = record_tuple[1]
        if record_msg is not None and record_msg!='\n' and record_msg != '\r' and record_msg != '\r\n':
            if level == 'INFO':
                record_msg = f'<span style="color:#ffffff;">{record_msg}'
            if level == 'WARNING':
                record_msg = f'<span style="color:#f79360;">{record_msg}'
            elif level == 'ERROR':
                record_msg = f'<span style="color:#f0605b;">{record_msg}'
            self.console_viewer.insertHtml(record_msg)
            self.console_viewer.insertHtml('<br>')

class streamHandler(QtCore.QObject):

    stream = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(streamHandler, self).__init__(parent)

    def write(self, stream):
        self.stream.emit(('INFO', str(stream)))