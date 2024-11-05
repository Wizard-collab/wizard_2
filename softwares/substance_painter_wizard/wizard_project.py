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
import substance_painter.resource
import substance_painter.logging as logging

# Wizard modules
from substance_painter_wizard import wizard_tools

def init_project(mesh_file, template_file):
    ogl_normal_map_format = substance_painter.project.NormalMapFormat.OpenGL
    per_vertex_tangent = substance_painter.project.TangentSpace.PerVertex
    workflow = substance_painter.project.ProjectWorkflow.UVTile

    project_settings = substance_painter.project.Settings(
        import_cameras=True,
        normal_map_format=ogl_normal_map_format,
        tangent_space_mode=per_vertex_tangent,
        project_workflow=workflow)

    substance_painter.project.create(
        mesh_file_path = mesh_file,
        settings = project_settings,
        template_file_path=template_file)

def on_mesh_reload(status: substance_painter.project.ReloadMeshStatus):
    import substance_painter.project
    if status == substance_painter.project.ReloadMeshStatus.SUCCESS:
        logging.info("The mesh was reloaded successfully.")
    else:
        logging.error("The mesh couldn't be reloaded.")

def update_mesh(mesh_file):
    mesh_reloading_settings = substance_painter.project.MeshReloadingSettings(
        import_cameras=True,
        preserve_strokes=True)

    substance_painter.project.reload_mesh(
        mesh_file,
        mesh_reloading_settings,
        on_mesh_reload)

def invoke_init_project_widget(mesh_file):
    widget = init_project_widget(mesh_file)
    widget.exec()

class init_project_widget(QtWidgets.QDialog):
    def __init__(self, mesh_file):
        super(init_project_widget, self).__init__()
        self.mesh_file = mesh_file
        self.setWindowTitle('Wizard init project')
        self.build_ui()
        self.load_templates()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.template_label = QtWidgets.QLabel("Template")
        self.main_layout.addWidget(self.template_label)

        self.templates_comboBox = QtWidgets.QComboBox()
        self.main_layout.addWidget(self.templates_comboBox)

        self.init_button = QtWidgets.QPushButton('Init project')
        self.init_button.setIcon(QtGui.QIcon(os.path.abspath("icons/all.png")))
        self.main_layout.addWidget(self.init_button)
        self.init_button.setDefault(True)
        self.init_button.setAutoDefault(True)

    def load_templates(self):
        self.templates_dic = wizard_tools.get_templates_dic()
        for template in self.templates_dic.keys():
            self.templates_comboBox.addItem(template)

    def init_project(self):
        template_name = self.templates_comboBox.currentText()
        template_file = self.templates_dic[template_name]
        init_project(self.mesh_file, template_file)
        self.close()

    def connect_functions(self):
        self.init_button.clicked.connect(self.init_project)
