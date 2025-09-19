# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Blender modules
import bpy

# Wizard modules
import wizard_communicate

logger = logging.getLogger(__name__)


def __init__():
    pass


def setup_render_directory(stage_name, export_name):
    if os.environ['wizard_stage_name'] == 'rendering':
        rendering_work_env_id = int(os.environ['wizard_work_env_id'])
    else:
        rendering_work_env_id = wizard_communicate.create_or_get_rendering_work_env(
            int(os.environ['wizard_work_env_id']))
    render_directory = wizard_communicate.request_render(int(os.environ['wizard_version_id']),
                                                         rendering_work_env_id,
                                                         export_name)

    if render_directory:
        extension = wizard_communicate.get_export_format(rendering_work_env_id)
        file_name = f"{os.environ['wizard_asset_name']}_{os.environ['wizard_stage_name']}"
        file_path = f"{render_directory}/{file_name}.####.{extension}"
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        return render_directory

def setup_compositing_directory(stage_name, export_name):
    compositing_work_env_id = int(os.environ['wizard_work_env_id'])
    compositing_directory = wizard_communicate.request_render(int(os.environ['wizard_version_id']),
                                                         compositing_work_env_id,
                                                         export_name)

    if compositing_directory:
        extension = wizard_communicate.get_export_format(compositing_work_env_id)
        file_name = f"{os.environ['wizard_asset_name']}_{os.environ['wizard_stage_name']}"
        file_path = f"{compositing_directory}/{file_name}.####.{extension}"
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"
        return compositing_directory


def setup_frame_range(render_type, frame_range=None):
    if not frame_range:
        frame_range = wizard_communicate.get_frame_range(
            os.environ['wizard_work_env_id'])
    if render_type == 'FML':
        frame_step = int((frame_range[2] - frame_range[1])/2)
    elif render_type == 'HD' or render_type == 'LD':
        frame_step = 1
    else:
        logger.info("Unkown render type : {0}".format(render_type))
        frame_step = 1
    bpy.context.scene.frame_start = frame_range[1]
    bpy.context.scene.frame_end = frame_range[2]
    bpy.context.scene.frame_step = frame_step


def setup_image_format(render_type):
    image_format = wizard_communicate.get_image_format()
    if render_type == 'LD':
        image_format = [int(image_format[0]/2), int(image_format[1]/2)]
    elif render_type == 'HD' or render_type == 'FML':
        pass
    else:
        logger.info("Unkown render type : {0}".format(render_type))
        image_format = None

    if image_format:
        bpy.context.scene.render.resolution_x = image_format[0]
        bpy.context.scene.render.resolution_y = image_format[1]


def setup_FML():
    setup_frame_range('FML')
    setup_image_format('FML')


def setup_HD():
    setup_frame_range('HD')
    setup_image_format('HD')


def setup_LD():
    setup_frame_range('LD')
    setup_image_format('LD')
