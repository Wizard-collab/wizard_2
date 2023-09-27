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
        frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
        lighting.setup_render_directory(render_type, frame_range)
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
    import_grooming(references)
    import_texturing(references)
    import_shading(references)
    import_custom(references)
    import_layout(references)
    import_animation(references)
    import_cfx(references)
    import_fx(references)
    import_camera(references)

def update_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    update_modeling(references)
    update_grooming(references)
    update_texturing(references)
    update_shading(references)
    update_custom(references)
    update_layout(references)
    update_animation(references)
    update_cfx(references)
    update_fx(references)
    update_camera(references)

def import_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.reference_modeling(reference)

def update_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.update_modeling(reference)

def import_grooming(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.reference_grooming(reference)

def update_grooming(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.update_grooming(reference)

def import_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            guerilla_shader.import_texturing(reference['namespace'],
                                                reference['files'],
                                                reference['asset_name'],
                                                reference['string_stage'])

def update_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            guerilla_shader.update_texturing(reference['namespace'],
                                                reference['files'],
                                                reference['asset_name'],
                                                reference['string_stage'])

def import_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.reference_shading(reference)

def update_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.update_shading(reference)

def import_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.reference_custom(reference)

def update_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.update_custom(reference)

def import_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.reference_layout(reference)

def update_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.update_layout(reference)

def import_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.reference_animation(reference)

def update_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.update_animation(reference)

def import_cfx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'cfx' in references.keys():
        for reference in references['cfx']:
            wizard_reference.reference_cfx(reference)

def update_cfx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'cfx' in references.keys():
        for reference in references['cfx']:
            wizard_reference.update_cfx(reference)

def import_fx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'fx' in references.keys():
        for reference in references['fx']:
            wizard_reference.reference_fx(reference)

def update_fx(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'fx' in references.keys():
        for reference in references['fx']:
            wizard_reference.update_fx(reference)

def import_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.reference_camera(reference)

def update_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.update_camera(reference)

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

def set_frame_rate(*args):
    frame_rate = wizard_communicate.get_frame_rate()
    Document().Preferences.FrameRate.set(frame_rate)
