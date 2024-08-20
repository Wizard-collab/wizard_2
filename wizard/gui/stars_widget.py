# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources
from wizard.gui import gui_utils

class rate_widget(QtWidgets.QWidget):

	rate_signal = pyqtSignal(int)

	def __init__(self, parent=None):
		super(rate_widget, self).__init__(parent)
		self.image_bg = gui_utils.QIcon_from_svg(ressources._star_icon_, '#24242b').pixmap(12)
		self.image_hover = gui_utils.QIcon_from_svg(ressources._star_icon_, '#ffdb4a').pixmap(12)
		self.image_rate = gui_utils.QIcon_from_svg(ressources._star_icon_, '#e0a628').pixmap(12)
		self.stars_list = []
		self.rate = 0
		self.setMaximumSize(60, 12)
		self.setMinimumSize(60, 12)
		self.build_ui()
		self.connect_functions()

	def build_ui(self):	
		self.main_layout = QtWidgets.QHBoxLayout()
		self.main_layout.setContentsMargins(0,0,0,0)
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)

		self.star_1 = star_widget(self.image_bg, self.image_hover, index=1)
		self.main_layout.addWidget(self.star_1)
		self.stars_list.append(self.star_1)
		self.star_2 = star_widget(self.image_bg, self.image_hover, index=2)
		self.main_layout.addWidget(self.star_2)
		self.stars_list.append(self.star_2)
		self.star_3 = star_widget(self.image_bg, self.image_hover, index=3)
		self.main_layout.addWidget(self.star_3)
		self.stars_list.append(self.star_3)
		self.star_4 = star_widget(self.image_bg, self.image_hover, index=4)
		self.main_layout.addWidget(self.star_4)
		self.stars_list.append(self.star_4)
		self.star_5 = star_widget(self.image_bg, self.image_hover, index=5)
		self.main_layout.addWidget(self.star_5)
		self.stars_list.append(self.star_5)

	def update_stars_hover(self, index):
		if index == 0:
			index = self.rate
			image_hover = self.image_rate
		else:
			image_hover = self.image_hover
		for star in self.stars_list:
			if self.stars_list.index(star)+1 <= index:
				star.setPixmap(image_hover)
			else:
				star.setPixmap(self.image_bg)

	def connect_functions(self):
		for star in self.stars_list:
			star.hover_signal.connect(self.update_stars_hover)
			star.rate_signal.connect(self.apply_rate)

	def set_rate(self, rate):
		self.rate = int(rate)
		self.update_stars_hover(0)

	def apply_rate(self, index):
		self.rate_signal.emit(index)

class star_widget(QtWidgets.QLabel):

	hover_signal = pyqtSignal(int)
	rate_signal = pyqtSignal(int)

	def __init__(self, image_bg, image_hover, index, parent=None):
		super(star_widget, self).__init__(parent)
		self.index = index
		self.image_bg = image_bg
		self.image_hover = image_hover
		self.setMaximumSize(12, 12)
		self.setMinimumSize(12, 12)
		self.setPixmap(self.image_bg)

	def enterEvent(self, event):
		self.hover_signal.emit(self.index)

	def leaveEvent(self, event):
		self.hover_signal.emit(0)

	def mouseReleaseEvent(self, event):
		self.rate_signal.emit(self.index)