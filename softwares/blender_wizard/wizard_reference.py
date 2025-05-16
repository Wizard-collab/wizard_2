# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
import wizard_hooks
from blender_wizard import cycles_shader
from blender_wizard import wizard_tools

# Python modules
import os
import logging

logger = logging.getLogger(__name__)


def reference_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    cycles_shader.plug_textures(
        reference_dic['namespace'], reference_dic['files'])
    trigger_after_reference_hook('texturing',
                                 reference_dic['files'],
                                 reference_dic['namespace'],
                                 wizard_tools.get_new_objects(old_objects),
                                 reference_dic['string_stage'])


def update_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    cycles_shader.reload_textures(
        reference_dic['namespace'], reference_dic['files'], update=True)
    trigger_after_reference_hook('texturing',
                                 reference_dic['files'],
                                 reference_dic['namespace'],
                                 wizard_tools.get_new_objects(old_objects),
                                 reference_dic['string_stage'])


def import_modeling(reference_dic):
    create_reference(reference_dic, 'MODELING')


def update_modeling(reference_dic):
    update_reference(reference_dic, 'MODELING')


def import_rigging(reference_dic):
    create_reference(reference_dic, 'RIGGING')


def update_rigging(reference_dic):
    update_reference(reference_dic, 'RIGGING')


def import_camrig(reference_dic):
    create_reference(reference_dic, 'CAMRIG')


def update_camrig(reference_dic):
    update_reference(reference_dic, 'CAMRIG')


def import_shading(reference_dic):
    create_reference(reference_dic, 'SHADING')
    apply_shaders()


def update_shading(reference_dic):
    update_reference(reference_dic, 'SHADING')
    apply_shaders()


def import_grooming(reference_dic):
    create_reference(reference_dic, 'GROOMING')


def update_grooming(reference_dic):
    update_reference(reference_dic, 'GROOMING')


def import_layout(reference_dic):
    create_reference(reference_dic, 'LAYOUT')


def update_layout(reference_dic):
    update_reference(reference_dic, 'LAYOUT')


def import_animation(reference_dic):
    create_reference(reference_dic, 'ANIMATION')


def update_animation(reference_dic):
    update_reference(reference_dic, 'ANIMATION')


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
        group_collection = wizard_tools.create_collection_if_not_exists(
            referenced_stage, parent=None)
        namespace_collection = wizard_tools.create_collection_if_not_exists(
            reference_dic['namespace'], parent=group_collection)
        wizard_tools.set_collection_active(namespace_collection)
        for file in reference_dic['files']:
            if file.endswith('.abc'):
                import_abc(file, reference_dic, namespace_collection)
            if file.endswith('.usd'):
                import_usd(file, reference_dic, namespace_collection)
            elif file.endswith('.blend'):
                link_blend(file, reference_dic, namespace_collection)
            else:
                logger.info('{} extension is unknown'.format(file))
        trigger_after_reference_hook(referenced_stage.lower(),
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     wizard_tools.get_new_objects(old_objects),
                                     reference_dic['string_stage'])


def update_reference(reference_dic, referenced_stage):
    old_objects = wizard_tools.get_all_nodes()
    if wizard_tools.namespace_exists(reference_dic['namespace']):
        for file in reference_dic['files']:
            if file.endswith('.blend'):
                update_blend(file, reference_dic['namespace'])
            if file.endswith('.abc'):
                update_abc(file, reference_dic['namespace'])
            if file.endswith('.usd'):
                update_usd(file, reference_dic['namespace'])
            else:
                logger.info('{} extension is not updatable'.format(file))
        trigger_after_reference_hook(referenced_stage.lower(),
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     wizard_tools.get_new_objects(old_objects),
                                     reference_dic['string_stage'])


def import_abc(file_path, reference_dic, parent_collection=None):
    if parent_collection is None:
        parent_collection = bpy.context.scene.collection
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.alembic_import(
        filepath=file_path, as_background_job=False, always_add_cache_reader=True)
    cache = bpy.data.cache_files[os.path.basename(file_path)]
    cache.name = f"{reference_dic['namespace']}:cache_file"
    return cache


def import_usd(file_path, reference_dic, parent_collection=None):
    if parent_collection is None:
        parent_collection = bpy.context.scene.collection
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.usd_import(
        filepath=file_path)
    if os.path.basename(file_path) not in bpy.data.cache_files.keys():
        return
    cache = bpy.data.cache_files[os.path.basename(file_path)]
    cache.name = f"{reference_dic['namespace']}:cache_file"
    return cache


def update_abc(file_path, namespace):
    file_cache_name = f"{namespace}:cache_file"
    if file_cache_name not in bpy.data.cache_files.keys():
        logger.warning(
            f"{file_cache_name} not found. Can't update Alembic file.")
        return
    cache = bpy.data.cache_files[file_cache_name]
    cache.filepath = file_path


def update_usd(file_path, namespace):
    file_cache_name = f"{namespace}:cache_file"
    if file_cache_name not in bpy.data.cache_files.keys():
        logger.warning(
            f"{file_cache_name} not found. Can't update USD file.")
        return
    cache = bpy.data.cache_files[file_cache_name]
    cache.filepath = file_path


def link_blend(file_path, reference_dic, parent_collection=None):
    '''
    if wizard_tools.find_library(file_path):
        logger.warning(f"Ressource already existing, skipping...")
        return
    '''

    if parent_collection is None:
        parent_collection = bpy.context.scene.collection
    wizard_tools.set_collection_active(parent_collection)
    with bpy.data.libraries.load(file_path, link=True) as (data_from, data_to):
        data_to.collections = [c for c in data_from.collections]
    for coll in data_to.collections:
        if coll is not None:

            if "main_collection_tag" not in coll.keys():
                continue

            override_collection = coll.override_hierarchy_create(
                bpy.context.scene, bpy.context.view_layer, do_fully_editable=True)
            bpy.context.scene.collection.children.unlink(override_collection)
            parent_collection.children.link(override_collection)
            bpy.context.view_layer.update()

    library_override(reference_dic['namespace'])

    if os.path.basename(file_path) in bpy.data.libraries.keys():
        lib = bpy.data.libraries[os.path.basename(file_path)]
        lib.name = reference_dic['namespace']


def library_override(collection_name):
    for object in bpy.data.collections[collection_name].all_objects:
        bpy.data.objects[object.name].override_create(
            remap_local_usages=True)
        object.data.override_create(remap_local_usages=True)


def update_blend(file_path, namespace):
    try:
        lib = bpy.data.libraries[namespace]
        lib.filepath = file_path
        lib.reload()
        lib = bpy.data.libraries[os.path.basename(file_path)]
        lib.name = namespace
        library_override(namespace)
    except KeyError:
        logger.error(f"Library {namespace} not found")


def trigger_after_reference_hook(referenced_stage_name,
                                 files_list,
                                 namespace,
                                 new_objects,
                                 referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('blender',
                                       stage_name,
                                       referenced_stage_name,
                                       referenced_files_dir,
                                       namespace,
                                       new_objects,
                                       string_asset,
                                       referenced_string_asset)


def apply_shaders():
    if 'SHADING' not in bpy.data.collections.keys():
        return
    shading_meshes = wizard_tools.get_objects_in_collection(
        bpy.data.collections['SHADING'])

    all_objects = bpy.context.scene.objects
    for sh_obj in shading_meshes:
        if 'wizardTags' not in sh_obj.keys():
            continue
        sh_tags = (sh_obj['wizardTags']).split(',')
        sh_tags.sort()
        for target_obj in all_objects:
            if target_obj in shading_meshes:
                continue
            if 'wizardTags' not in target_obj.keys():
                continue
            tags = (target_obj['wizardTags']).split(',')
            tags.sort()
            OBJECT_tag = []
            ASSET_tag = []
            sh_OBJECT_tag = []
            sh_ASSET_tag = []
            for tag in tags:
                if "OBJECT" in tag:
                    OBJECT_tag.append(tag)
                if "ASSET" in tag:
                    ASSET_tag.append(tag)
            for sh_tag in sh_tags:
                if "OBJECT" in sh_tag:
                    sh_OBJECT_tag.append(sh_tag)
                if "ASSET" in sh_tag:
                    sh_ASSET_tag.append(sh_tag)
            if not OBJECT_tag or not ASSET_tag or not sh_OBJECT_tag or not sh_ASSET_tag:
                continue
            match = 0
            for tag in OBJECT_tag:
                if tag in sh_OBJECT_tag:
                    match += 1
            for tag in ASSET_tag:
                if tag in sh_ASSET_tag:
                    match += 1
            if match == 2:
                target_obj.data.materials.clear()
                for material in sh_obj.data.materials:
                    target_obj.data.materials.append(material)
