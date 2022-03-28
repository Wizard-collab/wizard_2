# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export
from guerilla_render_wizard import wizard_reference
from guerilla_render_wizard import guerilla_shader
from guerilla_render_wizard.export import shading
from guerilla_render_wizard.export import custom

# Guerilla modules
from guerilla import Document, pynode

def save_increment():
    wizard_tools.save_increment()

def export():
    scene = wizard_export.save_or_save_increment()
    try:
        stage_name = os.environ['wizard_stage_name']
        if stage_name == 'shading':
            shading.main()
        elif stage_name == 'custom':
            custom.main()
        else:
            logger.warning("Unplugged stage : {0}".format(stage_name))
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def reference_modeling():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.import_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def update_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.update_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def import_shading():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.reference_shading(modeling_reference['namespace'], modeling_reference['files'])

def update_shading():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.update_shading(modeling_reference['namespace'], modeling_reference['files'])

def import_custom():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.reference_custom(modeling_reference['namespace'], modeling_reference['files'])

def update_custom():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.update_custom(modeling_reference['namespace'], modeling_reference['files'])

def import_layout():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.reference_modeling(layout_reference['namespace'], layout_reference['files'])

def update_layout():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.update_modeling(layout_reference['namespace'], layout_reference['files'])

def import_animation():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.reference_modeling(animation_reference['namespace'], animation_reference['files'])

def update_animation():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.update_modeling(animation_reference['namespace'], animation_reference['files'])

def set_frame_range(*args):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    Document().FirstFrame.set(frame_range[1])
    Document().LastFrame.set(frame_range[2])

def set_frame_range_with_rolls(*args):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    inframe = frame_range[1] - frame_range[0]
    outframe = frame_range[2] + frame_range[3]
    Document().FirstFrame.set(inframe)
    Document().LastFrame.set(outframe)

def set_image_format(*args):
    image_format = wizard_communicate.get_image_format()
    width=float(image_format[0])
    height=float(image_format[1])
    dar=width/height
    Document().ProjectWidth.set(width)
    Document().ProjectHeight.set(height)
    Document().ProjectAspectRatio.set(1)
