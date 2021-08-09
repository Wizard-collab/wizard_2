# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

class tabs_widget(QtWidgets.QFrame):

	currentChanged = pyqtSignal(int)

	def __init__(self, parent=None):
		super(tabs_widget, self).__init__(parent)
		self.build_ui()
		self.connect_functions()

	def build_ui(self):
		self.main_layout = QtWidgets.QHBoxLayout()
		self.main_layout.setContentsMargins(0,0,0,0)
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)

		self.tabs_widget = QtWidgets.QTabWidget()
		self.main_layout.addWidget(self.tabs_widget)

	def addTab(self, widget, title):
		return self.tabs_widget.addTab(widget, title)

	def connect_functions(self):
		self.tabs_widget.currentChanged.connect(self.currentChanged.emit)