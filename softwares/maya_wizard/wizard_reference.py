# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Maya modules
import pymel.core as pm

def reference_modeling(namespace, files_list):
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'MODELING')

def update_modeling(namespace, files_list):
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)

def reference_rigging(namespace, files_list):
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'RIGGING')

def update_rigging(namespace, files_list):
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)

def create_reference(file, namespace, group):
    if not pm.objExists(group):
        pm.group( em=True, name=group )
    pm.createReference(file,
                        namespace=namespace,
                        groupName='wizard_temp_reference_node',
                        groupReference=True)
    for object in pm.listRelatives('wizard_temp_reference_node'):
        pm.parent(object, group)
    pm.delete('wizard_temp_reference_node')

def update_reference(namespace, files_list):
    references = pm.listReferences(namespaces=True)
    for reference in references:
        if reference[0] == namespace:
            if os.path.normpath(files_list[0]) != os.path.normpath(reference[1].path):
                reference[1].load(files_list[0])
