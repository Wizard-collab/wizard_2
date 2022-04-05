# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        if wizard_tools.check_obj_list_existence(['custom_GRP']):
            custom_GRP_node = pm.PyNode('custom_GRP')
            asset_name = os.environ['wizard_asset_name']
            custom_GRP_node.rename(asset_name)
            export_GRP_list = [asset_name]

            additionnal_objects = wizard_export.trigger_before_export_hook('custom')
            export_GRP_list += additionnal_objects

            wizard_export.export('custom', export_name, export_GRP_list)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
