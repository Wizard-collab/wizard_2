# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from blender_wizard import wizard_menu
from blender_wizard import wizard_tools

wizard_menu.register()
wizard_tools.trigger_after_scene_openning_hook()