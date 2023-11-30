# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging

# Wizard modules
import wizard_communicate
from substance_designer_wizard import wizard_export
from substance_designer_wizard import wizard_tools

# Substance designer modules
import sd

logger = logging.getLogger(__name__)
ctx = sd.getContext()
logger.addHandler(ctx.createRuntimeLogHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

def main():
    scene = wizard_tools.save()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(os.environ['wizard_work_env_id'])
        wizard_export.trigger_before_export_hook('texturing', exported_string_asset)
        wizard_export.export('texturing', export_name, exported_string_asset)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
