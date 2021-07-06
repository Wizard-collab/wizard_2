# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules

class tabs_widget(QtWidgets.QTabWidget):
	def __init__(self, parent=None):
		super(tabs_widget, self).__init__(parent)
