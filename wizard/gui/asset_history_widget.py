# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

class asset_history_widget(QtWidgets.QFrame):
	def __init__(self, parent=None):
		super(asset_history_widget, self).__init__(parent)
		self.build_ui()

	def build_ui(self):
		self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
		self.main_layout = QtWidgets.QVBoxLayout()
		self.setLayout(self.main_layout)

		self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(300,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))