# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate

def invoke_settings_widget():
    from PySide2 import QtWidgets, QtCore, QtGui
    from houdini_wizard.widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        frange = video_settings_widget_win.frange
        create_video(frange)

def create_video(frange):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Flipbooking at {}...".format(directory))
    flipbook(directory, frange)
    #wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory)

def flipbook(directory, frange):
    image_format = wizard_communicate.get_image_format()
    file = os.path.join(directory, "tmp_flipbook.$F4.png")

    opengl_node = create_rop_network()
    #cam_path = get_cam_path(namespace)
    opengl_node.parm('camera').set(create_default_camera())
    opengl_node.parm('trange').set("normal")
    opengl_node.parm('f1').set(frange[0])
    opengl_node.parm('f2').set(frange[1])
    opengl_node.parm('scenepath').set('/obj')
    opengl_node.parm('picture').set(file)
    opengl_node.parm('execute').pressButton()

def create_default_camera():
    obj_node = hou.node("/obj")
    cam_node = obj_node.createNode("cam", "wizard_flipbook_default_cam")
    return cam_node.path()

def create_rop_network():
    obj_node = hou.node("/obj")
    rop_network = obj_node.createNode("ropnet", "wizard_rop_flipbook")
    opengl_node = rop_network.createNode("opengl", "wizard_opengl_flipbook")
    return opengl_node