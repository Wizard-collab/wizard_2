# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Houdini modules
import nuke

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_tools
from nuke_wizard import wizard_reference
from nuke_wizard.export import compositing
from nuke_wizard.export import custom

logger = logging.getLogger(__name__)


def save_increment(comment=''):
    wizard_tools.save_increment(comment=comment)


def export(prepare_only=False):
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'compositing':
        compositing.invoke_settings_widget(prepare_only=prepare_only)
    elif stage_name == 'custom':
        custom.main()
    else:
        logger.warning(f"Unplugged stage : {stage_name}")


def reference_and_update_all():
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    reference_all(references)
    update_all(references)


def reference_all(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    reference_custom(references)
    reference_camera(references)
    reference_rendering(references)


def update_all(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    update_custom(references)
    update_camera(references)
    update_rendering(references)


def reference_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.reference_custom(reference)


def update_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.update_custom(reference)


def reference_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.reference_camera(reference)


def update_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.update_camera(reference)


def reference_rendering(references=None, local=True):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'rendering' in references.keys():
        for reference in references['rendering']:
            wizard_reference.reference_rendering(reference, local)


def update_rendering(references=None, local=True):
    if not references:
        references = wizard_communicate.get_references(
            int(os.environ['wizard_work_env_id']))
    if 'rendering' in references.keys():
        for reference in references['rendering']:
            wizard_reference.update_rendering(reference, local)


def set_frame_rate():
    frame_rate = wizard_communicate.get_frame_rate()
    nuke.root()['fps'].setValue(frame_rate)


def set_frame_range(rolls=0):
    frame_range = wizard_communicate.get_frame_range(
        int(os.environ['wizard_work_env_id']))
    if rolls:
        f1 = frame_range[1] - frame_range[0]
        f2 = frame_range[2] + frame_range[3]
    else:
        f1 = frame_range[1]
        f2 = frame_range[2]
    for n in nuke.allNodes('Read'):
        n['first'].setValue(f1)
        n['last'].setValue(f2)
        n['origfirst'].setValue(f1)
        n['origlast'].setValue(f2)
    nuke.knob("root.first_frame", str(f1))
    nuke.knob("root.last_frame", str(f2))


def set_image_format():
    image_format = wizard_communicate.get_image_format()
    format = ' '.join([str(image_format[0]), str(image_format[1])])
    format_name = os.environ['wizard_project'] + '_format'
    project_format = '{} {}'.format(format, format_name)
    nuke.addFormat(project_format)
    nuke.knob('root.format', format_name)
