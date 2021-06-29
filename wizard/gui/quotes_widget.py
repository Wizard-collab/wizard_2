# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import random

# Wizard modules
from wizard.core import site

class quotes_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(quotes_widget, self).__init__(parent)
        self.previous_quote_id = None
        self.build_ui()
        self.connect_functions()
        self.get_new_random_quote()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.quote_label = QtWidgets.QLabel()
        self.quote_label.setWordWrap(True)
        self.quote_label.setObjectName('quote_label')
        self.quote_label.setMinimumHeight(0)
        self.main_layout.addWidget(self.quote_label)

        self.buttons_frame = QtWidgets.QFrame()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_frame.setLayout(self.buttons_layout)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)
        
        self.new_quote_button = QtWidgets.QPushButton()
        self.new_quote_button.setFixedSize(25,25)
        self.buttons_layout.addWidget(self.new_quote_button)

        self.my_quotes_button = QtWidgets.QPushButton()
        self.my_quotes_button.setFixedSize(25,25)
        self.buttons_layout.addWidget(self.my_quotes_button)

        self.random_button = QtWidgets.QPushButton()
        self.random_button.setFixedSize(25,25)
        self.buttons_layout.addWidget(self.random_button)

        self.main_layout.addWidget(self.buttons_frame)

    def connect_functions(self):
        self.random_button.clicked.connect(self.get_new_random_quote)

    def get_new_random_quote(self):
        quotes_ids = site.get_all_quotes('id')
        self.random_index = random.randint(0, len(quotes_ids)-1)
        while self.random_index == self.previous_quote_id:
            self.random_index = random.randint(0, len(quotes_ids)-1)
        self.previous_quote_id = self.random_index
        quote_row = site.get_quote_data(quotes_ids[self.random_index])
        self.quote_label.setText(quote_row['content'])


