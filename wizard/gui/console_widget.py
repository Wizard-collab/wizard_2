# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import sys
import logging

# Wizard modules
from wizard.core import user
from wizard.vars import user_vars
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import script_editor_widget
from wizard.gui import logging_widget
from wizard.gui import submit_log_widget

logger = logging.getLogger(__name__)

known_errors = ['libpng warning: iCCP: known incorrect sRGB profile',
                'The requested filter buffer is too big, ignoring']

class custom_stdout(QtCore.QObject):

    stdout_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(custom_stdout, self).__init__(parent)

    def write(self, buf):
        try:
            if buf in known_errors:
                return
            self.stdout_signal.emit(buf)
            if not sys.__stdout__:
                return
            sys.__stdout__.write(buf)
        except RuntimeError:
            if not sys.__stdout__:
                return
            sys.__stdout__.write(buf)

    def flush(self):
        if not sys.__stdout__:
            sys.__stdout__.flush()

class custom_stderr(QtCore.QObject):

    stderr_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(custom_stderr, self).__init__(parent)

    def write(self, buf):
        self.stderr_signal.emit(buf)
        if not sys.__stderr__:
            return
        sys.__stderr__.write(buf)

    def flush(self):
        if not sys.__stderr__:
            return
        sys.__stderr__.flush()

class console_widget(QtWidgets.QWidget):

    notification = pyqtSignal(str)

    def __init__(self, parent=None):
        super(console_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Console")

        self.custom_handler = logging_widget.custom_handler(long_formatter=True, parent=self)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.custom_handler)
        self.script_editor_widget = script_editor_widget.script_editor_widget()
        self.build_ui()
        self.redirect_stdout()
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

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def redirect_stdout(self):
        sys.stdout = custom_stdout()
        sys.stderr = custom_stderr()

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
        self.menu_bar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.header_custom_layout.addWidget(self.menu_bar)
        self.header_custom_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
        self.main_layout.addWidget(self.header_custom_widget)
        self.console_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, "Console")
        self.clear_console_action = self.console_action.addAction(QtGui.QIcon(ressources._archive_icon_), "Clear")
        self.send_to_support_action = self.console_action.addAction(QtGui.QIcon(ressources._send_icon_), "Send to support")

        self.script_action = gui_utils.add_menu_to_menu_bar(self.menu_bar, "Script")
        self.execute_action = self.script_action.addAction(QtGui.QIcon(ressources._play_icon_), "Execute ( Ctrl+Return )")
        self.clear_script_action = self.script_action.addAction(QtGui.QIcon(ressources._archive_icon_), "Clear")

        self.console_viewer = QtWidgets.QTextEdit()
        self.console_viewer.setObjectName('console_textEdit')
        self.console_scrollBar = self.console_viewer.verticalScrollBar()
        self.console_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.console_viewer)

        self.main_layout.addWidget(self.script_editor_widget)

    def connect_functions(self):
        self.console_scrollBar.rangeChanged.connect(lambda: self.console_scrollBar.setValue(self.console_scrollBar.maximum()))
        self.custom_handler.log_record.connect(self.handle_record)
        self.exec_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Return'), self)
        self.exec_sc.activated.connect(self.execute_script)

        self.clear_console_action.triggered.connect(self.console_viewer.clear)
        self.send_to_support_action.triggered.connect(self.send_to_support)

        self.execute_action.triggered.connect(self.execute_script)
        self.clear_script_action.triggered.connect(self.script_editor_widget.clear)
        
        sys.stdout.stdout_signal.connect(self.handle_stdout)
        sys.stderr.stderr_signal.connect(self.handle_stderr)

    def send_to_support(self):
        log = self.console_viewer.toPlainText()
        self.submit_log_widget = submit_log_widget.submit_log_widget(log, 'console')
        self.submit_log_widget.show()

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

    def handle_stdout(self, buf):
        if buf!='\n' and buf != '\r' and buf != '\r\n':
            self.console_viewer.insertHtml(buf)
            self.console_viewer.insertHtml('<br>')

    def handle_stderr(self, buf):
        if buf!='\n' and buf != '\r' and buf != '\r\n':
            buf = f'<strong><span style="color:#f0605b;">{buf}</strong>'
            self.console_viewer.insertHtml(buf)
            self.console_viewer.insertHtml('<br>')

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
