# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules

# Nuke modules
import nuke

# Wizard modules
from nuke_wizard import wizard_plugin
from nuke_wizard import wizard_tools
from nuke_wizard import wizard_video

nuke.menu('Nuke').addMenu("Wizard")
nuke.menu('Nuke').addCommand("Wizard/Save", "wizard_plugin.save_increment()")
nuke.menu('Nuke').addCommand("Wizard/Export data", "wizard_plugin.export()")

menu = nuke.menu( 'Nuke' ).findItem( 'Wizard' )
menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Import and update all", "wizard_plugin.reference_and_update_all()")

menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Mirror renders to local", "wizard_plugin.update_lighting()")
nuke.menu('Nuke').addCommand("Wizard/Use project renders ( Not recommended )", "wizard_plugin.update_lighting(local=False)")

menu.addSeparator()

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

menu.addMenu("Exr options")
nuke.menu('Nuke').addCommand("Wizard/Exr options/Switch selection to DeepRead", "wizard_tools.switch_selection_to_deepRead()")
nuke.menu('Nuke').addCommand("Wizard/Exr options/Switch selection to Read", "wizard_tools.switch_selection_to_read()")

menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Set frame range", "wizard_plugin.set_frame_range()")
nuke.menu('Nuke').addCommand("Wizard/Set frame range with rolls", "wizard_plugin.set_frame_range(rolls=1)")
nuke.menu('Nuke').addCommand("Wizard/Set image format", "wizard_plugin.set_image_format()")

menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Create video", "wizard_video.invoke_settings_widget()")

wizard_tools.trigger_after_scene_openning_hook()
