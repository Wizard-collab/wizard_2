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

def invoke_settings_widget(*args):
    from PySide2 import QtWidgets, QtCore, QtGui
    from maya_wizard.widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        frange = video_settings_widget_win.frange
        nspace_list = video_settings_widget_win.nspace_list
        create_videos(frange, nspace_list)

def create_videos(frange, nspace_list):
    if nspace_list == []:
        logger.info("No camera namespace given, creating video from default scene camera.")
        create_video(frange)
        return
    for nspace in nspace_list:
        if not select_cam(nspace):
            logger.warning(f"Skipping video for {nspace}, camera not found")
        else:
            create_video(frange)

def create_video(frange):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Playblasting at {}...".format(directory))
    playblast(directory, frange)
    wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory, frange, int(os.environ['wizard_version_id']))

def playblast(directory, frange):
    image_format = wizard_communicate.get_image_format()
    file = os.path.join(directory, 'tmp_playblast').replace('\\', '/')
    cmds.playblast(st=frange[0], et=frange[1], p= 100, f=file, wh=image_format, qlt= 100, fp= 4, fmt='image', compression='png', fo=1, v=False)

def select_cam(nspace):
    camera_shape = list_cam(nspace)
    if camera_shape is None:
        return
    cameras = pm.ls(type='camera')
    for camera in cameras:
        pm.setAttr(camera + '.rnd', 0)
    pm.setAttr(camera_shape + '.rnd', 1)
    try:
        pm.lookThru(camera_shape)
    except:
        pass
    logger.info(f"Creating video trough {camera_shape}")
    return True

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
