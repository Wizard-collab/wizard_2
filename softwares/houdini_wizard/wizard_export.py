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

# Hook modules
try:
    import houdini_hook
except:
    houdini_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import houdini_hook")

def export(stage_name, export_name, frange=[0,0], custom_work_env_id = None, parent=None):
    if trigger_sanity_hook(stage_name):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])

        if wizard_communicate.get_export_format(work_env_id) == 'vdb':
            export_dir = wizard_communicate.request_render(int(os.environ['wizard_version_id']), export_name)
            export_vdb(export_dir, frange, parent)
        else:
            export_file = wizard_communicate.request_export(work_env_id,
                                                                    export_name)
            export_by_extension(export_file, frange, parent)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                    [export_file],
                                                    work_env_id,
                                                    int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

def export_by_extension(export_file, frange, parent):
    if export_file.endswith('.hip'):
        export_hip(export_file, frange)
    elif export_file.endswith('.abc'):
        export_abc(export_file, frange, parent)
    elif export_file.endswith('.vdb'):
        export_vdb(export_file, frange, parent)
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

def export_abc(export_file, frange, parent):
    wizard_abc_output = wizard_tools.look_for_node('wizard_abc_output', parent)
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
        logger.warning('"wizard_abc_output" node not found')

def export_vdb(export_dir, frange, parent):
    wizard_vdb_output = wizard_tools.look_for_node('wizard_vdb_output', parent)
    if wizard_vdb_output:
        file = f"{export_dir}/$F4.vdb"
        wizard_vdb_output.parm('sopoutput').set(file)
        wizard_vdb_output.parm("trange").set('normal')
        hou.playbar.setFrameRange(frange[0], frange[1])
        wizard_vdb_output.parm("f1").setExpression('$FSTART')
        wizard_vdb_output.parm("f2").setExpression('$FEND')

        wizard_vdb_output.parm('lpostframe').set("python")
        wizard_vdb_output.parm('postframe').set(wizard_tools.by_frame_progress_script())

        wizard_vdb_output.parm("execute").pressButton()
    else:
        logger.warning('"wizard_vdb_output" node not found')

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if houdini_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = houdini_hook.sanity(stage_name)
            if not sanity:
                logger.info("Exporting cancelled due to sanity hook")
            return sanity
        except:
            logger.info("Can't trigger sanity hook")
            logger.error(str(traceback.format_exc()))
            return True
    else:
        return True

def trigger_before_export_hook(stage_name):
    # Trigger the before export hook
    if houdini_hook:
        try:
            logger.info("Trigger before export hook")
        except:
            logger.info("Can't trigger before export hook")
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if houdini_hook:
        try:
            logger.info("Trigger after export hook")
            houdini_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))
