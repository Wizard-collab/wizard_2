# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

from blender_wizard import wizard_tools
from blender_wizard import wizard_menu
import sys
import os

pythonpath_env = os.getenv('PYTHONPATH')
if pythonpath_env:
    for path in pythonpath_env.split(os.pathsep):
        if path not in sys.path:
            sys.path.append(path)

# Wizard modules

wizard_menu.register()
wizard_tools.trigger_after_scene_openning_hook()
