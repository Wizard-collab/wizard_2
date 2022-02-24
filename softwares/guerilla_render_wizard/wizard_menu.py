# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_plugin

# Guerilla modules
from guerilla import command

class menu():
    class save_increment(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.save_increment()

    class import_modeling(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.reference_modeling()

    class import_texturing(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_texturing()

    class update_modeling(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_modeling()

    class update_texturing(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_texturing()

    cmd = save_increment('Save', 'icons/save_increment.png')
    cmd.install('Wizard')
    command.addseparator ('Wizard')
    cmd = import_modeling('Import modeling', 'icons/modeling.png')
    cmd.install('Wizard', ' Import')
    cmd = import_texturing('Import texturing', 'icons/texturing.png')
    cmd.install('Wizard', ' Import')
    cmd = update_modeling('Update modeling', 'icons/modeling.png')
    cmd.install('Wizard', ' Update')
    cmd = update_texturing('Update texturing', 'icons/texturing.png')
    cmd.install('Wizard', ' Update')
    