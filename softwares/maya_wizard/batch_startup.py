# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import json

# Wizard modules
from maya_wizard import wizard_plugin

process = True
if 'wizard_json_settings' in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    if 'camera' in settings_dic.keys():
        wizard_plugin.export_camera()
        process = False

wizard_plugin.export()
