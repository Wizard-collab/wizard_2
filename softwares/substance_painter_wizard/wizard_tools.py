# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Substance Painter modules
import substance_painter.resource

def get_export_presets_list():
    presets_list = []
    all_presets = substance_painter.export.list_resource_export_presets()
    for preset in all_presets:
        presets_list.append(preset.resource_id.name)
    return presets_list

def get_export_preset_url(preset_name):
    all_presets = substance_painter.export.list_resource_export_presets()
    for preset in all_presets:
        if preset.resource_id.name == preset_name:
            return preset.resource_id.url()

def get_templates_dic():
    templates_dic = dict()
    for shelf in substance_painter.resource.Shelves.all():
        templates_dir = f"{shelf.path()}/templates"
        if not os.path.isdir(templates_dir):
            continue
        for filename in os.listdir(templates_dir):
            if not filename.endswith(".spt"):
                continue
            name = os.path.splitext(filename)[0]
            templates_dic[name] = os.path.join(templates_dir, filename)
    return templates_dic