# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
import os
from PySide2 import QtWidgets, QtCore, QtGui

# Substance Painter modules
import substance_painter.project
import substance_painter.ui
import substance_painter.logging as logging

# Wizard modules
import wizard_communicate
from substance_painter_wizard import export_ui
from substance_painter_wizard import substance_painter_export

def save():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path:
        if substance_painter.project.is_open():
            if substance_painter.project.needs_saving():
                substance_painter.project.save_as(file_path,
                                                  substance_painter.project.ProjectSaveMode.Full)
            else:
                logging.info("There is nothing to save!")
        else:
            logging.info("No painter project openned!")
            
    if version_id is not None:
        os.environ['wizard_version_id'] = str(version_id)

def export(material, size, file_type):
    substance_painter_export.export_textures(material, size, file_type)

class tool_bar(QtWidgets.QMenu):
    def __init__(self):
        super(tool_bar, self).__init__()
        self.setTitle('Wizard')
        self.export_dialog = export_ui.export_ui()
        substance_painter.ui.add_menu(self)
        save_icon = os.path.abspath("icons/save_increment.png")
        export_icon = os.path.abspath("icons/export.png")
        self.save_action = self.addAction(QtGui.QIcon(save_icon), 'Save')
        self.export_action = self.addAction(QtGui.QIcon(export_icon), 'Export')
        self.save_action.triggered.connect(save)
        self.export_action.triggered.connect(self.show_export_ui)

    def show_export_ui(self):
        if self.export_dialog.exec_() == QtWidgets.QDialog.Accepted:
            material = self.export_dialog.material
            size = self.export_dialog.size
            file_type = self.export_dialog.type
            export(material, size, file_type)

    def __del__(self):
        substance_painter.ui.delete_ui_element(self)
