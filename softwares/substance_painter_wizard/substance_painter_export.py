# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import math
import traceback

# Substance Painter modules
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import substance_painter.logging as logging
import substance_painter.resource

# Wizard modules
import wizard_communicate
import wizard_hooks
from substance_painter_wizard import wizard_tools


def export_textures(material, size, file_type, comment=''):
    if file_type == 'exr':
        bitdepth = '32f'
    else:
        bitdepth = '16'

    export_name = 'main'
    temp_export_path = os.path.dirname(wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                         export_name)).replace('\\', '/')

    texture_sets = substance_painter.textureset.all_texture_sets()
    export_list = []
    for texture_set in texture_sets:
        export_list.append({"rootPath": texture_set.name()})

    export_config = {
        "exportShaderParams": False,
        "exportPath": temp_export_path,
        "exportList": export_list,
        "exportPresets": [{"name": "default", "maps": []}],
        "defaultExportPreset": wizard_tools.get_export_preset_url(material),
        "exportParameters": [{"parameters": {"paddingAlgorithm": "infinite",
                                             "dithering": True,
                                             "fileFormat": file_type,
                                             "bitDepth": bitdepth,
                                             "sizeLog2": int(math.log2(int(size)))}}],
    }

    try:
        export_result = substance_painter.export.export_project_textures(
            export_config)
    except:
        logging.error(str(traceback.format_exc()))
        export_result = None

    if export_result:
        exported_files = []
        files = os.listdir(temp_export_path)
        for file in files:
            exported_files.append(os.path.join(temp_export_path, file))

        export_dir = wizard_communicate.add_export_version(export_name,
                                                           exported_files,
                                                           int(os.environ['wizard_work_env_id']),
                                                           int(os.environ['wizard_version_id']),
                                                           comment=comment)

        trigger_after_export_hook('texturing', export_dir)


def trigger_after_export_hook(stage_name, export_dir):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks(
        'substance_painter', stage_name, export_dir, string_asset, string_asset)
