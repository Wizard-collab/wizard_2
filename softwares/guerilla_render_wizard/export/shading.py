# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
        export_name = 'main'
        export_GRP = 'shading_GRP'
        if wizard_tools.check_obj_list_existence([export_GRP]):
            export_GRP_node = wizard_tools.get_node_from_name(export_GRP)
            asset_name = os.environ['wizard_asset_name']
            export_GRP_node.rename(asset_name)
            additionnal_objects = wizard_export.trigger_before_export_hook('shading', exported_string_asset)
            export_objects_list = [asset_name]+additionnal_objects
            wizard_export.export('shading', export_name, exported_string_asset, export_objects_list)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)