# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys

# Wizard modules
from wizard.core import user
from wizard.vars import user_vars
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger()

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import script_editor_widget
from wizard.gui import logging_widget

class console_widget(QtWidgets.QWidget):

    notification = pyqtSignal(str)

    def __init__(self, parent=None):
        super(console_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Console")

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
                self.close()
        else:
            self.show()
            self.raise_()

    def changeEvent(self, event):
        if self.isActiveWindow():
            self.notification.emit('')
        event.accept()

    def build_ui(self):
        self.resize(800,600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_custom_widget = QtWidgets.QWidget()
        self.header_custom_widget.setObjectName('transparent_widget')
        self.header_custom_layout = QtWidgets.QHBoxLayout()
        self.header_custom_layout.setContentsMargins(4,4,4,4)
        self.header_custom_layout.setSpacing(0)
        self.header_custom_widget.setLayout(self.header_custom_layout)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.header_custom_layout.addWidget(self.menu_bar)
        self.header_custom_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        self.main_layout.addWidget(self.header_custom_widget)
        self.console_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, "Console")
        self.clear_console_action = self.console_action.addAction("Clear")

        self.script_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, "Script")
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

    def set_context(self):
        data = self.script_editor_widget.text()
        context_dic = dict()
        context_dic['content'] = data
        user.user().add_context(user_vars._console_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._console_context_)
        if context_dic is not None and context_dic != dict():
            data = context_dic['content']
            self.script_editor_widget.setText(data)

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
