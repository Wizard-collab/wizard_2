# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger('batch_startup')

# Wizard modules
from guerilla_render_wizard import wizard_plugin
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard.export import shading
from guerilla_render_wizard.export import custom
from guerilla_render_wizard.export import lighting

wizard_tools.trigger_after_scene_openning_hook()

def main():
    # Checking settings dic existence
    if 'WIZARD_JSON_SETTINGS' not in os.environ.keys():
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
    logger.info("Batch type : {0}".format(settings_dic['batch_type']))
    if settings_dic['batch_type'] == 'video':
        if 'frange' not in settings_dic.keys():
            logger.error("frange parameter not found")
            return
        if 'nspace_list' not in settings_dic.keys():
            logger.error("nspace_list parameter not found")
            return
        logger.warning("Video not plugged for guerilla render. Quitting")
        return
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
        if stage_name == 'shading':
            shading.main(comment=comment)
        elif stage_name == 'custom':
            custom.main(comment=comment)
        elif stage_name == 'lighting':
            if 'render_type' not in settings_dic.keys():
                logger.error("render_type parameter not found")
                return
            if 'farm' not in settings_dic.keys():
                logger.error("farm parameter not found")
                return
            render_type = settings_dic['render_type']
            farm = settings_dic['farm']
            lighting.main(settings_dic['render_type'],
                            settings_dic['frange'],
                            settings_dic['farm'])
        else:
            logger.warning("Unplugged stage : {}".format(stage_name))
            return

main()
logger.info("Quitting batch")