# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Guerilla modules
import guerilla

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export
from guerilla_render_wizard import wizard_render
import wizard_communicate

def main(render_type, frange, farm=0):
    scene = wizard_export.save_or_save_increment()
    try:
        if render_type in ['FML', 'LD', 'HD']:

            export_name = "render_{0}".format(render_type)

            wizard_render.setup_frame_range(render_type, frange)
            wizard_render.setup_image_format(render_type)
            
            string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            exported_string_asset = string_asset

            if wizard_export.trigger_sanity_hook('lighting', exported_string_asset):
                wizard_export.trigger_before_export_hook('lighting', exported_string_asset)
                render_directory = wizard_render.setup_render_directory('lighting', export_name)
                wizard_export.trigger_after_export_hook('lighting', render_directory, exported_string_asset)
                if not farm:
                    batch()
                else:
                    deadline()
        else:
            logger.warning("Unkown render type : {0}".format(render_type))
    except:
        logger.error(str(traceback.format_exc()))

def setup_render_directory(render_type, frange):
    if render_type in ['FML', 'LD', 'HD']:
        export_name = "render_{0}".format(render_type)
        render_directory = wizard_render.setup_render_directory('lighting', export_name)
        wizard_render.setup_frame_range(render_type, frange)
        wizard_render.setup_image_format(render_type)
        return render_directory

def batch():
    guerilla.render('batch', None)

def deadline():
    settings_dic = dict()
    settings_dic['Name'] = "test"
    settings_dic['DeferredRibGen '] = True
    guerilla.render('farm', settings_dic)