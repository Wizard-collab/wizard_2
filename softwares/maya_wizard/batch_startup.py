# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger(__name__)

# Wizard modules
from maya_wizard import wizard_plugin
from maya_wizard.export import modeling
from maya_wizard.export import rigging
from maya_wizard.export import grooming
from maya_wizard.export import custom
from maya_wizard.export import camrig
from maya_wizard.export import layout
from maya_wizard.export import animation
from maya_wizard.export import cfx
from maya_wizard.export import camera

# read_settings
if 'wizard_json_settings'.upper() in os.environ.keys():
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    frange = settings_dic['frange']
    refresh_assets = settings_dic['refresh_assets']
    nspace_list = settings_dic['nspace_list']
    stage_name = settings_dic['stage_to_export']

    if refresh_assets:
        wizard_plugin.update_all()

    if stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'rigging':
        rigging.main()
    elif stage_name == 'grooming':
        grooming.main()
    elif stage_name == 'custom':
        custom.main()
    elif stage_name == 'camrig':
        camrig.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'animation':
        animation.main(nspace_list=nspace_list,
                            frange=frange)
    elif stage_name == 'cfx':
        cfx.main(nspace_list=nspace_list,
                            frange=frange)
    elif stage_name == 'camera':
        camera.main(nspace_list=nspace_list,
                            frange=frange)
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

else:
    logger.error("Batch settings not found")
