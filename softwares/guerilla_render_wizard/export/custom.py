# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        export_GRP = 'custom_GRP'
        if wizard_tools.check_obj_list_existence([export_GRP]):
            export_GRP_node = wizard_tools.get_node_from_name(export_GRP)
            asset_name = os.environ['wizard_asset_name']
            export_GRP_node.rename(asset_name)
            wizard_export.export('custom', export_name, [asset_name])
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
