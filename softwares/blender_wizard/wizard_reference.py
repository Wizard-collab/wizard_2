# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
import wizard_hooks
from blender_wizard import redshift_shader
from blender_wizard import cycles_shader
from blender_wizard import wizard_tools
from blender_wizard import animation

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)


def reference_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(reference_dic['namespace'], reference_dic['files'])
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(reference_dic['namespace'], reference_dic['files'])
    trigger_after_reference_hook('texturing',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def update_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(reference_dic['namespace'], reference_dic['files'], update=True)
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(reference_dic['namespace'], reference_dic['files'], update=True)
    trigger_after_reference_hook('texturing',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def import_modeling(reference_dic):
    create_reference(reference_dic, 'MODELING') 

def update_modeling(reference_dic):
    update_reference(reference_dic, 'MODELING')   

def import_shading(reference_dic):
    create_reference(reference_dic, 'SHADING') 

def update_shading(reference_dic):
    update_reference(reference_dic, 'SHADING')   

def import_layout(reference_dic):
    create_reference(reference_dic, 'LAYOUT')  

def update_layout(reference_dic):
    update_reference(reference_dic, 'LAYOUT')  

def import_animation(reference_dic):
    #create_reference(reference_dic, 'ANIMATION')  
    animation.import_animation_cache(reference_dic)

def update_animation(reference_dic):
    #update_reference(reference_dic, 'ANIMATION')  
    animation.update_animation_cache(reference_dic)

def import_camera(reference_dic):
    create_reference(reference_dic, 'CAMERA')  

def update_camera(reference_dic):
    update_reference(reference_dic, 'CAMERA')  

def import_custom(reference_dic):
    create_reference(reference_dic, 'CUSTOM')  

def update_custom(reference_dic):
    update_reference(reference_dic, 'CUSTOM')  

def create_reference(reference_dic, referenced_stage):
    old_objects = wizard_tools.get_all_nodes()
    if not wizard_tools.namespace_exists(reference_dic['namespace']):
        group_collection = wizard_tools.create_collection_if_not_exists(referenced_stage, parent=None)
        namespace_collection = wizard_tools.create_collection_if_not_exists(reference_dic['namespace'], parent=group_collection)
        wizard_tools.set_collection_active(namespace_collection)
        for file in reference_dic['files']:
            if file.endswith('.abc'):
                import_abc(file, namespace_collection)
            elif file.endswith('.blend'):
                link_blend(file, reference_dic, namespace_collection)
            else:
                logger.info('{} extension is unknown'.format(file))
        trigger_after_reference_hook(referenced_stage.lower(),
                                    reference_dic['files'],
                                    reference_dic['namespace'],
                                    wizard_tools.get_new_objects(old_objects),
                                    reference_dic['string_variant'])

def update_reference(reference_dic, referenced_stage):
    old_objects = wizard_tools.get_all_nodes()
    if wizard_tools.namespace_exists(reference_dic['namespace']):
        for file in reference_dic['files']:
            if file.endswith('.blend'):
                update_blend(file, reference_dic['namespace'])
            else:
                logger.info('{} extension is not updatable'.format(file))
        trigger_after_reference_hook(referenced_stage.lower(),
                                    reference_dic['files'],
                                    reference_dic['namespace'],
                                    wizard_tools.get_new_objects(old_objects),
                                    reference_dic['string_variant'])

def import_abc(file_path, parent_collection=None):
    if parent_collection is None:
        parent_collection = bpy.context.scene.collection
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.alembic_import(filepath=file_path, as_background_job=False)

def link_blend(file_path, reference_dic, parent_collection=None):
    if wizard_tools.find_library(file_path):
        logger.warning(f"Ressource already existing, skipping...")
        return

    if parent_collection is None:
        parent_collection = bpy.context.scene.collection
    wizard_tools.set_collection_active(parent_collection)
    with bpy.data.libraries.load(file_path, link=True) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections]
    for coll in data_to.collections:
        if coll is not None:
            if coll.name != reference_dic['asset_name']:
                continue
            override_collection = coll.override_hierarchy_create(bpy.context.scene, bpy.context.view_layer, do_fully_editable=True)
            bpy.context.scene.collection.children.unlink(override_collection)
            parent_collection.children.link(override_collection)

    lib = bpy.data.libraries[os.path.basename(file_path)]
    lib.name = reference_dic['namespace']

def update_blend(file_path, namespace):
    try:
        lib = bpy.data.libraries[namespace]
        lib.filepath = file_path
        lib.reload()
        lib = bpy.data.libraries[os.path.basename(file_path)]
        lib.name = namespace
    except KeyError:
        logger.error(f"Library {namespace} not found")

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects,
                                    referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('blender',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects,
                                string_asset,
                                referenced_string_asset)

