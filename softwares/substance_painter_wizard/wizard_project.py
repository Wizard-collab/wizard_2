# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Substance Painter modules
import substance_painter.project
import substance_painter.logging as logging

def init_project(mesh_file):
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
        settings = project_settings)

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