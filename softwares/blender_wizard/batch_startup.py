# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json
logger = logging.getLogger(__name__)

# Wizard modules
from blender_wizard import wizard_plugin
from blender_wizard import wizard_tools
from blender_wizard.export import modeling

wizard_tools.trigger_after_scene_openning_hook()

# read_settings
if 'wizard_json_settings' in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    frange = settings_dic['frange']
    refresh_assets = settings_dic['refresh_assets']
    nspace_list = settings_dic['nspace_list']
    stage_name = settings_dic['stage_to_export']

    if stage_name == 'modeling':
        modeling.main()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

else:
    logger.error("Batch settings not found")
