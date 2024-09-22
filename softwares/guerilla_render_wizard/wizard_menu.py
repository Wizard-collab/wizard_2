# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_plugin
from guerilla_render_wizard import wizard_render

# Guerilla modules
from guerilla import command

class menu():
    class save_increment(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.save_increment()

    class export_data(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.export()

    class import_and_update_all(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.reference_and_update_all()

    class import_all(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.reference_all()

    class import_modeling(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_modeling()

    class import_grooming(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_grooming()

    class import_texturing(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_texturing()

    class import_shading(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_shading()

    class import_custom(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_custom()

    class import_layout(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_layout()

    class import_animation(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_animation()

    class import_cfx(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_cfx()

    class import_fx(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_fx()

    class import_camera(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.import_camera()

    class update_all(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_all()

    class update_modeling(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_modeling()

    class update_grooming(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_grooming()

    class update_texturing(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_texturing()

    class update_shading(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_shading()

    class update_custom(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_custom()

    class update_layout(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_layout()

    class update_animation(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_animation()

    class update_cfx(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_cfx()

    class update_fx(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_fx()

    class update_camera(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.update_camera()

    class set_image_format(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.set_image_format()

    class set_frame_rate(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.set_frame_rate()

    class set_frame_range(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.set_frame_range()

    class set_frame_range_with_rolls(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.set_frame_range_with_rolls()

    class setup_render_FML(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.setup_render('FML')

    class setup_render_LD(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.setup_render('LD')

    class setup_render_HD(command):
        @staticmethod
        def action(luaObj, window, x, y, suffix):
            wizard_plugin.setup_render('HD')

    cmd = save_increment('Save', 'icons/save_increment.png')
    cmd.install('Wizard')
    
    if os.environ['wizard_stage_name'] not in ['rendering']:
        cmd = export_data('Export data', 'icons/export.png')
        cmd.install('Wizard')


    if os.environ['wizard_stage_name'] in ['shading', 'lighting', 'rendering']:
        command.addseparator ('Wizard')
        cmd = setup_render_FML('Setup render FML', 'icons/export.png')
        cmd.install('Wizard', 'Rendering')
        cmd = setup_render_LD('Setup render LD', 'icons/export.png')
        cmd.install('Wizard', 'Rendering')
        cmd = setup_render_HD('Setup render HD', 'icons/export.png')
        cmd.install('Wizard', 'Rendering')

    command.addseparator ('Wizard')
    cmd = import_and_update_all('Import and update all', 'icons/all.png')
    cmd.install('Wizard')
    cmd = import_all('Import all', 'icons/all.png')
    cmd.install('Wizard', ' Import')
    cmd = import_modeling('Import modeling', 'icons/modeling.png')
    cmd.install('Wizard', ' Import')
    cmd = import_grooming('Import grooming', 'icons/grooming.png')
    cmd.install('Wizard', ' Import')
    cmd = import_texturing('Import texturing', 'icons/texturing.png')
    cmd.install('Wizard', ' Import')
    cmd = import_shading('Import shading', 'icons/shading.png')
    cmd.install('Wizard', ' Import')
    cmd = import_custom('Import custom', 'icons/custom.png')
    cmd.install('Wizard', ' Import')
    cmd = import_layout('Import layout', 'icons/wlayout.png')
    cmd.install('Wizard', ' Import')
    cmd = import_animation('Import animation', 'icons/animation.png')
    cmd.install('Wizard', ' Import')
    cmd = import_cfx('Import cfx', 'icons/cfx.png')
    cmd.install('Wizard', ' Import')
    cmd = import_fx('Import fx', 'icons/fx.png')
    cmd.install('Wizard', ' Import')
    cmd = import_camera('Import camera', 'icons/camera.png')
    cmd.install('Wizard', ' Import')
    cmd = import_camera('Import lighting', 'icons/lighting.png')
    cmd.install('Wizard', ' Import')
    cmd = update_all('Update all', 'icons/all.png')
    cmd.install('Wizard', ' Update')
    cmd = update_modeling('Update modeling', 'icons/modeling.png')
    cmd.install('Wizard', ' Update')
    cmd = update_grooming('Update grooming', 'icons/grooming.png')
    cmd.install('Wizard', ' Update')
    cmd = update_texturing('Update texturing', 'icons/texturing.png')
    cmd.install('Wizard', ' Update')
    cmd = update_shading('Update shading', 'icons/shading.png')
    cmd.install('Wizard', ' Update')
    cmd = update_custom('Update custom', 'icons/custom.png')
    cmd.install('Wizard', ' Update')
    cmd = update_layout('Update layout', 'icons/wlayout.png')
    cmd.install('Wizard', ' Update')
    cmd = update_animation('Update animation', 'icons/animation.png')
    cmd.install('Wizard', ' Update')
    cmd = update_cfx('Update cfx', 'icons/cfx.png')
    cmd.install('Wizard', ' Update')
    cmd = update_fx('Update fx', 'icons/fx.png')
    cmd.install('Wizard', ' Update')
    cmd = update_camera('Update camera', 'icons/camera.png')
    cmd.install('Wizard', ' Update')
    cmd = update_camera('Update lighting', 'icons/lighting.png')
    cmd.install('Wizard', ' Update')
    command.addseparator ('Wizard')
    cmd = set_image_format('Set image size', 'icons/set_image_size.png')
    cmd.install('Wizard')
    cmd = set_frame_rate('Set frame rate', 'icons/set_frame_rate.png')
    cmd.install('Wizard')
    cmd = set_frame_range('Set frame range', 'icons/set_frame_range.png')
    cmd.install('Wizard')
    cmd = set_frame_range_with_rolls('Set frame range with rolls', 'icons/set_frame_range.png')
    cmd.install('Wizard')
