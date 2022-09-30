# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
import json

logger = logging.getLogger('batch_startup')

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_plugin
from nuke_wizard import wizard_tools
from nuke_wizard.export import compositing
from nuke_wizard.export import custom

# Nuke modules
import nuke

# Open version file
nuke.scriptOpen(wizard_communicate.get_file(os.environ['wizard_version_id']))

wizard_tools.trigger_after_scene_openning_hook()

def main():
    # Checking settings dic existence
    if 'wizard_json_settings' not in os.environ.keys():
        logger.error("Batch settings dic not found")
        return
    settings_dic = json.loads(os.environ['wizard_json_settings'])
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
        logger.warning("Video not plugged for nuke. Quitting")
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
        if stage_name == 'compositing':
            compositing.main(frange=settings_dic['frange'])
        elif stage_name == 'custom':
            custom.main()
        else:
            logger.warning("Unplugged stage : {}".format(stage_name))
            return
main()
logger.info("Quitting batch")
