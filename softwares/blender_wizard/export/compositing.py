# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from blender_wizard import wizard_export
from blender_wizard import wizard_render
import wizard_communicate

def main(render_type, frange, farm=0):
    scene = wizard_export.save_or_save_increment()
    try:
        if render_type in ['FML', 'LD', 'HD']:

            export_name = "compositing_{0}".format(render_type)

            wizard_render.setup_frame_range(render_type, frange)
            wizard_render.setup_image_format(render_type)
            
            string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            exported_string_asset = string_asset

            if wizard_export.trigger_sanity_hook('compositing', exported_string_asset):
                wizard_export.trigger_before_export_hook('compositing', exported_string_asset)
                compositing_directory = wizard_render.setup_compositing_directory('compositing', export_name)
                wizard_export.trigger_after_export_hook('compositing', compositing_directory, exported_string_asset)
                if not farm:
                    batch()
        else:
            logger.warning("Unkown render type : {0}".format(render_type))
    except:
        logger.error(str(traceback.format_exc()))

def setup_compositing_directory(render_type, frange):
    if render_type in ['FML', 'LD', 'HD']:
        export_name = "compositing_{0}".format(render_type)
        compositing_directory = wizard_render.setup_compositing_directory('compositing', export_name)
        wizard_render.setup_frame_range(render_type, frange)
        wizard_render.setup_image_format(render_type)
        return compositing_directory

def batch():
    bpy.ops.render.render(animation=True, use_viewport=True)
