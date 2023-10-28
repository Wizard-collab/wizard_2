# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Substance Painter modules
import substance_painter.resource

def get_export_presets_list():
    presets_list = []
    for shelf in substance_painter.resource.Shelves.all():
        export_presets_dir = f"{shelf.path()}/export-presets"
        if not os.path.isdir(export_presets_dir):
            continue
        for filename in os.listdir(export_presets_dir):
            if not filename.endswith(".spexp"):
                continue
            name = os.path.splitext(filename)[0]
            presets_list.append(name)
    return presets_list

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