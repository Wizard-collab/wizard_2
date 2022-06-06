# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_export

# Houdini modules


def main():
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        wizard_export.trigger_before_export_hook('custom')
        wizard_export.export(stage_name='custom', export_name=export_name, out_node='wizard_custom_output')
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
