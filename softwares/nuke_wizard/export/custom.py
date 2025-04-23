# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_export

logger = logging.getLogger(__name__)


def main(comment=''):
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(
            int(os.environ['wizard_work_env_id']))
        wizard_export.trigger_before_export_hook(
            'custom', exported_string_asset)
        wizard_export.export('custom', export_name,
                             exported_string_asset, comment=comment)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
