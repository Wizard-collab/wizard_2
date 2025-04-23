# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy
import bpy.utils.previews

# Wizard modules
from blender_wizard import wizard_plugin
from blender_wizard import wizard_video


class save_increment(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.save_increment"
    bl_label = "Save"
    bl_description = "Save file in Wizard's hierarchy"

    def execute(self, context):
        wizard_plugin.save_increment()
        return {'FINISHED'}


class export(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.export"
    bl_label = "Export data"
    bl_description = "Export file in Wizard's hierarchy"

    def execute(self, context):
        wizard_plugin.export()
        return {'FINISHED'}


class setup_LD(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.setup_ld"
    bl_label = "Setup LD"
    bl_description = "Setup the render settings for render in Low definition"

    def execute(self, context):
        wizard_plugin.setup_render('LD')
        return {'FINISHED'}


class setup_FML(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.setup_fml"
    bl_label = "Setup FML"
    bl_description = "Setup the render settings for render first, middle and last frame"

    def execute(self, context):
        wizard_plugin.setup_render('FML')
        return {'FINISHED'}


class setup_HD(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.setup_hd"
    bl_label = "Setup HD"
    bl_description = "Setup the render settings for render in high definition"

    def execute(self, context):
        wizard_plugin.setup_render('HD')
        return {'FINISHED'}


class export_camera(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.export_camera"
    bl_label = "Export camera"
    bl_description = "Export camera file in Wizard's hierarchy"

    def execute(self, context):
        wizard_plugin.export_camera()
        return {'FINISHED'}


class import_and_update_all(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_and_update_all"
    bl_label = "Import and update all"
    bl_description = "Import and update all references"

    def execute(self, context):
        wizard_plugin.import_and_update_all()
        return {'FINISHED'}


class import_modeling(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_modeling"
    bl_label = "Import modeling"
    bl_description = "Import modleing"

    def execute(self, context):
        wizard_plugin.reference_modeling()
        return {'FINISHED'}


class import_shading(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_shading"
    bl_label = "Import shading"
    bl_description = "Import shading"

    def execute(self, context):
        wizard_plugin.reference_shading()
        return {'FINISHED'}


class import_rigging(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_rigging"
    bl_label = "Import rigging"
    bl_description = "Import rigging"

    def execute(self, context):
        wizard_plugin.reference_rigging()
        return {'FINISHED'}


class import_grooming(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_grooming"
    bl_label = "Import grooming"
    bl_description = "Import grooming"

    def execute(self, context):
        wizard_plugin.reference_grooming()
        return {'FINISHED'}


class import_camrig(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_camrig"
    bl_label = "Import camrig"
    bl_description = "Import camrig"

    def execute(self, context):
        wizard_plugin.reference_camrig()
        return {'FINISHED'}


class import_layout(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_layout"
    bl_label = "Import layout"
    bl_description = "Import layout"

    def execute(self, context):
        wizard_plugin.reference_layout()
        return {'FINISHED'}


class import_animation(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_animation"
    bl_label = "Import animation"
    bl_description = "Import animation"

    def execute(self, context):
        wizard_plugin.reference_animation()
        return {'FINISHED'}


class import_camera(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_camera"
    bl_label = "Import camera"
    bl_description = "Import camera"

    def execute(self, context):
        wizard_plugin.reference_camera()
        return {'FINISHED'}


class import_custom(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_custom"
    bl_label = "Import custom"
    bl_description = "Import custom"

    def execute(self, context):
        wizard_plugin.reference_custom()
        return {'FINISHED'}


class import_texturing(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_texturing"
    bl_label = "Import texturing"
    bl_description = "Import texturing and create shader"

    def execute(self, context):
        wizard_plugin.reference_texturing()
        return {'FINISHED'}


class update_modeling(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_modeling"
    bl_label = "Update modeling"
    bl_description = "Update existing modeling"

    def execute(self, context):
        wizard_plugin.update_modeling()
        return {'FINISHED'}


class update_shading(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_shading"
    bl_label = "Update shading"
    bl_description = "Update existing shading"

    def execute(self, context):
        wizard_plugin.update_shading()
        return {'FINISHED'}


class update_rigging(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_rigging"
    bl_label = "Update rigging"
    bl_description = "Update existing rigging"

    def execute(self, context):
        wizard_plugin.update_rigging()
        return {'FINISHED'}


class update_grooming(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_grooming"
    bl_label = "Update grooming"
    bl_description = "Update existing grooming"

    def execute(self, context):
        wizard_plugin.update_grooming()
        return {'FINISHED'}


class update_camrig(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_camrig"
    bl_label = "Update camrig"
    bl_description = "Update existing camrig"

    def execute(self, context):
        wizard_plugin.update_camrig()
        return {'FINISHED'}


class update_layout(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_layout"
    bl_label = "Update layout"
    bl_description = "Update existing layout"

    def execute(self, context):
        wizard_plugin.update_layout()
        return {'FINISHED'}


class update_animation(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_animation"
    bl_label = "Update animation"
    bl_description = "Update existing animation"

    def execute(self, context):
        wizard_plugin.update_animation()
        return {'FINISHED'}


class update_camera(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_camera"
    bl_label = "Update camera"
    bl_description = "Update existing camera"

    def execute(self, context):
        wizard_plugin.update_camera()
        return {'FINISHED'}


class update_custom(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_custom"
    bl_label = "Update custom"
    bl_description = "Update existing_custom"

    def execute(self, context):
        wizard_plugin.update_custom()
        return {'FINISHED'}


class update_texturing(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.update_texturing"
    bl_label = "Update texturing"
    bl_description = "Update existing texturing in shaders"

    def execute(self, context):
        wizard_plugin.update_texturing()
        return {'FINISHED'}


class set_image_size(bpy.types.Operator):
    '''The set image size operator that call wizard function'''

    bl_idname = "wizard.set_image_size"
    bl_label = "Set image size"
    bl_description = "Apply wizard project image size"

    def execute(self, context):
        wizard_plugin.set_image_size()
        return {'FINISHED'}


class set_frame_rate(bpy.types.Operator):

    bl_idname = "wizard.set_frame_rate"
    bl_label = "Set frame rate"
    bl_description = "Apply wizard project frame rate"

    def execute(self, context):
        wizard_plugin.set_frame_rate()
        return {'FINISHED'}


class set_frame_range(bpy.types.Operator):

    bl_idname = "wizard.set_frame_range"
    bl_label = "Set frame range"
    bl_description = "Apply wizard project frame range"

    def execute(self, context):
        wizard_plugin.set_frame_range()
        return {'FINISHED'}


class set_frame_range_with_rolls(bpy.types.Operator):

    bl_idname = "wizard.set_frame_range_with_rolls"
    bl_label = "Set frame range with rolls"
    bl_description = "Apply wizard project frame range with rolls"

    def execute(self, context):
        wizard_plugin.set_frame_range_with_rolls()
        return {'FINISHED'}


class create_video(bpy.types.Operator):

    bl_idname = "wizard.create_video"
    bl_label = "Create video"
    bl_description = "Create a video in wizard"

    def execute(self, context):
        wizard_video.invoke_settings_widget()
        return {'FINISHED'}


class TOPBAR_MT_wizard_import_submenu(bpy.types.Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.import_modeling",
                        icon_value=wizard_icons["modeling"].icon_id)
        layout.operator("wizard.import_shading",
                        icon_value=wizard_icons["shading"].icon_id)
        layout.operator("wizard.import_rigging",
                        icon_value=wizard_icons["rigging"].icon_id)
        layout.operator("wizard.import_grooming",
                        icon_value=wizard_icons["grooming"].icon_id)
        layout.operator("wizard.import_texturing",
                        icon_value=wizard_icons["texturing"].icon_id)
        layout.operator("wizard.import_layout",
                        icon_value=wizard_icons["layout"].icon_id)
        layout.operator("wizard.import_animation",
                        icon_value=wizard_icons["animation"].icon_id)
        layout.operator("wizard.import_camera",
                        icon_value=wizard_icons["camera"].icon_id)
        layout.operator("wizard.import_custom",
                        icon_value=wizard_icons["custom"].icon_id)
        layout.operator("wizard.import_camrig",
                        icon_value=wizard_icons["camrig"].icon_id)


class TOPBAR_MT_wizard_update_submenu(bpy.types.Menu):
    bl_label = "Update"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.update_modeling",
                        icon_value=wizard_icons["modeling"].icon_id)
        layout.operator("wizard.update_shading",
                        icon_value=wizard_icons["shading"].icon_id)
        layout.operator("wizard.update_rigging",
                        icon_value=wizard_icons["rigging"].icon_id)
        layout.operator("wizard.update_grooming",
                        icon_value=wizard_icons["grooming"].icon_id)
        layout.operator("wizard.update_texturing",
                        icon_value=wizard_icons["texturing"].icon_id)
        layout.operator("wizard.update_layout",
                        icon_value=wizard_icons["layout"].icon_id)
        layout.operator("wizard.update_animation",
                        icon_value=wizard_icons["animation"].icon_id)
        layout.operator("wizard.update_camera",
                        icon_value=wizard_icons["camera"].icon_id)
        layout.operator("wizard.update_custom",
                        icon_value=wizard_icons["custom"].icon_id)
        layout.operator("wizard.update_camrig",
                        icon_value=wizard_icons["camrig"].icon_id)


class TOPBAR_MT_wizard_render_submenu(bpy.types.Menu):
    bl_label = "Render"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.setup_ld",
                        icon_value=wizard_icons["rendering"].icon_id)
        layout.operator("wizard.setup_fml",
                        icon_value=wizard_icons["rendering"].icon_id)
        layout.operator("wizard.setup_hd",
                        icon_value=wizard_icons["rendering"].icon_id)


class TOPBAR_MT_wizard_menu(bpy.types.Menu):
    bl_label = "Wizard"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.save_increment",
                        icon_value=wizard_icons["save_increment"].icon_id)
        layout.operator("wizard.export",
                        icon_value=wizard_icons["export"].icon_id)

        layout.separator()

        if os.environ['wizard_stage_name'] in ['shading', 'lighting', 'rendering', 'compositing']:
            layout.menu("TOPBAR_MT_wizard_render_submenu",
                        icon_value=wizard_icons["rendering"].icon_id)
            layout.separator()

        stage_name = os.environ['wizard_stage_name']
        camera_export_stage_names = ['animation', 'layout']
        if stage_name in camera_export_stage_names:
            layout.operator("wizard.export_camera",
                            icon_value=wizard_icons["export"].icon_id)
        layout.operator("wizard.import_and_update_all",
                        icon_value=wizard_icons["import_and_update_all"].icon_id)
        layout.menu("TOPBAR_MT_wizard_import_submenu",
                    icon_value=wizard_icons["import"].icon_id)
        layout.menu("TOPBAR_MT_wizard_update_submenu",
                    icon_value=wizard_icons["update"].icon_id)

        layout.separator()

        layout.operator("wizard.set_image_size",
                        icon_value=wizard_icons["set_image_size"].icon_id)
        layout.operator("wizard.set_frame_rate",
                        icon_value=wizard_icons["set_frame_rate"].icon_id)
        layout.operator("wizard.set_frame_range",
                        icon_value=wizard_icons["set_frame_range"].icon_id)
        layout.operator("wizard.set_frame_range_with_rolls",
                        icon_value=wizard_icons["set_frame_range"].icon_id)

        layout.separator()

        layout.operator("wizard.create_video",
                        icon_value=wizard_icons["video"].icon_id)

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_wizard_menu")


classes = (save_increment,
           export,
           setup_LD,
           setup_FML,
           setup_HD,
           export_camera,
           import_and_update_all,
           import_modeling,
           import_shading,
           import_rigging,
           import_grooming,
           import_layout,
           import_animation,
           import_camera,
           import_custom,
           import_camrig,
           import_texturing,
           update_texturing,
           update_modeling,
           update_shading,
           update_rigging,
           update_grooming,
           update_layout,
           update_animation,
           update_camera,
           update_custom,
           update_camrig,
           set_image_size,
           set_frame_rate,
           set_frame_range,
           set_frame_range_with_rolls,
           create_video,
           TOPBAR_MT_wizard_import_submenu,
           TOPBAR_MT_wizard_update_submenu,
           TOPBAR_MT_wizard_render_submenu,
           TOPBAR_MT_wizard_menu)


def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_wizard_menu.menu_draw)

    # Register icons
    global wizard_icons
    wizard_icons = bpy.utils.previews.new()
    wizard_icons.load("save_increment", 'icons/save_increment.png', 'IMAGE')
    wizard_icons.load("import_and_update_all", 'icons/all.png', 'IMAGE')
    wizard_icons.load("export", 'icons/export.png', 'IMAGE')
    wizard_icons.load("import", 'icons/import.png', 'IMAGE')
    wizard_icons.load("update", 'icons/update.png', 'IMAGE')
    wizard_icons.load("modeling", 'icons/modeling.png', 'IMAGE')
    wizard_icons.load("shading", 'icons/shading.png', 'IMAGE')
    wizard_icons.load("rigging", 'icons/rigging.png', 'IMAGE')
    wizard_icons.load("grooming", 'icons/grooming.png', 'IMAGE')
    wizard_icons.load("layout", 'icons/wlayout.png', 'IMAGE')
    wizard_icons.load("animation", 'icons/animation.png', 'IMAGE')
    wizard_icons.load("camera", 'icons/camera.png', 'IMAGE')
    wizard_icons.load("custom", 'icons/custom.png', 'IMAGE')
    wizard_icons.load("camrig", 'icons/camera_rig.png', 'IMAGE')
    wizard_icons.load("texturing", 'icons/texturing.png', 'IMAGE')
    wizard_icons.load("rendering", 'icons/rendering.png', 'IMAGE')
    wizard_icons.load("set_image_size", 'icons/set_image_size.png', 'IMAGE')
    wizard_icons.load("set_frame_rate", 'icons/set_frame_rate.png', 'IMAGE')
    wizard_icons.load("set_frame_range", 'icons/set_frame_range.png', 'IMAGE')
    wizard_icons.load("video", 'icons/video.png', 'IMAGE')


def unregister():
    # Unregister classes
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_wizard_menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Unregister icons
    global custom_icons
    bpy.utils.previews.remove(wizard_icons)


if __name__ == "__main__":
    register()
