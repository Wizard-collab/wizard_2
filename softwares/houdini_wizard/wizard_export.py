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
import wizard_hooks
import wizard_communicate
from houdini_wizard import wizard_tools

def export(stage_name, export_name, exported_string_asset, out_node, frange=[0,0], custom_work_env_id = None, parent=None):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])

        if wizard_communicate.get_export_format(work_env_id) == 'vdb':
            export_dir = wizard_communicate.request_render(int(os.environ['wizard_version_id']), export_name)
            export_vdb(export_dir, frange, out_node, parent)
        else:
            export_file = wizard_communicate.request_export(work_env_id,
                                                                    export_name)
            export_by_extension(export_file, frange, out_node, parent)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                    [export_file],
                                                    work_env_id,
                                                    int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_by_extension(export_file, frange, out_node, parent):
    if export_file.endswith('.hip'):
        export_hip(export_file, frange)
    elif export_file.endswith('.abc'):
        export_abc(export_file, frange, out_node, parent)
    elif export_file.endswith('.vdb'):
        export_vdb(export_file, frange, out_node, parent)
    else:
        logger.info("{} extension is unkown".format(export_file))

def reopen(scene):
    hou.hipFile.load(scene, suppress_save_prompt=True)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = hou.hipFile.path()
    if 'untitled.hip' in scene:
        wizard_tools.save_increment()
        scene = hou.hipFile.path()
    else:
        hou.hipFile.save()
        logger.info("Saving file {}".format(scene))
    return scene

def export_hip(export_file, frange):
    logger.info("Exporting .ma")
    hou.hipFile.save(file_name=export_file)

def export_abc(export_file, frange, out_node, parent):
    wizard_abc_output = wizard_tools.look_for_node(out_node, parent)
    if wizard_abc_output:
        wizard_tools.apply_tags(wizard_abc_output)
        wizard_abc_output.parm("trange").set('normal')
        hou.playbar.setFrameRange(frange[0], frange[1])
        wizard_abc_output.parm("f1").setExpression('$FSTART')
        wizard_abc_output.parm("f2").setExpression('$FEND')
        wizard_abc_output.parm("motionBlur").set(1)
        wizard_abc_output.parm("shutter1").set(-0.2)
        wizard_abc_output.parm("shutter2").set(0.2)
        wizard_abc_output.parm("filename").set(export_file)
        wizard_abc_output.parm("execute").pressButton()
    else:
        logger.warning(f'"{out_node}" node not found')

def export_vdb(export_dir, frange, out_node, parent):
    wizard_vdb_output = wizard_tools.look_for_node(out_node, parent)
    if wizard_vdb_output:
        file = f"{export_dir}/fx_export.$F4.vdb"
        wizard_vdb_output.parm('sopoutput').set(file)
        wizard_vdb_output.parm("trange").set('normal')
        hou.playbar.setFrameRange(frange[0], frange[1])
        wizard_vdb_output.parm("f1").setExpression('$FSTART')
        wizard_vdb_output.parm("f2").setExpression('$FEND')

        wizard_vdb_output.parm('lpostframe').set("python")
        wizard_vdb_output.parm('postframe').set(wizard_tools.by_frame_progress_script())

        wizard_vdb_output.parm("execute").pressButton()
    else:
        logger.warning(f'"{out_node}" node not found')

def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('houdini', stage_name, string_asset, exported_string_asset)

def trigger_before_export_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.before_export_hooks('houdini', stage_name, string_asset, exported_string_asset)
    logger.warning("Ignoring additionnal objects from before export hooks. ( Wizard/Houdini exception )")

def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('houdini', stage_name, export_dir, string_asset, exported_string_asset)

