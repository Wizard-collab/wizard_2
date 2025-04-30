# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
import os

pythonpath_env = os.getenv('PYTHONPATH')  # noqa
if pythonpath_env:  # noqa
    for path in pythonpath_env.split(os.pathsep):  # noqa
        if path not in sys.path:  # noqa
            sys.path.append(path)  # noqa

# Wizard modules
from blender_wizard import wizard_tools
from blender_wizard import wizard_menu

wizard_menu.register()
wizard_tools.trigger_after_scene_openning_hook()
