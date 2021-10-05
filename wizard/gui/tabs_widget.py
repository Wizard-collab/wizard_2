# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import user
from wizard.core import assets
from wizard.vars import user_vars
from wizard.vars import ressources

class tabs_widget(QtWidgets.QFrame):

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(tabs_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.string_asset_widget = string_asset_widget(self)
        self.main_layout.addWidget(self.string_asset_widget)

        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setIconSize(QtCore.QSize(16,16))
        self.main_layout.addWidget(self.tabs_widget)

    def addTab(self, widget, icon, title):
        return self.tabs_widget.addTab(widget, icon, title)

    def setCurrentIndex(self, index):
        return self.tabs_widget.setCurrentIndex(index)

    def connect_functions(self):
        self.tabs_widget.currentChanged.connect(self.currentChanged.emit)

    def set_context(self):
        current_index = self.tabs_widget.currentIndex()
        context_dic = dict()
        context_dic['index'] = current_index
        user.user().add_context(user_vars._tabs_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._tabs_context_)
        if context_dic is not None and context_dic != dict():
            index = context_dic['index']
            self.setCurrentIndex(index)

    def change_work_env(self, work_env_id):
        self.string_asset_widget.change_work_env(work_env_id)

class string_asset_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(string_asset_widget, self).__init__(parent)
        self.work_env_id = None
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(2,2,2,2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open work environment folder")
        self.folder_button.setFixedSize(QtCore.QSize(26, 26))
        self.folder_button.setIconSize(QtCore.QSize(20, 20))
        self.folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.main_layout.addWidget(self.folder_button)

        self.string_asset_lineEdit = QtWidgets.QLineEdit()
        self.string_asset_lineEdit.setPlaceholderText('...')
        self.main_layout.addWidget(self.string_asset_lineEdit)

    def change_work_env(self, work_env_id):
        self.work_env_id = work_env_id
        if self.work_env_id:
            string_asset = assets.instance_to_string(('work_env', work_env_id))
            self.string_asset_lineEdit.setText(string_asset)
        else:
            self.string_asset_lineEdit.setText('')

    def connect_functions(self):
        self.folder_button.clicked.connect(self.open_work_env_folder)

    def open_work_env_folder(self):
        if self.work_env_id:
            work_env_path = assets.get_work_env_path(self.work_env_id)
            if os.path.isdir(work_env_path):
                os.startfile(work_env_path)