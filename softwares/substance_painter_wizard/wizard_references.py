# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Wizard modules
import wizard_communicate

# Substance Painter modules
import substance_painter.logging as logging

def get_mesh_file():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' not in references.keys():
        logging.error("No modeling references found")
        return
    if len(references['modeling']) != 1:
        logging.error("Please reference only ONE modeling export")
        return
    mesh_file_path = references['modeling'][0]['files'][0]
    return mesh_file_path
