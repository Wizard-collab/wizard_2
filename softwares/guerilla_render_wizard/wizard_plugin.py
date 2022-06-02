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
from guerilla_render_wizard.export import lighting

# Guerilla modules
from guerilla import Document, pynode

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'shading':
        shading.main()
    elif stage_name == 'custom':
        custom.main()
    else:
        logger.warning("Unplugged stage : {0}".format(stage_name))

def setup_render(render_type):
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'lighting':
        lighting.setup_render_directory(render_type)
    else:
        logger.warning("Unplugged stage : {0}".format(stage_name))

def reference_and_update_all():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    reference_all(references)
    update_all(references)

def reference_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    import_modeling(references)
    import_texturing(references)
    import_shading(references)
    import_custom(references)
    import_layout(references)
    import_animation(references)
    import_cfx(references)
    import_camera(references)

def update_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    update_modeling(references)
    update_texturing(references)
    update_shading(references)
    update_custom(references)
    update_layout(references)
    update_animation(references)
    update_cfx(references)
    update_camera(references)

def import_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.import_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def update_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.update_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def import_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.reference_shading(modeling_reference['namespace'], modeling_reference['files'])

def update_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.update_shading(modeling_reference['namespace'], modeling_reference['files'])

def import_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.reference_custom(modeling_reference['namespace'], modeling_reference['files'])

def update_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.update_custom(modeling_reference['namespace'], modeling_reference['files'])

def import_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.reference_layout(layout_reference['namespace'], layout_reference['files'])

def update_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.update_layout(layout_reference['namespace'], layout_reference['files'])

def import_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.reference_animation(animation_reference['namespace'], animation_reference['files'])

def update_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.update_animation(animation_reference['namespace'], animation_reference['files'])

def import_cfx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'cfx' in references.keys():
        for animation_reference in references['cfx']:
            wizard_reference.reference_cfx(animation_reference['namespace'], animation_reference['files'])

def update_cfx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'cfx' in references.keys():
        for animation_reference in references['cfx']:
            wizard_reference.update_cfx(animation_reference['namespace'], animation_reference['files'])

def import_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for camera_reference in references['camera']:
            wizard_reference.reference_camera(camera_reference['namespace'], camera_reference['files'])

def update_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for camera_reference in references['camera']:
            wizard_reference.update_camera(camera_reference['namespace'], camera_reference['files'])

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
