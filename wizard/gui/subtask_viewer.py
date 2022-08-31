# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.core import path_utils

logger = logging.getLogger(__name__)

class subtask_viewer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(subtask_viewer, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Subtask viewer")

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.log_textEdit_scrollBar.rangeChanged.connect(lambda: self.log_textEdit_scrollBar.setValue(self.log_textEdit_scrollBar.maximum()))

    def update_log(self, log):
        self.analyse_log(log)

    def update_current_task(self, name):
        self.subtask_name_label.setText(name)

    def update_status(self, status):
        if status == 'Running':
            color = '#f79360'
        elif status == 'Killed':
            color = '#f0605b'
        elif status == 'Done':
            color = '#9cf277'
        self.status_frame.setStyleSheet(f"background-color:{color};border-radius:4px;")
        self.status_label.setText(status)

    def update_progress(self, percent):
        self.progress.setValue(percent)

    def build_ui(self):
        self.resize(QtCore.QSize(1400,1000))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.subtask_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.subtask_name_label)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.status_frame = QtWidgets.QFrame()
        self.status_frame.setFixedSize(8,8)
        self.status_frame.setStyleSheet(f"background-color:#f79360;border-radius:4px;")
        self.header_layout.addWidget(self.status_frame)

        self.status_label = QtWidgets.QLabel('Running')
        self.header_layout.addWidget(self.status_label)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximumHeight(6)
        self.progress.setObjectName('task_progressBar')
        self.progress.setStyleSheet('#task_progressBar{color:transparent;}')
        self.main_layout.addWidget(self.progress)

        self.log_textEdit = QtWidgets.QTextEdit()
        self.log_textEdit.setObjectName('console_textEdit')
        self.log_textEdit.setReadOnly(True)
        self.log_textEdit_scrollBar = self.log_textEdit.verticalScrollBar()
        self.main_layout.addWidget(self.log_textEdit)

    def analyse_log(self, log):
        if log.startswith('\n'):
            log = log[1:]
        for line in log.split('\n'):
            if 'INFO' in line:
                line = f'<span style="color:#90d1f0;">{line}'
            elif 'WARNI' in line:
                line = f'<strong><span style="color:#f79360;">{line}</strong>'
            elif 'CRITI' in line or 'ERRO' in line:
                line = f'<strong><span style="color:#f0605b;">{line}</strong>'
            self.log_textEdit.insertHtml(line+'<br>')
