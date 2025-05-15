# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import bpy
from blender_wizard import wizard_export
from blender_wizard import wizard_tools
import wizard_communicate
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules

# Blender modules


def main(comment=''):
    scene = wizard_export.save_or_save_increment()
    try:

        collections_dic = wizard_tools.get_export_grps('modeling_GRP')
        if collections_dic == dict():
            logger.warning("No group to export...")
            return
        for collection_name in collections_dic.keys():
            logger.info(f"Exporting {collection_name}...")

            collection_obj = bpy.data.collections[collection_name]

            asset_name = os.environ['wizard_asset_name']
            collection_obj.name = asset_name

            export_name = collections_dic[collection_name]

            object_list = wizard_tools.get_all_children(
                collection_obj, meshes=1)
            objects_dic = wizard_tools.remove_export_name_from_names(
                object_list, export_name)

            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(
                int(os.environ['wizard_work_env_id']))

            export_GRP_list = [collection_obj]
            additionnal_objects = wizard_export.trigger_before_export_hook(
                'modeling', exported_string_asset)
            export_GRP_list += additionnal_objects
            wizard_tools.apply_tags(export_GRP_list)

            wizard_export.export(
                'modeling', export_name, exported_string_asset, export_GRP_list, comment=comment)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
