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

# Wizard modules
import wizard_communicate

# Hook modules
try:
    import substance_painter_hook
except:
    substance_painter_hook = None
    logging.error(str(traceback.format_exc()))
    logging.warning("Can't import substance_painter_hook")

def export_textures(material, size, file_type) :

    # Trigger the before export hook
    if substance_painter_hook:
        try:
            substance_painter_hook.before_export()
        except:
            logging.error(str(traceback.format_exc()))

    if file_type == 'exr':
        bitdepth = '32f'
    else:
        bitdepth = '16'

    export_preset = substance_painter.resource.ResourceID(
                        context="starter_assets",
                        name=material )

    export_name = 'main'
    temp_export_path = os.path.dirname(wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                        export_name))

    # Build the configuration
    config = dict()
    config["exportShaderParams"] = False
    config["exportPath"] = temp_export_path

    config["exportList"] = []
    texture_sets_list = substance_painter.textureset.all_texture_sets()
    for texture_set in texture_sets_list :
        config["exportList"].append( { "rootPath" : texture_set.name() } )

    config["exportPresets"] = [ { "name" : "default", "maps" : [] } ]
    config["defaultExportPreset"] = export_preset.url()
    config["exportParameters"] = [{"parameters":{"paddingAlgorithm": "infinite",
                                        "fileFormat" : file_type,
                                        "bitDepth" : bitdepth,
                                        "sizeLog2" : math.log2(int(size))}}]

    export_result = substance_painter.export.export_project_textures(config)

    if export_result.status != substance_painter.export.ExportStatus.Success:
        logging.error(export_result.message)

    exported_files = []
    for k,v in export_result.textures.items():
        for exported in v:
            exported_files.append(exported)

    export_dir = wizard_communicate.add_export_version(export_name, exported_files, int(os.environ['wizard_version_id']))

    # Trigger the after export hook
    if substance_painter_hook:
        try:
            substance_painter_hook.after_export(export_dir)
        except:
            logging.error(str(traceback.format_exc()))