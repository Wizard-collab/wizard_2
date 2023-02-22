# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy
import bpy.utils.previews

# Wizard modules
from blender_wizard import wizard_plugin
from blender_wizard import wizard_tools

bl_info = {
    "name": "Wizard",
    "author": "Auguste Lefort",
    "version": (2, 0),
    "blender": (2, 93, 3),
    "location": "View3D > Wizard",
    "description": "Provide Wizard's tools",
    "warning": "",
    "doc_url": "wizard-pipeline-manager.webflow.io",
    "category": "User",
}

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

class import_modeling(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_modeling"
    bl_label = "Import modeling"
    bl_description = "Import modleing ( hard )"
    
    def execute(self, context):
        wizard_plugin.reference_modeling()
        return {'FINISHED'}

class import_layout(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_layout"
    bl_label = "Import layout"
    bl_description = "Import layout ( hard )"
    
    def execute(self, context):
        wizard_plugin.reference_layout()
        return {'FINISHED'}

class import_animation(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_animation"
    bl_label = "Import animation"
    bl_description = "Import animation ( hard )"
    
    def execute(self, context):
        wizard_plugin.reference_animation()
        return {'FINISHED'}

class import_texturing(bpy.types.Operator):
    '''The save operator that call wizard function'''

    bl_idname = "wizard.import_texturing"
    bl_label = "Import texturing"
    bl_description = "Import texturing and create shader"
    
    def execute(self, context):
        wizard_plugin.reference_texturing()
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

class clear_all_materials(bpy.types.Operator):
    '''Clear all materials of selection'''

    bl_idname = "wizard.clear_all_materials"
    bl_label = "Clear all materials"
    bl_description = "Clear all materials of selected object and children"
    
    def execute(self, context):
        wizard_tools.clear_all_materials_of_selection()
        return {'FINISHED'}

class TOPBAR_MT_wizard_import_submenu(bpy.types.Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.import_modeling", icon_value=wizard_icons["modeling"].icon_id)
        layout.operator("wizard.import_texturing", icon_value=wizard_icons["texturing"].icon_id)
        layout.operator("wizard.import_layout", icon_value=wizard_icons["layout"].icon_id)
        layout.operator("wizard.import_animation", icon_value=wizard_icons["animation"].icon_id)

class TOPBAR_MT_wizard_update_submenu(bpy.types.Menu):
    bl_label = "Update"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.update_texturing", icon_value=wizard_icons["texturing"].icon_id)

class TOPBAR_MT_wizard_menu(bpy.types.Menu):
    bl_label = "Wizard"

    def draw(self, context):
        layout = self.layout
        layout.operator("wizard.save_increment", icon_value=wizard_icons["save_increment"].icon_id)
        
        layout.separator()

        layout.operator("wizard.export", icon_value=wizard_icons["export"].icon_id)
        layout.menu("TOPBAR_MT_wizard_import_submenu", icon_value=wizard_icons["import"].icon_id)
        layout.menu("TOPBAR_MT_wizard_update_submenu", icon_value=wizard_icons["update"].icon_id)

        layout.separator()

        layout.operator("wizard.set_image_size", icon_value=wizard_icons["set_image_size"].icon_id)
        layout.operator("wizard.clear_all_materials", icon_value=wizard_icons["clear_all_materials"].icon_id)

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_wizard_menu")

classes = (save_increment,
                export,
                import_modeling,
                import_layout,
                import_animation,
                import_texturing,
                update_texturing,
                set_image_size,
                clear_all_materials,
                TOPBAR_MT_wizard_import_submenu,
                TOPBAR_MT_wizard_update_submenu,
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
    wizard_icons.load("export", 'icons/export.png', 'IMAGE')
    wizard_icons.load("import", 'icons/import.png', 'IMAGE')
    wizard_icons.load("update", 'icons/update.png', 'IMAGE')
    wizard_icons.load("modeling", 'icons/modeling.png', 'IMAGE')
    wizard_icons.load("layout", 'icons/wlayout.png', 'IMAGE')
    wizard_icons.load("animation", 'icons/animation.png', 'IMAGE')
    wizard_icons.load("texturing", 'icons/texturing.png', 'IMAGE')
    wizard_icons.load("set_image_size", 'icons/set_image_size.png', 'IMAGE')
    wizard_icons.load("clear_all_materials", 'icons/remove_all_materials.png', 'IMAGE')

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