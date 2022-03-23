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

# Hook modules
try:
    import guerilla_render_hook
except:
    guerilla_render_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import guerilla_render_hook")

def main(stage_name):
    export_dir = None
    if stage_name == 'shading':
        export_shading()
    if stage_name == 'custom':
        export_custom()

def export(stage_name, export_name, export_GRP):
    trigger_before_export_hook(stage_name)
    export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
    if export_from_extension(export_file, export_GRP):
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_version_id']))
    trigger_after_export_hook(stage_name, export_dir)

def export_shading():
    export_dir = None
    export_name = 'main'
    export('shading', export_name, 'shading_GRP')

def export_custom():
    export_dir = None
    export_name = 'main'
    export('custom', export_name, 'custom_GRP')

def export_from_extension(file, export_GRP):
    extension = file.split('.')[-1]
    if extension == 'gnode':
        return export_node(file, export_GRP)
    elif extension == 'gproject':
        return export_project(file, export_GRP)

def export_node(file, export_GRP):
    if export_GRP in wizard_tools.get_all_nodes():
        grp_node = wizard_tools.get_node_from_name(export_GRP)
        grp_node.savefile(file)
        return 1
    else:
        logger.warning('{0} not found'.format(export_GRP))
        return None

def export_project(file, export_GRP):
    if export_GRP in wizard_tools.get_all_nodes():
        filename = Document().getfilename()
        Document().save(file)
        Document().load(filename)
        return 1
    else:
        logger.warning('{0} not found'.format(export_GRP))
        return None

def trigger_before_export_hook(stage_name):
    # Trigger the before export hook
    if guerilla_render_hook:
        try:
            guerilla_render_hook.before_export(stage_name)
        except:
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if guerilla_render_hook:
        try:
            guerilla_render_hook.after_export(stage_name, export_dir)
        except:
            logger.error(str(traceback.format_exc()))

