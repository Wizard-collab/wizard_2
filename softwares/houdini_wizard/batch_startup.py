# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger(__name__)

# Wizard modules
from houdini_wizard import wizard_plugin
from houdini_wizard import wizard_video
from houdini_wizard import wizard_tools
from houdini_wizard.export import modeling
from houdini_wizard.export import rigging
from houdini_wizard.export import custom
from houdini_wizard.export import layout
from houdini_wizard.export import cfx
from houdini_wizard.export import fx

wizard_tools.trigger_after_scene_openning_hook()

# read_settings
if 'wizard_json_settings' in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    frange = settings_dic['frange']
    refresh_assets = settings_dic['refresh_assets']
    nspace_list = settings_dic['nspace_list']

    if refresh_assets:
        wizard_plugin.update_all()

    if 'batch_type' in settings_dic.keys():
        if settings_dic['batch_type'] == 'video':
            wizard_video.create_video(frange)
        elif settings_dic['batch_type'] == 'export':
            stage_name = settings_dic['stage_to_export']
            if stage_name == 'modeling':
                modeling.main()
            elif stage_name == 'rigging':
                rigging.main()
            elif stage_name == 'custom':
                custom.main()
            elif stage_name == 'layout':
                layout.main()
            elif stage_name == 'cfx':
                cfx.main(nspace_list=nspace_list,
                                    frange=frange)
            elif stage_name == 'fx':
                fx.main(frange=frange)
            else:
                logger.warning("Unplugged stage : {}".format(stage_name))

else:
    logger.error("Batch settings not found")