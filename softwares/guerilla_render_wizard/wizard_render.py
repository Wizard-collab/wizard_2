# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Guerilla modules
import guerilla
from guerilla import Document, pynode, Modifier

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export

def __init__():
    pass

def setup_render_directory(stage_name, export_name):
    render_directory = wizard_communicate.request_render(int(os.environ['wizard_version_id']),
                                                        export_name)
    if render_directory:
        file_pattern = "$L_$n_$o.$05f.$x"
        render_pass_list = wizard_tools.get_all_render_passes()
        for render_pass in render_pass_list:
            render_pass.FileName.set(os.path.join(render_directory, file_pattern))
        return render_directory

def setup_frame_range(render_type, frame_range=None):
    if not frame_range:
        frame_range = wizard_communicate.get_frame_range(os.environ['wizard_work_env_id'])
    if render_type == 'FML':
        frames = "{0},{1},{2}".format(frame_range[1], int((frame_range[1]+frame_range[2])/2), frame_range[2])
    elif render_type == 'HD' or render_type == 'LD':
        frames = "{0}-{1}".format(frame_range[1], frame_range[2])
    else:
        logger.info("Unkown render type : {0}".format(render_type))
        frames = None
    if frames is not None:
        with Modifier() as mod: 
            preferences_node = wizard_tools.get_node_from_name('Preferences')
            preferences_node.RenderRange.set(frames)

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
        width=float(image_format[0])
        height=float(image_format[1])
        Document().ProjectWidth.set(width)
        Document().ProjectHeight.set(height)
        Document().ProjectAspectRatio.set(1)

def setup_FML():
    setup_frame_range('FML')
    setup_image_format('FML')

def setup_HD():
    setup_frame_range('HD')
    setup_image_format('HD')

def setup_LD():
    setup_frame_range('LD')
    setup_image_format('LD')