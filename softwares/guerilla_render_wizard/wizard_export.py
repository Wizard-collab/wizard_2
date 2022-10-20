# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Guerilla modules
import guerilla
from guerilla import Document, pynode

# Wizard modules
import wizard_communicate
import wizard_hooks
from guerilla_render_wizard import wizard_tools

def __init__():
    pass

def export(stage_name, export_name, exported_string_asset, export_GRP_list):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                    export_name)
        export_from_extension(export_file, export_GRP_list)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_work_env_id']),
                                                            int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def prepare_render(stage_name, export_name):
    if trigger_sanity_hook(stage_name):
        trigger_before_export_hook(stage_name)
        render_dir = wizard_communicate.request_render(export_name,
                                                int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, render_dir)
        return render_dir

def export_custom():
    export_dir = None
    export_name = 'main'
    export('custom', export_name, 'custom_GRP')

def export_from_extension(file, export_GRP_list):
    extension = file.split('.')[-1]
    if extension == 'gnode':
        return export_node(file, export_GRP_list)
    elif extension == 'gproject':
        return export_project(file, export_GRP_list)

def export_node(file, export_GRP_list):
    grp_node = wizard_tools.get_node_from_name(export_GRP_list[0])
    grp_node.savefile(file)

def export_project(file, export_GRP_list):
    wizard_tools.delete_all_but_list(export_GRP_list)
    Document().save(file)

def reopen(scene):
    Document().load(scene)
    logger.info("Opening file {0}".format(scene))

def save_or_save_increment():
    scene = Document().getfilename()
    if scene == None:
        wizard_tools.save_increment()
        scene = Document().getfilename()
    else:
        if os.environ["wizard_launch_mode"] == 'gui':
            wizard_communicate.screen_over_version(int(os.environ['wizard_version_id']))
        Document().save(scene)
        logger.info("Saving file {0}".format(scene))
    return scene

def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('guerilla_render', stage_name, string_asset, exported_string_asset)

def trigger_before_export_hook(stage_name, exported_string_asset):
    additionnal_objects = []
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    nodes = wizard_hooks.before_export_hooks('guerilla_render', stage_name, string_asset, exported_string_asset)
    for node in nodes:
        if wizard_tools.node_exists(node):
            additionnal_objects.append(node)
        else:
            logger.warning("{0} doesn't exists".format(node))
    return additionnal_objects

def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('guerilla_render', stage_name, export_dir, string_asset, exported_string_asset)
