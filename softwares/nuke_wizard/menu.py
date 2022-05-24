# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules

# Nuke modules
import nuke

# Wizard modules
from nuke_wizard import wizard_plugin

nuke.menu('Nuke').addMenu("Wizard")
nuke.menu('Nuke').addCommand("Wizard/Save", "wizard_plugin.save_increment()")

menu = nuke.menu( 'Nuke' ).findItem( 'Wizard' )
menu.addSeparator()

nuke.menu('Nuke').addCommand("Wizard/Set frame range", "wizard_plugin.set_frame_range()")
nuke.menu('Nuke').addCommand("Wizard/Set frame range with rolls", "wizard_plugin.set_frame_range(rolls=1)")
nuke.menu('Nuke').addCommand("Wizard/Set image format", "wizard_plugin.set_image_format()")
