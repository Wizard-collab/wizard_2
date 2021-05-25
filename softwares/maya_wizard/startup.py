import os

import maya
import maya.cmds as cmds
'''
from maya_wizard import shelf
from maya_wizard.menu import menu
from maya_wizard import reference_asset
from maya_wizard import scene_setup

from wizard.asset import main as asset_core
from wizard.vars import defaults

maya.utils.executeDeferred("init()")

def init():
	cmds.loadPlugin('AbcImport.mll')
	shelf.shelf('Wizard')
	menu()
	asset = asset_core.string_to_asset(os.environ[defaults._asset_var_])
	cmds.file(asset.file, o=True)
	reference_asset.import_all()
	scene_setup.set_f_range()
	scene_setup.setFormatToMaya()
'''
