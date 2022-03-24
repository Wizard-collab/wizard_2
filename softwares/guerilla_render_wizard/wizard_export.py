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
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard.export import shading
from guerilla_render_wizard.export import custom

# Hook modules
try:
    import guerilla_render_hook
except:
    guerilla_render_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import guerilla_render_hook")

def main(stage_name):
    scene = save_or_save_increment()

    if stage_name == 'shading':
        export_dic = shading.main()
    if stage_name == 'custom':
        export_dic = custom.main()

    for export_name in export_dic.keys():
        export(export_dic[export_name]['stage_name'],
                    export_name,
                    export_dic[export_name]['export_GRP_list'])

    reopen(scene)

def export(stage_name, export_name, export_GRP_list):
    if trigger_sanity_hook(stage_name):
        additionnal_objects = trigger_before_export_hook(stage_name)
        export_GRP_list += additionnal_objects
        export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                    export_name)
        export_from_extension(export_file, export_GRP_list)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

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
        Document().save(scene)
        logger.info("Saving file {0}".format(scene))
    return scene

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if guerilla_render_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = guerilla_render_hook.sanity(stage_name)
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
    if guerilla_render_hook:
        try:
            additionnal_objects = []
            objects = guerilla_render_hook.before_export(stage_name)
            if type(objects) is list:
                for object in objects:
                    if wizard_tools.node_exists(object):
                        additionnal_objects.append(object)
                    else:
                        logger.warning("{0} doesn't exists".format(object))
            else:
                logger.warning("The before export hook should return an object list")
            return additionnal_objects
        except:
            logger.info("Can't trigger before export hook")
            logger.error(str(traceback.format_exc()))
            return []

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if guerilla_render_hook:
        try:
            logger.info("Trigger after export hook")
            guerilla_render_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))

