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
    # OUTPUT
    file = f"{export_dir}/fx_export.$F4.vdb"
    parm_output = wizard_vdb_output.parm('sopoutput')
    parm_output.deleteAllKeyframes()  # Prevents any expression from overriding the constant value
    parm_output.set(file)

    # FRAME RANGE
    hou.playbar.setFrameRange(frange[0], frange[1])
    hou.setFrame(frange[0])

    wizard_vdb_output.parm("trange").set('normal')
    start, end = map(int, frange)
    for name, value in (("f1", start), ("f2", end), ("f3", 1)):
        parm = wizard_vdb_output.parm(name)
        parm.deleteAllKeyframes()
        parm.set(value)

    # POST FRAME SCRIPT
    wizard_vdb_output.parm('lpostframe').set("python")
    wizard_vdb_output.parm('postframe').set(
        wizard_tools.by_frame_progress_script())

    if prepare_only:
        return

    # LOAD FROM DISK
    load_parm = wizard_vdb_output.parm('loadfromdisk')
    if load_parm is not None:
        load_parm.set(0)  # Makes sure the VDB is not loaded from disk before the export,
                          # which would prevent the export from happening

    # EXECUTING THE EXPORT
    wizard_vdb_output.parm("execute").pressButton()

    # \/ not useful as houdini automatically sets the load from disk parameter to 1 after the export
    # if load_parm is not None:
    #     load_parm.set(1)
