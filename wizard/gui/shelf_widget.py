# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources
from wizard.core import shelf
from wizard.core import project

class shelf_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(shelf_widget, self).__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(4,4,4,4)
        self.setLayout(self.main_layout)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(2)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.add_script_button = QtWidgets.QPushButton()
        self.add_script_button.setFixedSize(20,20)
        self.add_script_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_script_button.setIconSize(QtCore.QSize(10,10))
        self.main_layout.addWidget(self.add_script_button)

    def refresh(self):
        shelf_scripts_rows = project.get_all_shelf_scripts()
        if shelf_scripts_rows is not None:
            for shelf_script_row in shelf_scripts_rows:
                self.button = shelf_script_button(shelf_script_row)
                self.button.exec_signal.connect(self.exec_script)
                self.buttons_layout.addWidget(self.button)

    def exec_script(self, shelf_script_row):
        shelf.execute_script(shelf_script_row['id'])

class shelf_script_button(QtWidgets.QToolButton):

    exec_signal = pyqtSignal(dict)

    def __init__(self, shelf_script_row, parent=None):
        super(shelf_script_button, self).__init__(parent)
        self.shelf_script_row = shelf_script_row
        self.setFixedWidth(30)
        self.setObjectName('shelf_script_button')
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setText(shelf_script_row['name'])
        self.setIcon(QtGui.QIcon(shelf_script_row['icon']))
        self.setIconSize(QtCore.QSize(10,10))
        self.connect_functions()

    def connect_functions(self):
        self.clicked.connect(lambda:self.exec_signal.emit(self.shelf_script_row))