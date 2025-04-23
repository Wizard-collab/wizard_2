# coding: utf-8
# Wizard commands hook

import logging

import hou
from houdini_wizard import wizard_tools

logger = logging.getLogger(__name__)


def hip_command(export_file):
    ''' This function is used to store 
    a default hip export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    hou.hipFile.save(file_name=export_file)


def abc_command(wizard_abc_output, frange, export_file, prepare_only=False):
    ''' This function is used to store 
    a default alembic export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    wizard_tools.apply_tags(wizard_abc_output)
    wizard_abc_output.parm("trange").set('normal')
    hou.playbar.setFrameRange(frange[0], frange[1])
    wizard_abc_output.parm("f1").setExpression('$FSTART')
    wizard_abc_output.parm("f2").setExpression('$FEND')
    wizard_abc_output.parm("motionBlur").set(1)
    wizard_abc_output.parm("shutter1").set(-0.2)
    wizard_abc_output.parm("shutter2").set(0.2)
    wizard_abc_output.parm("filename").set(export_file)
    if prepare_only:
        return
    wizard_abc_output.parm("execute").pressButton()


def vdb_command(wizard_vdb_output, frange, export_dir, prepare_only=False):
    ''' This function is used to store 
    a default vdb export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    file = f"{export_dir}/fx_export.$F4.vdb"
    wizard_vdb_output.parm('sopoutput').set(file)
    wizard_vdb_output.parm("trange").set('normal')
    hou.playbar.setFrameRange(frange[0], frange[1])
    wizard_vdb_output.parm("f1").setExpression('$FSTART')
    wizard_vdb_output.parm("f2").setExpression('$FEND')
    wizard_vdb_output.parm('lpostframe').set("python")
    wizard_vdb_output.parm('postframe').set(
        wizard_tools.by_frame_progress_script())
    if prepare_only:
        return
    wizard_vdb_output.parm("execute").pressButton()
