# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
import os
import shutil
try:
    from PySide6 import QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtWidgets, QtGui
# Substance Painter modules
import substance_painter.project
import substance_painter.ui
import substance_painter.logging as logging

# Wizard modules
import wizard_communicate
from substance_painter_wizard import export_ui
from substance_painter_wizard import substance_painter_export
from substance_painter_wizard import wizard_project
from substance_painter_wizard import wizard_reference

def save():
    if not substance_painter.project.is_open():
        logging.info("No painter project openned!")
        return
    if not substance_painter.project.needs_saving():
        logging.info("There is nothing to save!")
        return
    # Save as local
    local_path = wizard_communicate.get_local_path()
    if local_path is None:
        logging.warning("Please set a local path, skipping save.")
        return
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if not file_path:
        logging.error("No file path found")
        return
    project_path = wizard_communicate.get_project_path()
    local_file_path = local_path+file_path[len(project_path):]
    if local_file_path is None:
        logging.error("Local path not found, no file path to save to.")
        return
    substance_painter.project.save_as(local_file_path,
                                      substance_painter.project.ProjectSaveMode.Full)
            
    if version_id is not None:
        os.environ['wizard_version_id'] = str(version_id)

def copy_save(evt):
    saved_file = substance_painter.project.file_path()
    # Copy to network
    local_path = wizard_communicate.get_local_path()
    project_path = wizard_communicate.get_project_path()
    if os.environ["wizard_launch_mode"] == 'gui':
        wizard_communicate.screen_over_version(int(os.environ['wizard_version_id']))
    if not saved_file.startswith(local_path):
        return
    network_file_path = project_path+saved_file[len(local_path):]
    if not os.path.isdir(os.path.dirname(network_file_path)):
        logging.error(f"{os.path.dirname(network_file_path)} not found. Skipping copy to project")
        return
    logging.info(f"Copying {saved_file} to {network_file_path}")
    shutil.copyfile(saved_file, network_file_path)

def export(material, size, file_type):
    save_or_save_increment()
    substance_painter_export.export_textures(material, size, file_type)

def save_or_save_increment():
    if substance_painter.project.name() is None:
        save()
    else:
        logging.info("Saving file")
        substance_painter.project.save()
        copy_save(None)

def init_project():
    mesh_file_path = wizard_reference.get_mesh_file()
    if mesh_file_path:
        wizard_project.invoke_init_project_widget(mesh_file_path)

def update_mesh():
    mesh_file_path = wizard_reference.get_mesh_file()
    if mesh_file_path:
        wizard_project.update_mesh(mesh_file_path)

def import_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.import_texturing(reference)

class tool_bar(QtWidgets.QMenu):
    def __init__(self):
        super(tool_bar, self).__init__()
        self.setTitle('Wizard')
        self.export_dialog = export_ui.export_ui()
        substance_painter.ui.add_menu(self)
        save_icon = os.path.abspath("icons/save_increment.png")
        export_icon = os.path.abspath("icons/export.png")
        magic_icon = os.path.abspath("icons/all.png")
        modeling_icon = os.path.abspath("icons/modeling.png")
        texturing_icon = os.path.abspath("icons/texturing.png")
        import_icon = os.path.abspath("icons/import.png")
        update_icon = os.path.abspath("icons/update.png")
        self.save_action = self.addAction(QtGui.QIcon(save_icon), 'Save')
        self.export_action = self.addAction(QtGui.QIcon(export_icon), 'Export')
        self.init_project_action = self.addAction(QtGui.QIcon(magic_icon), 'Init project')
        self.import_menu = self.addMenu(QtGui.QIcon(import_icon), 'Import')
        self.import_texturing_action = self.import_menu.addAction(QtGui.QIcon(texturing_icon), 'Import/Update texturing')
        self.update_menu = self.addMenu(QtGui.QIcon(update_icon), 'Update')
        self.update_modeling_action = self.update_menu.addAction(QtGui.QIcon(modeling_icon), 'Update modeling')
        self.save_action.triggered.connect(save)
        self.export_action.triggered.connect(self.show_export_ui)
        self.init_project_action.triggered.connect(init_project)
        self.import_texturing_action.triggered.connect(import_texturing)
        self.update_modeling_action.triggered.connect(update_mesh)

    def show_export_ui(self):
        if self.export_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            material = self.export_dialog.material
            size = self.export_dialog.size
            file_type = self.export_dialog.type
            export(material, size, file_type)

    def __del__(self):
        substance_painter.ui.delete_ui_element(self)
