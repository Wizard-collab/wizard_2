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
        
        mainMenu = pm.menu(l='Wizard', parent=mainMayaWindow, tearOff=1)
        pm.menuItem(l='Save', c=wizard_plugin.save_increment, i='icons/save_increment.png')
        #pm.menuItem(l='Export data', c=self.save_increment, i='icons/export.png')
        
        import_menu = pm.menuItem(l='Import', subMenu=True, parent=mainMenu, i='icons/import.png')
        
        pm.menuItem(l='Modeling', c=wizard_plugin.reference_modeling, i='icons/import_modeling.png')
        pm.setParent(import_menu, menu=True)

        update_menu = pm.menuItem(l='Update', subMenu=True, parent=mainMenu, i='icons/reload.png')
        pm.menuItem(l='Modeling', c=wizard_plugin.update_modeling, i='icons/import_modeling.png')
        pm.setParent(update_menu, menu=True)

    def export(self, *args):
        pass
