# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

import sys
import os 

pythonpath_env = os.getenv('PYTHONPATH')
if pythonpath_env:
    for path in pythonpath_env.split(os.pathsep):
        if path not in sys.path:
            sys.path.append(path)
            
# Wizard modules
from blender_wizard import wizard_menu
from blender_wizard import wizard_tools

wizard_menu.register()
wizard_tools.trigger_after_scene_openning_hook()