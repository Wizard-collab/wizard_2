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
import json
import re

logger = logging.getLogger(__name__)


def check_points_in_names(export_GRP_list):
    for grp in export_GRP_list:
        for obj in get_all_children(grp):
            if '.' in obj.name:
                logger.warning(
                    f"Object '{obj.name}' contains a '.' in its name.")
                return True
    return False


def export_object_attributes_to_json(object_list, export_file, frange=None, visibility_data=None):
    """Export object attributes to JSON file.
    
    Args:
        object_list: List of objects to export attributes from
        export_file: Path to the export file (used to determine output directory)
        frange: Optional frame range [start, end] for per-frame attribute export
        visibility_data: Optional dict of visibility data to include in export
    """
    # Collect all descendants
    all_objects = []
    for obj in object_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj)
    # Remove duplicates and ensure unique objects
    all_objects = list(set(all_objects))
    
    # Collect only custom (extra) string attributes for each object
    attributes_dict = {}
    for obj in all_objects:
        if type(obj) == bpy.types.Collection:
            continue
        obj_name = obj.name if hasattr(obj, 'name') else str(obj)
        json_obj_name = obj_name.replace('.', '_')
        # Blender custom attributes are stored in obj.keys(), but skip Blender's internal keys (start with '_')
        extra_attrs = [k for k in obj.keys() if not k.startswith('_')]
        attr_values = {}
        for attr in extra_attrs:
            try:
                value = obj[attr]
                if isinstance(value, str):
                    attr_values[attr] = value
            except Exception:
                pass
        attributes_dict[json_obj_name] = attr_values
    
    # Add visibility data if provided
    if visibility_data:
        for obj_name, vis_data in visibility_data.items():
            json_obj_name = obj_name.replace('.', '_')
            if json_obj_name not in attributes_dict:
                attributes_dict[json_obj_name] = {}
            attributes_dict[json_obj_name]['visibility'] = vis_data
    
    # Save to JSON file in same folder as export_file
    export_dir = os.path.dirname(export_file)
    json_path = os.path.join(export_dir, 'attributes.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(attributes_dict, f, indent=2, ensure_ascii=False)
    print(f"Attributes exported to {json_path}")
    return json_path


def export_camera_data_to_json(object_list, output_dir):
    """Export camera focal length and focus distance data to JSON files for each camera in the object list."""

    camera_json_files = []

    # Get all objects including children
    all_objects = []
    for obj in object_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj)

    # Remove duplicates
    all_objects = list(set(all_objects))

    # Process each camera
    for obj in all_objects:
        if not hasattr(obj, "type"):
            continue
        if obj.type == 'CAMERA':
            camera_data = {}
            camera = obj.data

            # Get frame range from scene
            scene = bpy.context.scene
            start_frame = scene.frame_start
            end_frame = scene.frame_end

            # Store current frame to restore later
            current_frame = scene.frame_current

            # Collect data for each frame
            for frame in range(start_frame, end_frame + 1):
                scene.frame_set(frame)

                # Get focal length (lens value in mm)
                focal_length = camera.lens

                # Get focus distance (dof_distance)
                focus_distance = camera.dof.focus_distance if hasattr(
                    camera.dof, 'focus_distance') else 0.0

                # Get f-stop (aperture fstop)
                fstop = camera.dof.aperture_fstop if hasattr(
                    camera.dof, 'aperture_fstop') else 2.8

                camera_data[str(frame)] = {
                    'focal_length': focal_length,
                    'focus_distance': focus_distance,
                    'fstop': fstop
                }

            # Restore original frame
            scene.frame_set(current_frame)

            # Save to JSON file
            json_filename = f"{obj.name}.json"
            json_path = os.path.join(output_dir, json_filename)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(camera_data, f, indent=2, ensure_ascii=False)

            camera_json_files.append(json_path)

            logger.info(f"Camera data exported to {json_path}")
    return camera_json_files


def add_MAYA_USD_attribute_to_objects(object_list):
    all_objects = []
    for object in object_list:
        all_objects.append(object)
        all_objects += get_all_children(object)
    for obj in all_objects:
        if type(obj) == bpy.types.Collection:
            continue
        shape = getattr(obj, 'data', None)
        if shape is None:
            continue
        for attr in list(shape.keys()):
            if attr.startswith("_") or attr.startswith("primvars:"):
                continue
            primvar_attr = f"primvars:{attr}"
            # Actually create a new attribute with the same content
            if primvar_attr not in shape.keys():
                shape[primvar_attr] = shape[attr]


def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory


def unhide_all_children(object_list):
    def _unhide(obj):
        # hide_set is a method on objects, hide_viewport/hide_render are attributes on objects/collections
        try:
            if hasattr(obj, "hide_set") and callable(getattr(obj, "hide_set")):
                obj.hide_set(False)
        except Exception:
            pass
        try:
            if hasattr(obj, "hide_viewport"):
                obj.hide_viewport = False
        except Exception:
            pass
        try:
            if hasattr(obj, "hide_render"):
                obj.hide_render = False
        except Exception:
            pass

    def _unhide_parent_collections(obj):
        # Get all collections that contain this object
        if hasattr(obj, "users_collection"):
            for collection in obj.users_collection:
                _unhide(collection)
                # Recursively unhide parent collections
                _unhide_parent_collections_recursive(collection)
    
    def _unhide_parent_collections_recursive(collection):
        # Find parent collections of this collection
        for parent_collection in bpy.data.collections:
            if collection.name in parent_collection.children.keys():
                _unhide(parent_collection)
                _unhide_parent_collections_recursive(parent_collection)
        # Also check scene collection
        if collection.name in bpy.context.scene.collection.children.keys():
            _unhide(bpy.context.scene.collection)

    for obj in object_list:
        # Unhide parent collections
        _unhide_parent_collections(obj)
        # Unhide the object itself
        _unhide(obj)
        # Unhide all children
        for child in get_all_children(obj):
            _unhide(child)


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
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_list:
        if type(obj) != bpy.types.Collection:
            obj.select_set(True)
        for obj in get_all_children(obj):
            obj.select_set(True)
        # bpy.context.view_layer.objects.active = GRP


def add_default_shader(objects_list):
    all_objects = []
    for obj in objects_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj, meshes=1)
    for obj in all_objects:
        if type(obj) == bpy.types.Collection:
            continue
        if obj.type == 'MESH':
            if not obj.data.materials:
                mat = bpy.data.materials.new(name="DefaultMaterial")
                mat.use_nodes = False
                obj.data.materials.append(mat)


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
        # Add tags directly to the object
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


def apply_json_attr_to_new_objects(new_objects, file_path):
    # Get the directory of the file_path
    attributes_path = os.path.join(
        os.path.dirname(file_path), "attributes.json")
    if os.path.exists(attributes_path):
        with open(attributes_path, "r", encoding="utf-8") as f:
            attributes_data = json.load(f)

        # Extract visibility data separately
        visibility_data = {}
        for obj_name, attrs in attributes_data.items():
            if 'visibility' in attrs:
                visibility_data[obj_name] = attrs['visibility']

        # Assign attributes from JSON to matching objects
        for obj in new_objects:
            if type(obj) == bpy.types.Collection:
                continue
            # Helper to strip Blender's numeric suffixes (.001, .002, etc.)
            obj_base_name = re.sub(r"\.\d+$", "", obj.name)
            if obj_base_name in attributes_data:
                for attr, value in attributes_data[obj_base_name].items():
                    if attr == 'visibility':
                        # Skip visibility here, it's handled separately
                        continue
                    obj[attr] = value
        
        # Apply visibility data to objects
        if visibility_data:
            apply_visibility_data_to_objects(new_objects, visibility_data)


def apply_json_camera_data_to_new_cameras(new_objects, file_path):
    # Get the directory of the file_path
    output_dir = os.path.dirname(file_path)

    # Process each camera
    for obj in new_objects:
        if obj.type == 'CAMERA':
            # Try multiple naming patterns to find the matching JSON file
            json_filename = None
            potential_names = [
                obj.name,  # Exact match
                # Remove Blender suffix (.001, .002, etc.)
                re.sub(r"\.\d+$", "", obj.name),
                obj.name.replace("_", "."),  # Convert underscores to dots
                # Remove suffix and convert underscores
                re.sub(r"\.\d+$", "", obj.name).replace("_", "."),
                obj.name.replace(".", "_"),  # Convert dots to underscores
                # Remove underscore suffix (_001, _002, etc.)
                re.sub(r"_\d+$", "", obj.name),
                # Extract name after namespace (e.g., "namespace:camera" -> "camera")
                obj.name.split(":")[-1] if ":" in obj.name else None,
                # Capitalize first letter (e.g., "camera" -> "Camera")
                obj.name.split(":")[-1].title() if ":" in obj.name else None,
            ]
            # Remove None values from the list
            potential_names = [
                name for name in potential_names if name is not None]
            for name in potential_names:
                test_filename = f"{name}.json"
                test_path = os.path.join(output_dir, test_filename)
                if os.path.exists(test_path):
                    json_filename = test_filename
                    break

            if json_filename is None:
                logger.warning(
                    f"No matching JSON file found for camera '{obj.name}'")
                continue
            json_path = os.path.join(output_dir, json_filename)

            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    camera_data = json.load(f)

                camera = obj.data

                # Get frame range from scene
                scene = bpy.context.scene
                start_frame = scene.frame_start
                end_frame = scene.frame_end

                # Store current frame to restore later
                current_frame = scene.frame_current

                # Apply data for each frame
                for frame in range(start_frame, end_frame + 1):
                    if str(frame) in camera_data:
                        scene.frame_set(frame)

                        # Set focal length (lens value in mm)
                        camera.lens = camera_data[str(frame)]['focal_length']
                        camera.keyframe_insert(data_path="lens", frame=frame)

                        # Set focus distance (dof_distance)
                        if hasattr(camera.dof, 'focus_distance'):
                            camera.dof.focus_distance = camera_data[str(
                                frame)]['focus_distance']
                            camera.dof.keyframe_insert(
                                data_path="focus_distance", frame=frame)

                        # Set f-stop (aperture fstop)
                        if 'fstop' in camera_data[str(frame)] and hasattr(camera.dof, 'aperture_fstop'):
                            camera.dof.aperture_fstop = camera_data[str(
                                frame)]['fstop']
                            camera.dof.keyframe_insert(
                                data_path="aperture_fstop", frame=frame)

                # Restore original frame
                scene.frame_set(current_frame)


def set_mode_to_object():
    # Ensure there is an active object for the operator poll to succeed.
    # If none, try to pick one from the view_layer or scene. If still none, do nothing.
    try:
        active = bpy.context.view_layer.objects.active
    except Exception:
        active = None

    if active is None:
        # try to find any object in the current view layer
        objs = [o for o in bpy.context.view_layer.objects if o is not None]
        if not objs:
            # try scene objects as last resort
            objs = [o for o in bpy.context.scene.objects if o is not None]
        if objs:
            bpy.context.view_layer.objects.active = objs[0]
        else:
            logger.debug(
                "set_mode_to_object: no objects available to set active, skipping mode change")
            return

    # Only call the operator if we are not already in OBJECT mode
    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    except RuntimeError as exc:
        # log and continue to avoid crashing callers
        logger.exception("Failed to set mode to OBJECT: %s", exc)
        return


# =============================================================================
# VISIBILITY HANDLING FUNCTIONS
# =============================================================================

def store_visibility_data(object_list, frange):
    """Store visibility data for all objects in the list, per frame.
    
    This function captures viewport visibility (hide_viewport) and render
    visibility (hide_render) for every frame in the range. This is needed
    because Blender's ABC export stops writing data when objects become hidden.
    
    Args:
        object_list: List of root objects/collections to process
        frange: [start_frame, end_frame]
    
    Returns:
        dict: {object_name: {frame: {'hide_viewport': bool, 'hide_render': bool}}}
    """
    visibility_data = {}
    
    # Collect all descendants
    all_objects = []
    for obj in object_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj)
    # Remove duplicates and filter out collections
    all_objects = [obj for obj in set(all_objects) if type(obj) != bpy.types.Collection]
    
    scene = bpy.context.scene
    current_frame = scene.frame_current
    start_frame = frange[0]
    end_frame = frange[1]
    
    for obj in all_objects:
        obj_name = obj.name
        visibility_data[obj_name] = {}
        
        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)
            visibility_data[obj_name][str(frame)] = {
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render
            }
    
    # Restore original frame
    scene.frame_set(current_frame)
    
    return visibility_data


def remove_visibility_animation(object_list):
    """Remove visibility animation/drivers and force all objects visible.
    
    This function removes all keyframes and drivers on hide_viewport and 
    hide_render, and sets all objects to visible. This is necessary because 
    Blender's ABC exporter stops writing object data when objects become 
    hidden mid-animation.
    
    Note: The scene is typically reopened after export, so no restoration
    is performed.
    
    Args:
        object_list: List of root objects/collections to process
    """
    # Collect all descendants
    all_objects = []
    for obj in object_list:
        all_objects.append(obj)
        all_objects += get_all_children(obj)
    # Remove duplicates and filter out collections
    all_objects = [obj for obj in set(all_objects) if type(obj) != bpy.types.Collection]
    
    for obj in all_objects:
        # Remove drivers on visibility properties
        if obj.animation_data:
            drivers_to_remove = []
            for driver in obj.animation_data.drivers:
                if driver.data_path in ('hide_viewport', 'hide_render'):
                    drivers_to_remove.append(driver.data_path)
            for data_path in drivers_to_remove:
                obj.driver_remove(data_path)
        
        # Remove keyframe animation on visibility properties
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            
            # Remove hide_viewport fcurve
            for fcurve in list(action.fcurves):
                if fcurve.data_path == 'hide_viewport':
                    action.fcurves.remove(fcurve)
                    break
            
            # Remove hide_render fcurve
            for fcurve in list(action.fcurves):
                if fcurve.data_path == 'hide_render':
                    action.fcurves.remove(fcurve)
                    break
        
        # Force objects visible for export
        obj.hide_viewport = False
        obj.hide_render = False


def apply_visibility_data_to_objects(new_objects, visibility_data):
    """Apply per-frame visibility data to imported objects.
    
    This function reads the visibility data from the JSON and creates
    keyframe animation on hide_viewport and hide_render for each object.
    
    Args:
        new_objects: List of imported objects
        visibility_data: dict {object_name: {frame: {'hide_viewport': bool, 'hide_render': bool}}}
    """
    scene = bpy.context.scene
    current_frame = scene.frame_current
    
    for obj in new_objects:
        if type(obj) == bpy.types.Collection:
            continue
        
        # Try to find matching visibility data
        obj_base_name = re.sub(r"\.(\d+)$", "", obj.name)
        obj_base_name_underscore = obj_base_name.replace('.', '_')
        
        vis_data = None
        for name_variant in [obj.name, obj_base_name, obj.name.replace('.', '_'), obj_base_name_underscore]:
            if name_variant in visibility_data:
                vis_data = visibility_data[name_variant]
                break
        
        if vis_data is None:
            continue
        
        # Check if there's any actual animation (values change across frames)
        frames = sorted(vis_data.keys(), key=int)
        if not frames:
            continue
        
        hide_viewport_values = [vis_data[f]['hide_viewport'] for f in frames]
        hide_render_values = [vis_data[f]['hide_render'] for f in frames]
        
        has_viewport_animation = len(set(hide_viewport_values)) > 1
        has_render_animation = len(set(hide_render_values)) > 1
        
        if not has_viewport_animation and not has_render_animation:
            # Just set static values
            obj.hide_viewport = hide_viewport_values[0]
            obj.hide_render = hide_render_values[0]
            continue
        
        # Remove existing visibility animation/drivers before applying new ones
        if obj.animation_data:
            # Remove drivers on visibility
            for data_path in ['hide_viewport', 'hide_render']:
                try:
                    obj.driver_remove(data_path)
                except:
                    pass
            
            # Remove existing visibility fcurves
            if obj.animation_data.action:
                action = obj.animation_data.action
                for fcurve in list(action.fcurves):
                    if fcurve.data_path.startswith('hide_viewport') or fcurve.data_path.startswith('hide_render'):
                        action.fcurves.remove(fcurve)
        
        # Use keyframe_insert method which is more reliable
        for frame_str in frames:
            frame = int(frame_str)
            scene.frame_set(frame)
            
            if has_viewport_animation:
                obj.hide_viewport = vis_data[frame_str]['hide_viewport']
                obj.keyframe_insert(data_path='hide_viewport', frame=frame)
            
            if has_render_animation:
                obj.hide_render = vis_data[frame_str]['hide_render']
                obj.keyframe_insert(data_path='hide_render', frame=frame)
        
        # Set interpolation to CONSTANT for visibility keyframes
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            for fcurve in action.fcurves:
                if fcurve.data_path in ('hide_viewport', 'hide_render'):
                    for kp in fcurve.keyframe_points:
                        kp.interpolation = 'CONSTANT'
        
        # Set static values if not animated
        if not has_viewport_animation:
            obj.hide_viewport = hide_viewport_values[0]
        if not has_render_animation:
            obj.hide_render = hide_render_values[0]
    
    scene.frame_set(current_frame)
