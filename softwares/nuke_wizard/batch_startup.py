# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_plugin
from nuke_wizard import wizard_tools
from nuke_wizard.export import compositing

# Nuke modules
import nuke

# Open version file
nuke.scriptOpen(wizard_communicate.get_file(os.environ['wizard_version_id']))

wizard_tools.trigger_after_scene_openning_hook()

# read_settings
if 'wizard_json_settings' in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    frange = settings_dic['frange']
    refresh_assets = settings_dic['refresh_assets']
    stage_name = settings_dic['stage_to_export']

    if refresh_assets:
        wizard_plugin.update_all()

    if stage_name == 'compositing':
        compositing.main(frange=frange)
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

else:
    logger.error("Batch settings not found")
