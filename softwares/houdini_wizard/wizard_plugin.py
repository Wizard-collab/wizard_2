# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_reference
from houdini_wizard.export import custom
from houdini_wizard.export import modeling
from houdini_wizard.export import rigging
from houdini_wizard.export import grooming
from houdini_wizard.export import layout
from houdini_wizard.export import cfx
from houdini_wizard.export import fx

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'custom':
        custom.main()
    elif stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'rigging':
        rigging.main()
    elif stage_name == 'grooming':
        grooming.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'cfx':
        cfx.invoke_settings_widget()
    elif stage_name == 'fx':
        fx.invoke_settings_widget()
    else:
        logger.warning(f"Unplugged stage : {stage_name}")

def reference_and_update_all():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    reference_all(references)
    update_all(references)

def reference_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    import_modeling(references)
    import_rigging(references)
    import_grooming(references)
    import_custom(references)
    import_layout(references)
    import_animation(references)
    import_cfx(references)
    import_camera(references)

def update_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    update_modeling(references)
    update_rigging(references)
    update_grooming(references)
    update_custom(references)
    update_layout(references)
    update_animation(references)
    update_cfx(references)
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

def import_rigging(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.reference_rigging(reference)

def update_rigging(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.update_rigging(reference)

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

def set_frame_range(rolls=0):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    if rolls:
        f1 = frame_range[1] - frame_range[0]
        f2 = frame_range[2] + frame_range[3]
    else:
        f1 = frame_range[1]
        f2 = frame_range[2]
    hou.playbar.setFrameRange(f1, f2)
