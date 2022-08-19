# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules

# Nuke modules
import nuke

# Wizard modules
from nuke_wizard import wizard_plugin
from nuke_wizard import wizard_tools

nuke.menu('Nuke').addMenu("Wizard")
nuke.menu('Nuke').addCommand("Wizard/Save", "wizard_plugin.save_increment()")
nuke.menu('Nuke').addCommand("Wizard/Export data", "wizard_plugin.export()")

menu = nuke.menu( 'Nuke' ).findItem( 'Wizard' )
menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Import and update all", "wizard_plugin.reference_and_update_all()")

menu.addMenu("Import")
nuke.menu('Nuke').addCommand("Wizard/Import/Import all", "wizard_plugin.reference_all()")
nuke.menu('Nuke').addCommand("Wizard/Import/Import custom", "wizard_plugin.reference_custom()")
nuke.menu('Nuke').addCommand("Wizard/Import/Import camera", "wizard_plugin.reference_camera()")
nuke.menu('Nuke').addCommand("Wizard/Import/Import lighting", "wizard_plugin.reference_lighting()")

menu.addMenu("Update")
nuke.menu('Nuke').addCommand("Wizard/Update/Update all", "wizard_plugin.update_all()")
nuke.menu('Nuke').addCommand("Wizard/Update/Update custom", "wizard_plugin.update_custom()")
nuke.menu('Nuke').addCommand("Wizard/Update/Update camera", "wizard_plugin.update_camera()")
nuke.menu('Nuke').addCommand("Wizard/Update/Update lighting", "wizard_plugin.update_lighting()")

menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Set frame range", "wizard_plugin.set_frame_range()")
nuke.menu('Nuke').addCommand("Wizard/Set frame range with rolls", "wizard_plugin.set_frame_range(rolls=1)")
nuke.menu('Nuke').addCommand("Wizard/Set image format", "wizard_plugin.set_image_format()")

wizard_tools.trigger_after_scene_openning_hook()