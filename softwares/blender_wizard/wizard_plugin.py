# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_tools
from blender_wizard import wizard_reference
from blender_wizard.export import modeling
from blender_wizard.export import shading
from blender_wizard.export import rigging
from blender_wizard.export import layout
from blender_wizard.export import custom
from blender_wizard.export import grooming
from blender_wizard.export import animation
from blender_wizard.export import camrig
from blender_wizard.export import camera
from blender_wizard.export import rendering

logger = logging.getLogger(__name__)


def save_increment(comment=''):
    wizard_tools.save_increment(comment)


def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'shading':
        shading.main()
    elif stage_name == 'rigging':
        rigging.main()
    elif stage_name == 'grooming':
        grooming.main()
    elif stage_name == 'camrig':
        camrig.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'custom':
        custom.main()
    elif stage_name == 'animation':
        animation.invoke_settings_widget()
    elif stage_name == 'camera':
        camera.invoke_settings_widget()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))


def setup_render(render_type):
    stage_name = os.environ['wizard_stage_name']
    if stage_name in ['lighting', 'shading', 'rendering']:
        frame_range = wizard_communicate.get_frame_range(
            int(os.environ['wizard_work_env_id']))
        rendering.setup_render_directory(render_type, frame_range)
    else:
        logger.warning("Unplugged stage : {0}".format(stage_name))


def export_camera():
    camera.invoke_settings_widget()


def import_and_update_all():
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    reference_texturing(references)
    reference_modeling(references)
    reference_rigging(references)
    reference_grooming(references)
    reference_shading(references)
    reference_layout(references)
    reference_animation(references)
    reference_camera(references)
    reference_custom(references)
    reference_camrig(references)
    update_texturing(references)
    update_modeling(references)
    update_rigging(references)
    update_grooming(references)
    update_shading(references)
    update_layout(references)
    update_animation(references)
    update_camera(references)
    update_custom(references)
    update_camrig(references)


def update_all():
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    update_texturing(references)
    update_modeling(references)
    update_rigging(references)
    update_grooming(references)
    update_shading(references)
    update_layout(references)
    update_animation(references)
    update_camera(references)
    update_custom(references)
    update_camrig(references)


def set_image_size():
    image_format = wizard_communicate.get_image_format()
    bpy.context.scene.render.resolution_x = image_format[0]
    bpy.context.scene.render.resolution_y = image_format[1]


def set_frame_rate():
    frame_rate = wizard_communicate.get_frame_rate()
    bpy.context.scene.render.fps = frame_rate


def set_frame_range():
    frame_range = wizard_communicate.get_frame_range(
        int(os.environ['wizard_work_env_id']))
    bpy.context.scene.frame_start = frame_range[1]
    bpy.context.scene.frame_end = frame_range[2]


def set_frame_range_with_rolls():
    frame_range = wizard_communicate.get_frame_range(
        int(os.environ['wizard_work_env_id']))
    bpy.context.scene.frame_start = frame_range[1]-frame_range[0]
    bpy.context.scene.frame_end = frame_range[2]+frame_range[3]


def reference_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.reference_texturing(reference)


def update_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.update_texturing(reference)


def reference_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.import_modeling(reference)


def update_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.update_modeling(reference)


def reference_rigging(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.import_rigging(reference)


def update_rigging(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.update_rigging(reference)


def reference_grooming(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.import_grooming(reference)


def update_grooming(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.update_grooming(reference)


def reference_camrig(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camrig' in references.keys():
        for reference in references['camrig']:
            wizard_reference.import_camrig(reference)


def update_camrig(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camrig' in references.keys():
        for reference in references['camrig']:
            wizard_reference.update_camrig(reference)


def reference_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.import_shading(reference)


def update_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.update_shading(reference)


def reference_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.import_layout(reference)


def update_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.update_layout(reference)


def reference_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.import_animation(reference)


def update_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.update_animation(reference)


def reference_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.import_camera(reference)


def update_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.update_camera(reference)


def reference_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.import_custom(reference)


def update_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.update_custom(reference)
