# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Nuke modules
import nuke

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_tools

# Hook modules
try:
    import nuke_hook
except:
    nuke_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import nuke_hook")

def export(stage_name, export_name, frange=[0,0], custom_work_env_id = None):
    if trigger_sanity_hook(stage_name):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])

        if wizard_communicate.get_export_format(work_env_id) == 'exr':
            export_dir = wizard_communicate.request_render(int(os.environ['wizard_version_id']), export_name)
            export_exr(export_dir, frange)
        else:
            export_file = wizard_communicate.request_export(work_env_id,
                                                                    export_name)
            export_by_extension(export_file, frange)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                    [export_file],
                                                    work_env_id,
                                                    int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

def export_by_extension(export_file, frange):
    if export_file.endswith('.nk'):
        export_nk(export_file, frange)
    else:
        logger.info("{} extension is unkown".format(export_file))

def export_exr(export_dir, frange):
    render_node_name = 'wizard_render_node'
    if render_node_name in wizard_tools.get_all_nodes_names():
        render_node = nuke.toNode(render_node_name)
        file = f"{export_dir}/%05d.exr"
        render_node['file'].setValue(file)
        #render_node['colorspace'].setValue('compositing_linear')
        render_node['compression'].setValue('PIZ Wavelet')
        nuke.execute(render_node_name,frange[0],frange[1],1)
    else:
        logger.warning(f"{render_node_name} not found")

def reopen(scene):
    nuke.scriptClear()
    nuke.scriptOpen(scene)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = nuke.root()['name'].value()
    if scene == '':
        wizard_tools.save_increment()
        scene = nuke.root()['name'].value()
    else:
        nuke.scriptSave()
        logger.info("Saving file {}".format(scene))
    return scene

def export_nk(export_file, frange):
    logger.info("Exporting .nk")
    nuke.scriptSaveAs(export_file)

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if nuke_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = nuke_hook.sanity(stage_name)
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
    if nuke_hook:
        try:
            logger.info("Trigger before export hook")
        except:
            logger.info("Can't trigger before export hook")
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if nuke_hook:
        try:
            logger.info("Trigger after export hook")
            nuke_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))
