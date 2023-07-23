# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_tools

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

def import_animation_cache(reference_dic):
    animated_asset_name = wizard_communicate.get_export_name_from_reference_namespace(reference_dic['namespace'], int(os.environ['wizard_work_env_id']))
    shading_reference_namespace = get_shading_reference(animated_asset_name)
    if not shading_reference_namespace:
        logger.warning(f"{animated_asset_name} shading reference not found, can't plug animation.")
        return
    all_meshes = wizard_tools.get_meshes_in_collection(bpy.data.collections[shading_reference_namespace])
    cache_file = load_cache_file(reference_dic)
    add_sequences_caches(reference_dic['namespace'], all_meshes, cache_file)

def update_animation_cache(reference_dic):
    file_cache_name = f"{reference_dic['namespace']}:cache_file"
    if file_cache_name not in bpy.data.cache_files.keys():
        logger.warning(f"{file_cache_name} not found. Can't update animation")
    cache = bpy.data.cache_files[file_cache_name]
    cache.filepath = reference_dic['files'][0]

def load_cache_file(reference_dic):
    bpy.ops.cachefile.open(filepath=reference_dic['files'][0])
    cache = bpy.data.cache_files[os.path.basename(reference_dic['files'][0])]
    cache.name = f"{reference_dic['namespace']}:cache_file"
    return cache

def get_shading_reference(animated_asset_name):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    shading_reference = None
    if 'shading' in references.keys():
        for reference in references['shading']:
            if reference['asset_name'] == animated_asset_name:
                shading_reference = reference
                break
    if not shading_reference:
        return None
    if not wizard_tools.namespace_exists(shading_reference['namespace']):
        return None
    return shading_reference['namespace']

def add_sequences_caches(animation_namespace, meshes, cache_file):
    for mesh in meshes:
        while animation_namespace not in mesh.modifiers.keys():
            mesh.modifiers.new(name=animation_namespace, type='MESH_SEQUENCE_CACHE')
        modifier = mesh.modifiers[animation_namespace]
        bpy.context.evaluated_depsgraph_get()
        modifier.cache_file = cache_file
        for object_path in cache_file.object_paths.values():
            if mesh.name in object_path.path:
                modifier.object_path = object_path.path
                modifier.read_data = {'VERT'}
                modifier.use_vertex_interpolation = False

                break
        if modifier.object_path == '':
            mesh.modifiers.remove(modifier)
