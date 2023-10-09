# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_tools

def invoke_settings_widget(*args):
    from wizard_widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == video_settings_widget.dialog_accepted:
        frange = video_settings_widget_win.frange
        nspace_list = video_settings_widget_win.nspace_list
        create_videos(frange, nspace_list)

def create_videos(frange, nspace_list, comment=''):
    if nspace_list == []:
        camera = select_default_cam()
        if not camera:
            logger.warning(f"No camera found.")
            return
        create_video(frange, camera, comment=comment)
        return
    for nspace in nspace_list:
        camera = select_cam(nspace)
        if not camera:
            logger.warning(f"Skipping video for {nspace}, camera not found")
            return
        create_video(frange, camera, comment=comment)

def create_video(frange, camera, comment=''):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Playblasting at {}...".format(directory))
    bpy.context.scene.camera = camera
    playblast(directory, frange)
    focal_lengths_dic = get_focal_length(frange, camera)
    wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory, frange, int(os.environ['wizard_version_id']), focal_lengths_dic=focal_lengths_dic, comment=comment)

def get_focal_length(frange, camera):
    focal_lengths_dic = dict()
    for frame in range(frange[0], frange[1]+1):
        bpy.context.scene.frame_set(frame)
        focal_lengths_dic[frame] = round(camera.data.lens, 1)
    return focal_lengths_dic

def playblast(directory, frange):
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    temp_dir = os.path.join(directory, 'tmp_playblast').replace('\\', '/')
    bpy.context.scene.render.filepath = temp_dir
    # Set the resolution and frame range
    resolution = wizard_communicate.get_image_format()
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]
    bpy.context.scene.frame_start = frange[0]
    bpy.context.scene.frame_end = frange[1]
    bpy.ops.render.render(animation=True)

def select_cam(camrig_nspace):
    if not is_referenced(camrig_nspace):
        return
    namespace_collection = bpy.data.collections[camrig_nspace]
    render_set_collection = wizard_tools.get_render_set_collection(namespace_collection)
    if not render_set_collection:
        logger.warning("{}/render_set not found".format(camrig_nspace))
        return

    cameras = list(render_set_collection.all_objects)
    if len(cameras) == 0:
        logger.warning("{} is empty".format(render_set_collection))
        return
    if len(cameras) > 1:
        logger.warning("More than one camera found in {}, skipping".format(render_set_collection))
        return
    return cameras[0]

def is_referenced(camrig_nspace):
    if not wizard_tools.namespace_exists(camrig_nspace):
        logger.warning("{} not found in current scene".format(camrig_nspace))
        return
    return 1

def select_default_cam():
    default_camera = bpy.data.objects.get("Camera")
    if not default_camera:
        return
    logger.info(f"No namespace given, creating video trough {default_camera}")
    return default_camera
