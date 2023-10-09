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
from houdini_wizard import wizard_tools

def invoke_settings_widget():
    from wizard_widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == video_settings_widget.dialog_accepted:
        frange = video_settings_widget_win.frange
        nspace_list = video_settings_widget_win.nspace_list
        create_videos(frange, nspace_list)

def create_videos(frange, nspace_list, comment=''):
    if nspace_list == []:
        camera = get_default_camera()
        create_video(frange, camera, comment=comment)
        return
    for nspace in nspace_list:
        camera = select_cam(nspace)
        if not camera:
            logger.warning(f"Skipping video for {nspace}, camera not found")
        else:
            create_video(frange, camera, comment=comment)

def create_video(frange, camera, comment=''):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Flipbooking at {}...".format(directory))
    focal_lengths_dic = get_focal_length(frange, camera)
    logger.info(focal_lengths_dic)
    flipbook(directory, frange, camera, focal_lengths_dic, comment=comment)

def get_focal_length(frange, camera):
    focal_lengths_dic = dict()
    for frame in range(frange[0], frange[1]+1):
        hou.setFrame(frame)
        camera_node = hou.node("/obj").node(camera)
        focal_lengths_dic[frame] = round(camera_node.parm("focal").eval(), 1)
    return focal_lengths_dic

def publish_video_script(directory, frange, focal_lengths_dic, comment=''):
    command = """import wizard_communicate\n"""
    command += """import os\n"""
    command += f"""wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), "{directory}", {frange}, int(os.environ['wizard_version_id']), focal_lengths_dic={focal_lengths_dic}, comment="{comment}")"""
    return command

def progress_script(frange):
    command = "import hou\n"
    command+= "frame=hou.frame()\n"
    command+= f"inframe={frange[0]}\n"
    command+= f"outframe={frange[0]}\n"
    command+= "percent=(frame-inframe)/(outframe-inframe)\n"
    command+= 'print("wizard_task_percent:{}".format(percent))\n'
    return command

def flipbook(directory, frange, camera, focal_lengths_dic, comment=''):
    image_format = wizard_communicate.get_image_format()
    file = os.path.join(directory, "tmp_flipbook.$F4.png")
    opengl_node = create_rop_network()
    logger.info(f"Creating video trough {camera}")

    hou.playbar.setFrameRange(frange[0], frange[1])
    opengl_node.parm('camera').set(camera)
    opengl_node.parm('trange').set("normal")
    opengl_node.parm('f1').set(frange[0])
    opengl_node.parm('f2').set(frange[1])
    opengl_node.parm('scenepath').set('/obj')
    opengl_node.parm('picture').set(file)
    opengl_node.parm('lpostframe').set("python")
    opengl_node.parm('postframe').set(wizard_tools.by_frame_progress_script())
    opengl_node.parm('lpostrender').set("python")
    opengl_node.parm('postrender').set(publish_video_script(directory, frange, focal_lengths_dic, comment=comment))
    opengl_node.parm('execute').pressButton()

def get_default_camera():
    logging.info("Looking for an existing camera in scene.")
    obj_node = hou.node("/obj")
    for node in obj_node.allSubChildren():
        if node.type().name() == 'cam':
            logger.info(f"Camera found, {node.path()}")
            return node.path()
    logging.info("No camera found, creating a camera.")
    cam_node = obj_node.createNode("cam", "wizard_flipbook_default_cam")
    return cam_node.path()

def create_rop_network():
    obj_node = hou.node("/obj")
    opengl_node = wizard_tools.look_for_node('wizard_opengl_flipbook', parent=obj_node)
    if opengl_node is not None:
        return opengl_node
    rop_network = obj_node.createNode("ropnet", "wizard_rop_flipbook")
    opengl_node = rop_network.createNode("opengl", "wizard_opengl_flipbook")
    return opengl_node

def select_cam(nspace):
    obj_node = hou.node("/obj")
    nspace_node = wizard_tools.look_for_node(nspace, parent=obj_node)
    if not nspace_node:
        logger.warning(f"{nspace} not found.")
        return
    for node in nspace_node.allSubChildren():
        if node.type().name() == 'cam':
            logger.info(f"Camera found, {node.path()}")
            return node.path()
