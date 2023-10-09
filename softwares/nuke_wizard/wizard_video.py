# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Nuke modules
import nuke

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_tools

def invoke_settings_widget(*args):
    from wizard_widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == video_settings_widget.dialog_accepted:
        frange = video_settings_widget_win.frange
        nspace_list = video_settings_widget_win.nspace_list
        create_video(frange)

def create_video(frange, comment=''):
    directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
    logger.info("Creating video files at {}...".format(directory))
    if not export_pngs(directory, frange, comment=comment):
        return

def after_render(directory, frange, video_node, comment=''):
    wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory, frange, int(os.environ['wizard_version_id']), comment=comment)
    nuke.removeAfterRender(after_render, args=(directory, frange, video_node))
    nuke.removeAfterFrameRender(wizard_tools.by_frame_progress, args=(frange))
    nuke.delete(video_node)

def export_pngs(directory, frange, comment=''):
    image_format = wizard_communicate.get_image_format()

    viewer = get_viewer()
    if not viewer:
        return

    video_node = create_write_node(viewer)
    file = f"{directory}/tmp_%04d.png"
    video_node['file'].setValue(file)
    video_node.knob('afterRender')
    nuke.addAfterRender(after_render, args=(directory, frange, video_node, comment))
    nuke.addAfterFrameRender(wizard_tools.by_frame_progress, args=(frange))
    nuke.execute(video_node, frange[0], frange[1], 1)

def get_viewer():
    # Look for viewer
    for node in wizard_tools.get_all_nodes():
        if node.Class() == 'Viewer':
            if node.inputs() > 0:
                return node
    logger.warning("No viewer with input found")
    return

def create_write_node(viewer):
    write_node = nuke.nodes.Write(name="wizard_video_write")
    for i in range(viewer.inputs()):
        write_node.setInput(i, viewer.input(i))
    return write_node