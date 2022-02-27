# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Maya modules
import pymel.core as pm

# Wizard modules
from maya_wizard import wizard_plugin

class menu():
    def __init__(self):
        self.createMenu()
    
    def createMenu(self):

        mainMayaWindow = pm.language.melGlobals['gMainWindow'] 
        
        mainMenu = pm.menu(l='Wizard', parent=mainMayaWindow, tearOff=0)
        pm.menuItem(l='Save', c=wizard_plugin.save_increment, i='icons/save_increment.png')
        pm.menuItem(l='Export data', c=wizard_plugin.export, i='icons/export.png')
        
        pm.menuItem( divider=True )
        
        import_menu = pm.menuItem(l='Import', subMenu=True, parent=mainMenu, i='icons/import.png')
        
        pm.menuItem(l='Import modeling', c=wizard_plugin.reference_modeling, i='icons/modeling.png')
        pm.setParent(import_menu, menu=True)

        pm.menuItem(l='Import rigging', c=wizard_plugin.reference_rigging, i='icons/rigging.png')
        pm.setParent(import_menu, menu=True)

        update_menu = pm.menuItem(l='Update', subMenu=True, parent=mainMenu, i='icons/update.png')
        
        pm.menuItem(l='Update modeling', c=wizard_plugin.update_modeling, i='icons/modeling.png')
        pm.setParent(update_menu, menu=True)
        pm.menuItem(l='Update rigging', c=wizard_plugin.update_rigging, i='icons/rigging.png')
        pm.setParent(update_menu, menu=True)

        pm.menuItem(divider=True, parent=mainMenu)

        LOD_menu = pm.menuItem(l='LOD', subMenu=True, parent=mainMenu, i='')
        pm.menuItem(l='LOD1', c=wizard_plugin.LOD1, i='')
        pm.setParent(LOD_menu, menu=True)
        pm.menuItem(l='LOD2', c=wizard_plugin.LOD2, i='')
        pm.setParent(LOD_menu, menu=True)
        pm.menuItem(l='LOD3', c=wizard_plugin.LOD3, i='')
        pm.setParent(LOD_menu, menu=True)
