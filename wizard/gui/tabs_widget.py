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


