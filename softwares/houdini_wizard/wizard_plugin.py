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

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'custom':
        custom.main()

def reference_and_update_all():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    reference_all(references)

def reference_all(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    import_modeling(references)
    import_custom(references)
    import_animation(references)

def import_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for modeling_reference in references['animation']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.reference_custom(modeling_reference['namespace'], modeling_reference['files'])

def set_frame_range(rolls=0):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    if rolls:
        f1 = frame_range[1] - frame_range[0]
        f2 = frame_range[2] + frame_range[3]
    else:
        f1 = frame_range[1]
        f2 = frame_range[2]
    hou.playbar.setFrameRange(f1, f2)
