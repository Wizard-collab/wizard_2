# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

class message_widget(QtWidgets.QDialog):
    def __init__(self, title, message, parent=None):
        super(message_widget, self).__init__(parent)
        self.title = title
        self.message = message
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setMinimumSize(350, 120)
        self.resize(350, 120)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel(self.title)
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.message_label = QtWidgets.QLabel(self.message)
        self.message_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.message_label)

        self.spaceItem = QtWidgets.QSpacerItem(10,100,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.spaceItem = QtWidgets.QSpacerItem(10,100,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)
        self.ok_button = QtWidgets.QPushButton('Ok')
        self.ok_button.setObjectName("red_button")
        self.buttons_layout.addWidget(self.ok_button)
        self.main_layout.addWidget(self.buttons_widget)

    def connect_functions(self):
        self.ok_button.clicked.connect(self.accept)