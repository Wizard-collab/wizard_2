# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from nuke_wizard import wizard_tools

# Nuke modules
import nuke

# Hook modules
try:
    import nuke_hook
except:
    nuke_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import nuke_hook")

def reference_lighting(namespace, files_list):
    import_from_extension(namespace, files_list, 'lighting')

def import_from_extension(namespace, files_list, stage_name):
    old_nodes = wizard_tools.get_all_nodes()
    extension = files_list[0].split('.')[-1]
    if extension == 'exr':
        reference_exr(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_nodes))

def reference_exr(namespace, files_list):
    paths_dic = wizard_tools.exr_list_to_paths_list(files_list)
    reads_list = []
    for path in paths_dic.keys():
        read_name = os.path.basename(path).split('.')[0]
        read = nuke.nodes.Read(file=path, name=read_name)
        namespace_knob = nuke.String_Knob('wizard_namespace', 'wizard_namespace')
        read.addKnob(namespace_knob)
        read['wizard_namespace'].setValue(namespace)
        read['wizard_namespace'].setEnabled(False)
        frange = paths_dic[path]
        read['first'].setValue(frange[0])
        read['last'].setValue(frange[1])
        read['origfirst'].setValue(frange[0])
        read['origlast'].setValue(frange[1])
        reads_list.append(read)
    wizard_tools.backdrop_nodes(reads_list, namespace)

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    # Trigger the after reference hook
    if nuke_hook:
        try:
            logger.info("Trigger after reference hook")
            nuke_hook.after_reference(stage_name,
                                        referenced_stage_name,
                                        referenced_files_dir,
                                        namespace,
                                        new_objects)
        except:
            logger.info("Can't trigger after reference hook")
            logger.error(str(traceback.format_exc()))