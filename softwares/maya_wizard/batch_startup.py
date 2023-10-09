# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger('batch_startup')

# Wizard modules
from maya_wizard import wizard_plugin
from maya_wizard import wizard_tools
from maya_wizard import wizard_video
from maya_wizard.export import modeling
from maya_wizard.export import rigging
from maya_wizard.export import grooming
from maya_wizard.export import custom
from maya_wizard.export import camrig
from maya_wizard.export import layout
from maya_wizard.export import animation
from maya_wizard.export import fx
from maya_wizard.export import cfx
from maya_wizard.export import camera

wizard_tools.trigger_after_scene_openning_hook()

def main():
    # Checking settings dic existence
    if 'wizard_json_settings' not in os.environ.keys():
        logger.error("Batch settings dic not found")
        return
    settings_dic = json.loads(os.environ['wizard_json_settings'])
    comment=''
    if 'comment' in settings_dic.keys():
        comment = settings_dic['comment']
    if 'refresh_assets' in settings_dic.keys():
        if settings_dic['refresh_assets']:
            wizard_plugin.update_all()
    if 'batch_type' not in settings_dic.keys():
        logger.error("Batch type setting not found")
        return
    logger.info(f"Batch type : {settings_dic['batch_type']}")
    if settings_dic['batch_type'] == 'video':
        if 'frange' not in settings_dic.keys():
            logger.error("frange parameter not found")
            return
        if 'nspace_list' not in settings_dic.keys():
            logger.error("nspace_list parameter not found")
            return
        wizard_video.create_videos(settings_dic['frange'],
                                    settings_dic['nspace_list'])
    if settings_dic['batch_type'] == 'import_update_and_save':
        wizard_plugin.reference_and_update_all()
        wizard_plugin.save_increment(comment=comment)
    if settings_dic['batch_type'] == 'export':
        if 'frange' not in settings_dic.keys():
            logger.error("frange parameter not found")
            return
        if 'nspace_list' not in settings_dic.keys():
            logger.error("nspace_list parameter not found")
            return
        if 'stage_to_export' not in settings_dic.keys():
            logger.error("stage_to_export parameter not found")
            return
        stage_name = settings_dic['stage_to_export']
        if stage_name == 'modeling':
            modeling.main(comment=comment)
        elif stage_name == 'rigging':
            rigging.main(comment=comment)
        elif stage_name == 'grooming':
            grooming.main(comment=comment)
        elif stage_name == 'custom':
            custom.main(comment=comment)
        elif stage_name == 'camrig':
            camrig.main(comment=comment)
        elif stage_name == 'layout':
            layout.main(comment=comment)
        elif stage_name == 'animation':
            animation.main(nspace_list=settings_dic['nspace_list'],
                                frange=settings_dic['frange'],
                                comment=comment)
        elif stage_name == 'cfx':
            cfx.main(nspace_list=settings_dic['nspace_list'],
                                frange=settings_dic['frange'],
                                comment=comment)
        elif stage_name == 'fx':
            fx.main(frange=settings_dic['frange'])
        elif stage_name == 'camera':
            camera.main(nspace_list=settings_dic['nspace_list'],
                                frange=settings_dic['frange'],
                                comment=comment)
        else:
            logger.warning("Unplugged stage : {}".format(stage_name))
            return

main()
logger.info("Quitting batch")
