# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# PYthon modules
import os

# Maya modules
import pymel.core as pm

# Wizard modules
from maya_wizard import wizard_plugin
from maya_wizard import wizard_video

class menu():
    def __init__(self):
        self.createMenu()
    
    def createMenu(self):

        mainMayaWindow = pm.language.melGlobals['gMainWindow'] 
        
        mainMenu = pm.menu(l='Wizard', parent=mainMayaWindow, tearOff=0)
        pm.menuItem(l='Save', c=wizard_plugin.save_increment, i='icons/save_increment.png')
        pm.menuItem(l='Export data', c=wizard_plugin.export, i='icons/export.png')

        stage_name = os.environ['wizard_stage_name']
        camera_export_stage_names = ['animation', 'layout']
        if stage_name in camera_export_stage_names:
            pm.menuItem(l='Export camera', c=wizard_plugin.export_camera, i='icons/export.png')
        
        pm.menuItem(divider=True)
        
        pm.menuItem(l='Import and update all', c=wizard_plugin.reference_and_update_all, i='icons/all.png', parent=mainMenu)

        import_menu = pm.menuItem(l='Import', subMenu=True, parent=mainMenu, i='icons/import.png')
        
        pm.menuItem(l='Import all', c=wizard_plugin.reference_all, i='icons/all.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import modeling', c=wizard_plugin.reference_modeling, i='icons/modeling.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import rigging', c=wizard_plugin.reference_rigging, i='icons/rigging.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import grooming', c=wizard_plugin.reference_grooming, i='icons/grooming.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import custom', c=wizard_plugin.reference_custom, i='icons/custom.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import camrig', c=wizard_plugin.reference_camrig, i='icons/camera_rig.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import layout', c=wizard_plugin.reference_layout, i='icons/wlayout.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import animation', c=wizard_plugin.reference_animation, i='icons/animation.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import cfx', c=wizard_plugin.reference_cfx, i='icons/cfx.png')
        pm.setParent(import_menu, menu=True)
        pm.menuItem(l='Import camera', c=wizard_plugin.reference_camera, i='icons/camera.png')
        pm.setParent(import_menu, menu=True)

        update_menu = pm.menuItem(l='Update', subMenu=True, parent=mainMenu, i='icons/update.png')
        
        pm.menuItem(l='Update all', c=wizard_plugin.update_all, i='icons/all.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update modeling', c=wizard_plugin.update_modeling, i='icons/modeling.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update rigging', c=wizard_plugin.update_rigging, i='icons/rigging.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update grooming', c=wizard_plugin.update_grooming, i='icons/grooming.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update custom', c=wizard_plugin.update_custom, i='icons/custom.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update camrig', c=wizard_plugin.update_camrig, i='icons/camera_rig.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update layout', c=wizard_plugin.update_layout, i='icons/wlayout.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update animation', c=wizard_plugin.update_animation, i='icons/animation.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update cfx', c=wizard_plugin.update_cfx, i='icons/cfx.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update camera', c=wizard_plugin.update_camera, i='icons/camera.png')
        pm.setParent(import_menu, menu=True)

        pm.menuItem(divider=True, parent=mainMenu)

        LOD_menu = pm.menuItem(l='LOD', subMenu=True, parent=mainMenu, i='')
        pm.menuItem(l='LOD1', c=wizard_plugin.LOD1, i='')
        pm.setParent(LOD_menu, menu=True)
        pm.menuItem(l='LOD2', c=wizard_plugin.LOD2, i='')
        pm.setParent(LOD_menu, menu=True)
        pm.menuItem(l='LOD3', c=wizard_plugin.LOD3, i='')
        pm.setParent(LOD_menu, menu=True)

        pm.menuItem(divider=True, parent=mainMenu)

        pm.menuItem(l='Set image size', c=wizard_plugin.set_image_format, i='icons/set_image_size.png', parent=mainMenu)
        pm.menuItem(l='Set frame range', c=wizard_plugin.set_frame_range, i='icons/set_frame_range.png', parent=mainMenu)
        pm.menuItem(l='Set frame range with rolls', c=wizard_plugin.set_frame_range_with_rolls, i='icons/set_frame_range.png', parent=mainMenu)

        pm.menuItem(divider=True, parent=mainMenu)

        pm.menuItem(l='Create video', c=wizard_video.create_video, i='icons/video.png', parent=mainMenu)

