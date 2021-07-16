# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys

# Wizard modules
from wizard.core import user
from wizard.core import custom_logger
logger = custom_logger.get_logger()

# Wizard gui modules
from wizard.gui import script_editor_widget
from wizard.gui import logging_widget

class console_widget(QtWidgets.QWidget):

    notification = pyqtSignal(str)

    def __init__(self, parent=None):
        super(console_widget, self).__init__(parent)
        self.custom_handler = logging_widget.custom_handler(self)
        logger.addHandler(self.custom_handler)
        self.script_editor_widget = script_editor_widget.script_editor_widget()
        self.build_ui()
        self.connect_functions()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()

    def changeEvent(self, event):
        if self.isActiveWindow():
            self.notification.emit('')
        event.accept()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def build_ui(self):
        self.resize(800,600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.menu_bar = QtWidgets.QMenuBar()
        self.main_layout.addWidget(self.menu_bar)
        self.console_action = self.menu_bar.addMenu("Console")
        self.clear_console_action = self.console_action.addAction("Clear")

        self.script_action = self.menu_bar.addMenu("Script")
        self.execute_action = self.script_action.addAction("Execute ( Ctrl+Return )")
        self.clear_script_action = self.script_action.addAction("Clear")

        self.console_viewer = QtWidgets.QTextEdit()
        self.console_viewer.setObjectName('console_textEdit')
        self.console_scrollBar = self.console_viewer.verticalScrollBar()
        self.console_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.console_viewer)

        self.main_layout.addWidget(self.script_editor_widget)

    def connect_functions(self):
        self.console_scrollBar.rangeChanged.connect(lambda: self.console_scrollBar.setValue(self.console_scrollBar.maximum()))
        self.custom_handler.log_record.connect(self.handle_record)
        self.exec_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Return'), self)
        self.exec_sc.activated.connect(self.execute_script)

        self.clear_console_action.triggered.connect(self.console_viewer.clear)

        self.execute_action.triggered.connect(self.execute_script)
        self.clear_script_action.triggered.connect(self.script_editor_widget.clear)

    def execute_script(self):
        data = self.script_editor_widget.selectedText()
        if data == '':
            data = self.script_editor_widget.text()
        user.user().execute_session(data)

    def handle_record(self, record_tuple):
        level = record_tuple[0]
        record_msg = record_tuple[1]
        if record_msg is not None and record_msg!='\n' and record_msg != '\r' and record_msg != '\r\n':
            if level == 'INFO':
                record_msg = f'<span style="color:#90d1f0;">{record_msg}'
                if not self.isActiveWindow():
                    self.notification.emit('info')
            elif level == 'STDOUT':
                record_msg = f'<span style="color:#ffffff;">{record_msg}'
            elif level == 'WARNING':
                record_msg = f'<strong><span style="color:#f79360;">{record_msg}</strong>'
                if not self.isActiveWindow():
                    self.notification.emit('warning')
            elif level == 'ERROR':
                record_msg = f'<strong><span style="color:#f0605b;">{record_msg}</strong>'
                if not self.isActiveWindow():
                    self.notification.emit('error')
            self.console_viewer.insertHtml(record_msg)
            self.console_viewer.insertHtml('<br>')
