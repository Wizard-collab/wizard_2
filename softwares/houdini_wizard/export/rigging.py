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
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_export

# Houdini modules

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
        wizard_export.trigger_before_export_hook('rigging', exported_string_asset)
        wizard_export.export(stage_name='rigging', export_name=export_name, exported_string_asset=exported_string_asset, out_node='wizard_rigging_output')
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
