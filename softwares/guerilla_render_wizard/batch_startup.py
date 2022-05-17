# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_plugin
from guerilla_render_wizard.export import shading
from guerilla_render_wizard.export import custom
from guerilla_render_wizard.export import lighting

# read_settings
if 'WIZARD_JSON_SETTINGS' in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    frange = settings_dic['frange']
    refresh_assets = settings_dic['refresh_assets']
    stage_name = settings_dic['stage_to_export']

    if refresh_assets:
        wizard_plugin.update_all()

    if stage_name == 'shading':
        shading.main()
    elif stage_name == 'custom':
        custom.main()
    elif stage_name == 'lighting':
        render_type = settings_dic['render_type']
        farm = settings_dic['farm']
        lighting.main(render_type, frange, farm)
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

else:
    logger.error("Batch settings not found")
