# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class log_viewer(QtWidgets.QWidget):

    def __init__(self, file=None, parent=None):
        super(log_viewer, self).__init__(parent)

        self.build_ui()
        self.file = file
        self.refresh()

    def set_file(self, file):
        self.file = file
        self.refresh()

    def refresh(self):
        if self.file is not None:
            if os.path.isfile(self.file):
                self.file_name_label.setText(self.file)
                with open(self.file, 'r') as f:
                    data = f.read()
                self.analyse_log(data)
            else:
                logger.warning(f"{self.file} doesn't exists")
        else:
            logger.warning("No valid file given")

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.file_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.file_name_label)

        self.log_textEdit = QtWidgets.QTextEdit()
        self.log_textEdit.setObjectName('console_textEdit')
        self.log_textEdit.setReadOnly(True)
        self.log_textEdit_scrollBar = self.log_textEdit.verticalScrollBar()
        self.main_layout.addWidget(self.log_textEdit)

    def analyse_log(self, log):
        for line in log.split('\n'):
            if 'INFO' in line:
                line = f'<span style="color:#90d1f0;">{line}'
            elif 'WARNI' in line:
                line = f'<strong><span style="color:#f79360;">{line}</strong>'
            elif 'CRITI' in line or 'ERRO' in line:
                line = f'<strong><span style="color:#f0605b;">{line}</strong>'
            self.log_textEdit.insertHtml(line)
            self.log_textEdit.insertHtml('<br>')
