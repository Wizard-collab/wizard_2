# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os
import logging

from wizard.vars import ressources

class custom_tab_widget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(custom_tab_widget, self).__init__(parent)
		self.build_ui()
		self.tabs_dic = dict()
		self.index = None

	def build_ui(self):
		self.main_layout = QtWidgets.QHBoxLayout()
		self.main_layout.setContentsMargins(0,0,0,0)
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)

		self.buttons_widget = QtWidgets.QWidget()
		self.buttons_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
		self.buttons_widget.setObjectName('dark_widget')
		self.buttons_layout = QtWidgets.QVBoxLayout()
		self.buttons_layout.setSpacing(0)
		self.buttons_layout.setContentsMargins(11,11,11,11)
		self.buttons_widget.setLayout(self.buttons_layout)
		self.main_layout.addWidget(self.buttons_widget)

		self.buttons_content_widget = QtWidgets.QWidget()
		self.buttons_content_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		self.buttons_content_widget.setObjectName('transparent_widget')
		self.buttons_content_layout = QtWidgets.QVBoxLayout()
		self.buttons_content_layout.setSpacing(3)
		self.buttons_content_layout.setContentsMargins(0,0,0,0)
		self.buttons_content_widget.setLayout(self.buttons_content_layout)
		self.buttons_layout.addWidget(self.buttons_content_widget)

		self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

		self.widgets_area = QtWidgets.QWidget()
		self.widgets_area.setObjectName('dark_widget')
		self.widgets_area_layout = QtWidgets.QHBoxLayout()
		self.widgets_area_layout.setContentsMargins(0,0,0,0)
		self.widgets_area.setLayout(self.widgets_area_layout)
		self.main_layout.addWidget(self.widgets_area)

	def addTab(self, widget, label, icon=''):
		index = len(self.tabs_dic.keys())
		button = tab_button(index, label, icon, 40)
		button.select_signal.connect(self.tab_selected)
		self.buttons_content_layout.addWidget(button)
		self.widgets_area_layout.addWidget(widget)
		widget.setVisible(0)
		self.tabs_dic[index] = dict()
		self.tabs_dic[index]['widget'] = widget
		self.tabs_dic[index]['button'] = button
		if index == 0:
			self.tab_selected(index)
		return index

	def tab_selected(self, index):
		for tab_index in self.tabs_dic.keys():
			if tab_index != index:
				self.tabs_dic[tab_index]['button'].setChecked(False)
				self.tabs_dic[tab_index]['widget'].setVisible(0)
		self.tabs_dic[index]['button'].setChecked(True)
		self.tabs_dic[index]['widget'].setVisible(1)
		self.index = index

	def current_index(self):
		return self.index

class tab_button(QtWidgets.QPushButton):

	select_signal = pyqtSignal(int)

	def __init__(self, index, label, icon, size, parent=None):
		super(tab_button, self).__init__(parent)
		self.index = index
		self.setFixedHeight(size)
		self.setObjectName('round_tab_button')
		self.setIcon(QtGui.QIcon(icon))
		if label == '':
			self.setFixedWidth(size)
		self.setText(label)
		self.setCheckable(True)
		self.connect_functions()

	def connect_functions(self):
		self.clicked.connect(self.emit_index)

	def emit_index(self):
		self.select_signal.emit(self.index)	
