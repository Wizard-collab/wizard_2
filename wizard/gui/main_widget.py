# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import time

# Wizard modules
from wizard.core import communicate
from wizard.core import custom_logger
logger = custom_logger.get_logger()

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import tree_widget
from wizard.gui import versions_widget
from wizard.gui import exports_widget
from wizard.gui import tabs_widget
from wizard.gui import launcher_widget
from wizard.gui import wall_widget
from wizard.gui import user_widget
from wizard.gui import quotes_widget
from wizard.gui import shelf_widget
from wizard.gui import logging_widget

class main_widget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(main_widget, self).__init__(parent)
		self.tree_widget = tree_widget.tree_widget(self)
		self.launcher_widget = launcher_widget.launcher_widget(self)
		self.versions_widget = versions_widget.versions_widget(self)
		self.exports_widget = exports_widget.exports_widget(self)
		self.tabs_widget = tabs_widget.tabs_widget(self)
		self.wall_widget = wall_widget.wall_widget(self)
		self.user_widget = user_widget.user_widget(self)
		self.quotes_widget = quotes_widget.quotes_widget(self)
		self.shelf_widget = shelf_widget.shelf_widget(self)
		self.logging_widget = logging_widget.logging_widget(self)
		self.build_ui()
		self.init_gui_server()
		self.init_communicate_server()
		self.connect_functions()
		self.init_contexts()

	def init_gui_server(self):
		self.gui_server = gui_server.gui_server()
		self.gui_server.start()

	def init_communicate_server(self):
		self.communicate_server = communicate.communicate_server()
		self.communicate_server.start()

	def init_contexts(self):
		self.tree_widget.get_context()

	def connect_functions(self):
		self.tree_widget.stage_changed_signal.connect(self.stage_changed)
		self.launcher_widget.work_env_changed_signal.connect(self.work_env_changed)
		self.launcher_widget.variant_changed_signal.connect(self.variant_changed)
		self.gui_server.refresh_signal.connect(self.refresh)
		self.versions_widget.version_changed_signal.connect(self.launcher_widget.focus_version)
		self.tabs_widget.currentChanged.connect(self.tab_changed)

	def stage_changed(self, stage_id):
		self.launcher_widget.change_stage(stage_id)

	def variant_changed(self, variant_id):
		self.exports_widget.change_variant(variant_id)

	def work_env_changed(self, work_env_id):
		self.versions_widget.change_work_env(work_env_id)

	def tab_changed(self):
		self.versions_widget.refresh()
		self.exports_widget.refresh()

	def refresh(self):
		start_time = time.time()
		start_tree = time.time()
		self.tree_widget.refresh()
		logger.info(f"Refresh tree : {str(time.time()-start_tree)}")
		start_launcher = time.time()
		self.launcher_widget.refresh()
		logger.info(f"Refresh launcher : {str(time.time()-start_launcher)}")
		start_user = time.time()
		self.user_widget.refresh()
		logger.info(f"Refresh user : {str(time.time()-start_user)}")
		start_wall = time.time()
		self.wall_widget.refresh()
		logger.info(f"Refresh wall : {str(time.time()-start_wall)}")
		start_versions = time.time()
		self.versions_widget.refresh()
		logger.info(f"Refresh versions : {str(time.time()-start_versions)}")
		start_exports = time.time()
		self.exports_widget.refresh()
		logger.info(f"Refresh exports : {str(time.time()-start_exports)}")
		logger.info(f"Refresh time : {str(time.time()-start_time)}")

	def build_ui(self):
		self.setObjectName('main_widget')
		self.main_layout = QtWidgets.QVBoxLayout()
		self.main_layout.setSpacing(2)
		self.main_layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.main_layout)

		self.contents_widget = QtWidgets.QWidget()
		self.contents_widget.setObjectName('main_widget')
		self.contents_layout = QtWidgets.QHBoxLayout()
		self.contents_layout.setSpacing(2)
		self.contents_layout.setContentsMargins(0,0,0,0)
		self.contents_widget.setLayout(self.contents_layout)
		self.main_layout.addWidget(self.contents_widget)

		self.contents_layout.addWidget(self.tree_widget)

		self.contents_1_widget = QtWidgets.QWidget()
		self.contents_1_widget.setObjectName('main_widget')
		self.contents_1_layout = QtWidgets.QVBoxLayout()
		self.contents_1_layout.setSpacing(2)
		self.contents_1_layout.setContentsMargins(0,0,0,0)
		self.contents_1_widget.setLayout(self.contents_1_layout)
		self.contents_layout.addWidget(self.contents_1_widget)

		self.header_widget = QtWidgets.QWidget()
		self.header_widget.setObjectName('main_widget')
		self.header_layout = QtWidgets.QHBoxLayout()
		self.header_layout.setSpacing(2)
		self.header_layout.setContentsMargins(0,0,0,0)
		self.header_widget.setLayout(self.header_layout)
		self.contents_1_layout.addWidget(self.header_widget)
		self.contents_1_layout.addWidget(self.shelf_widget)

		self.header_layout.addWidget(self.user_widget)
		self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
		#self.header_layout.addWidget(self.quotes_widget)

		self.contents_2_widget = QtWidgets.QWidget()
		self.contents_2_widget.setObjectName('main_widget')
		self.contents_2_layout = QtWidgets.QHBoxLayout()
		self.contents_2_layout.setSpacing(2)
		self.contents_2_layout.setContentsMargins(0,0,0,0)
		self.contents_2_widget.setLayout(self.contents_2_layout)
		self.contents_1_layout.addWidget(self.contents_2_widget)

		#self.contents_2_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
		self.contents_2_layout.addWidget(self.tabs_widget)
		self.tabs_widget.addTab(self.versions_widget, 'Work versions')
		self.tabs_widget.addTab(self.exports_widget, 'Exports')
		self.contents_2_layout.addWidget(self.launcher_widget)
		
		#self.contents_layout.addWidget(self.wall_widget)

		self.main_layout.addWidget(self.logging_widget)
