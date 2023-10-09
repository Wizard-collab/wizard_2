# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Maya modules
import maya.cmds as cmds
import pymel.core as pm

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools

def invoke_settings_widget(*args):
    from wizard_widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget(wizard_tools.maya_main_window())
    if video_settings_widget_win.exec_() == video_settings_widget.dialog_accepted:
        frange = video_settings_widget_win.frange
        nspace_list = video_settings_widget_win.nspace_list
        create_videos(frange, nspace_list)

def create_videos(frange, nspace_list):
    if nspace_list == []:
        camera = select_default_cam()
        if not camera:
            logger.warning(f"No camera found.")
            return
        create_video(frange, camera)
        return
    for nspace in nspace_list:
        camera = select_cam(nspace)
        if not camera:
            logger.warning(f"Skipping video for {nspace}, camera not found")
            return
        create_video(frange, camera)

def create_video(frange, camera):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Playblasting at {}...".format(directory))
    playblast(directory, frange)
    focal_lengths_dic = get_focal_length(frange, camera)
    wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory, frange, int(os.environ['wizard_version_id']), focal_lengths_dic=focal_lengths_dic)

def get_focal_length(frange, camera):
    focal_lengths_dic = dict()
    for frame in range(frange[0], frange[1]+1):
        pm.currentTime(frame)
        focal_lengths_dic[frame] = round(pm.getAttr(camera+'.focalLength'), 1)
    return focal_lengths_dic

def playblast(directory, frange):
    image_format = wizard_communicate.get_image_format()
    file = os.path.join(directory, 'tmp_playblast').replace('\\', '/')
    pm.colorManagementPrefs(e=True, outputTransformEnabled=True, outputTarget="renderer")
    cmds.playblast(st=frange[0], et=frange[1], p=100, f=file, wh=image_format, qlt= 100, fp= 4, fmt='image', compression='png', fo=1, v=False)

def select_cam(nspace):
    camera_shape = list_cam(nspace)
    if camera_shape is None:
        return
    set_cam_as_renderable(camera_shape)
    logger.info(f"Creating video trough {camera_shape}")
    return camera_shape

def select_default_cam():
    perspCameras = pm.listCameras( p=True )
    if len(perspCameras) > 1:
        perspCameras.remove('persp')
    camera = perspCameras[0]
    set_cam_as_renderable(camera)
    logger.info(f"No namespace given, creating video trough {camera}")
    return camera

def set_cam_as_renderable(camera_to_ren):
    cameras = pm.ls(type='camera')
    for camera in cameras:
        pm.setAttr(camera + '.rnd', 0)
    pm.setAttr(camera_to_ren + '.rnd', 1)
    try:
        pm.lookThru(camera_to_ren)
    except:
        pass

def list_cam(nspace):
    render_set = "{}:render_set".format(nspace)
    if not pm.objExists(render_set):
        logger.info("{} not found, looking for a camera in the reference.".format(render_set))
        objects = pm.namespaceInfo(nspace, ls=True)
    else:
        objects = pm.sets(render_set, q=True)
        if len(objects) == 0:
            logger.warning("{} is empty".format(render_set))
            return
    for obj in objects:
        cameras_shapes = pm.listRelatives(obj, type='camera')
        if len(cameras_shapes) == 1:
            logger.info(f"Camera found, {cameras_shapes[0]}")
            return cameras_shapes[0]
