# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
from PySide2 import QtWidgets, QtGui

# Substance Designer modules
import sd

# Wizard modules
from substance_designer_wizard import wizard_plugin

def wizard_menu():
	# Get the application and the UI Manager.
	app = sd.getContext().getSDApplication()
	uiMgr = app.getQtForPythonUIMgr()

	wizard_menu = uiMgr.newMenu(menuTitle="Wizard", objectName="wizard")
	save_invcrement_action = QtWidgets.QAction(QtGui.QIcon("icons/save_increment.png"), "Save", wizard_menu)
	save_invcrement_action.triggered.connect(wizard_plugin.save)
	wizard_menu.addAction(save_invcrement_action)
	export_action = QtWidgets.QAction(QtGui.QIcon("icons/export.png"), "Export data", wizard_menu)
	export_action.triggered.connect(wizard_plugin.export)
	wizard_menu.addAction(export_action)
	wizard_menu.addSeparator()
	init_scene_action = QtWidgets.QAction(QtGui.QIcon("icons/all.png"), "Init scene", wizard_menu)
	init_scene_action.triggered.connect(wizard_plugin.init_scene)
	wizard_menu.addAction(init_scene_action)

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
	wizard_menu()

# If this function is present in your plugin,
# it will be called by Designer when unloading the plugin.
def uninitializeSDPlugin():
	pass
