import test
from wizard.gui import app_utils
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import datetime
import time
import random
from wizard.core import project
from wizard.vars import ressources

class calendar_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendar_widget, self).__init__(parent)

        self.resize(800, 600)

        self.header_view = test.calendar_header()
        self.view = test.calendar_viewport()

        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.header_view)
        self.main_layout.addWidget(self.view)

       	for a in range(50):
	        domains = project.get_domains()
	        for category_row in project.get_domain_childs(domains[0]['id']):
	        	assets = project.get_category_childs(category_row['id'])
	        	for asset_row in assets:
	        		stages = project.get_asset_childs(asset_row['id'])
			        for stage_row in stages:
			            item = stage_item(stage_row, datetime.datetime(2023, 12, random.randint(5,25)),
			            					random.randint(1, 10),
			            					bg_color = ressources._stages_colors_[stage_row['name']])
			            self.view.add_item(item)

class stage_item(test.calendar_item):
    def __init__(self, stage_row, date, duration, bg_color):
        super(stage_item, self).__init__(date=date, duration=duration, bg_color=bg_color)
        self.stage_row = stage_row

    def paint(self, painter, option, widget):
    	super(stage_item, self).paint(painter, option, widget)
    	rect = self.boundingRect().toRect()
    	text_rect = QtCore.QRect(rect.x(), rect.y(), rect.width()-43, rect.height())
    	test.draw_text(painter, text_rect, self.stage_row['string'], size=6)
    	state_rect = QtCore.QRect(rect.width()-39, rect.y()+4, 25, rect.height()-8)
    	test.draw_rect(painter, state_rect, bg_color=QtGui.QColor(ressources._states_colors_[self.stage_row['state']]), radius=2)
    	test.draw_text(painter, state_rect, self.stage_row['state'], size=6)


w= calendar_widget()
w.show()
