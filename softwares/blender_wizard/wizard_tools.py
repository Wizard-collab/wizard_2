# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
import wizard_communicate
import wizard_hooks

# Blender modules
import bpy

# Python modules
import os
import logging

logger = logging.getLogger(__name__)


def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory


def save_increment(comment=''):
    file_path, version_id = wizard_communicate.add_version(
        int(os.environ['wizard_work_env_id']), comment)
    if file_path and version_id:
        logger.info("Saving file {}".format(file_path))
        bpy.ops.wm.save_as_mainfile(filepath=file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
        return file_path
    else:
        logger.warning("Can't save increment")


def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('blender', stage_name, string_asset, scene_path)


def trigger_after_scene_openning_hook():
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_scene_openning_hooks('blender', stage_name, string_asset)


def check_obj_list_existence(object_list):
    success = True
    for obj_name in object_list:
        obj = bpy.context.scene.objects.get(obj_name)
        if not obj:
            logger.warning("'{}' not found".format(obj_name))
            success = False
    return success


def get_direct_children(obj):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == obj:
            children.append(ob)
    return children


def get_all_nodes():
    all_objects = []
    for node in bpy.data.objects:
        all_objects.append(node)
    for node in bpy.data.meshes:
        all_objects.append(node)
    for material in bpy.data.materials:
        all_objects.append(material)
    for image in bpy.data.images:
        all_objects.append(image)
    return all_objects


def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for obj in all_objects:
        if obj not in old_objects:
            new_objects.append(obj)
    return new_objects


def get_render_set_collection(namespace_collection):
    all_children = namespace_collection.children_recursive
    for child in all_children:
        if type(child) != bpy.types.Collection:
            continue
        if 'render_set' not in child.name:
            continue
        return child
    logger.warning(f"{namespace_collection}/render_set not found")
    return


def get_all_children(obj, meshes=0):
    if type(obj) == bpy.types.Collection:
        return obj.all_objects
    else:
        children = []
        all_objects = []
        for ob in bpy.data.objects:
            ancestor = ob
            while 1:
                ancestor = ancestor.parent
                if ancestor == None:
                    break
                if ancestor == obj:
                    children.append(ob)
                    if meshes:
                        children.append(ob.data)
                    break
        return (children)


def select_all_children(objects_list):
    # bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_list:
        if type(obj) != bpy.types.Collection:
            obj.select_set(True)
        for obj in get_all_children(obj):
            obj.select_set(True)
        # bpy.context.view_layer.objects.active = GRP


def namespace_exists(namespace):
    return namespace in list_all_collections(bpy.context.scene.collection)


def list_all_collections(collection, all_collections=None):
    if all_collections is None:
        all_collections = []
    if collection.override_library:
        pass
    else:
        all_collections.append(collection.name.split('.')[0])
    for child in collection.children:
        list_all_collections(child, all_collections)
    return all_collections


def create_collection_if_not_exists(collection_name, parent=None):
    if parent is None:
        parent = bpy.context.scene.collection

    new_collection = None
    for coll in parent.children.keys():
        if collection_name == coll.split('.')[0] or collection_name == coll:
            new_collection = bpy.data.collections[coll]
        else:
            continue

    if new_collection is None:
        new_collection = bpy.data.collections.new(collection_name)
        parent.children.link(new_collection)
    return new_collection


def set_collection_active(collection):
    if not collection:
        return
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, collection.name)
    bpy.context.view_layer.active_layer_collection = layerColl


def find_library(file_path):
    for lib in bpy.data.libraries:
        if lib.filepath == file_path:
            return 1
    return 0


def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found


def remove_export_name_from_names(object_list, export_name):
    objects_dic = dict()
    for obj in object_list:
        old_name = obj.name
        if obj.name.endswith(f'_{export_name}'):
            obj.name = old_name.replace(f'_{export_name}', '')
        objects_dic[obj] = old_name
    return objects_dic


def reassign_old_name_to_objects(objects_dic):
    for obj in objects_dic.keys():
        obj.name = objects_dic[obj]


def apply_tags(object_list):
    all_objects = []
    for obj in object_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj, meshes=1)
    for obj in all_objects:
        if type(obj) == bpy.types.Collection:
            continue
        if 'wizardTags' not in obj.keys():
            existing_tags = []
        else:
            existing_tags = obj['wizardTags'].split(',')
        asset_tag = "{}_{}".format(
            os.environ['wizard_category_name'], os.environ['wizard_asset_name'])
        if os.environ['wizard_variant_name'] != 'main':
            asset_tag += f"_{os.environ['wizard_variant_name']}"
        to_tag = [f"CATEGORY={os.environ['wizard_category_name']}",
                  f"ASSET={asset_tag}", f"OBJECT={obj.name}"]
        to_tag += [f"{os.environ['wizard_category_name']}",
                   asset_tag, obj.name]
        tags = existing_tags + to_tag
        obj['wizardTags'] = (',').join(set(tags))


def get_all_collections():
    collections = bpy.data.collections
    return collections


def get_export_grps(base_name):
    grp_dic = dict()
    tokens_len = len(base_name.split('_'))
    for collection in get_all_collections():
        collection_name = collection.name
        if base_name in collection_name:
            object_name_tokens = collection_name.split('_')
            if len(object_name_tokens) == tokens_len:
                export_name = 'main'
            elif len(object_name_tokens) > tokens_len:
                export_name = object_name_tokens[-1]
            if export_name in grp_dic.values():
                logger.warning(f'{collection_name} already found.')
                continue
            grp_dic[collection_name] = export_name
    return grp_dic


def group_objects_before_export(export_GRP_list):
    new_export_GRP_list = []
    for obj in export_GRP_list:
        if type(obj) == bpy.types.Collection:
            bpy.ops.object.empty_add(location=(0, 0, 0))
            empty_object = bpy.context.object
            empty_object.name = obj.name

            for child in obj.all_objects:
                if child == empty_object:
                    continue
                if child.parent is None:
                    child.parent = empty_object

            new_export_GRP_list.append(empty_object)
        else:
            new_export_GRP_list.append(obj)
    return new_export_GRP_list


def get_meshes_in_collection(collection):
    meshes = []
    for obj in collection.objects:
        if obj.type == 'MESH':
            meshes.append(obj)
    for child_collection in collection.children:
        meshes.extend(get_meshes_in_collection(child_collection))
    return meshes


def get_objects_in_collection(collection):
    objects = []
    for obj in collection.objects:
        objects.append(obj)
    for child_collection in collection.children:
        objects.extend(get_objects_in_collection(child_collection))
    return objects
