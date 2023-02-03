# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import win32api
import win32con
import pywintypes
import threading
import pyautogui
import rotatescreen
import random
import traceback
import webbrowser
import subprocess
import time
import logging
logger = logging.getLogger(__name__)
from PyQt5 import QtWidgets, QtCore

# Wizard core modules
from wizard.core import game
from wizard.core import team_client
from wizard.vars import ressources
from wizard.vars import game_vars

# Wizard gui modules
from wizard.gui import gui_server

def execute_attack(signal_dic):
    if 'mouse_attack' in signal_dic['attack_type']:
        prank = mouse_attack()
        prank.set_duration(game_vars.artefacts_dic[signal_dic['attack_type']]['duration'])
        logger.info(f"You are poisonned by {signal_dic['from_user']}, jiggly mouuuse !")
        gui_server.custom_popup(f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, jiggly mouuuse !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        prank.start()
    elif 'life_attack' in signal_dic['attack_type']:
        logger.info(f"You are attacked by {signal_dic['from_user']}, you loose {game_vars.artefacts_dic[signal_dic['attack_type']]['force']}% of life !")
        gui_server.custom_popup(f"Mouahahah",
                                f"You are attacked by {signal_dic['from_user']}, you loose {game_vars.artefacts_dic[signal_dic['attack_type']]['force']}% of life !",
                                game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        life_attack(game_vars.artefacts_dic[signal_dic['attack_type']]['force'])
    elif 'resolution_attack' in signal_dic['attack_type']:
        logger.info(f"You are poisonned by {signal_dic['from_user']}, good luck with the interface")
        gui_server.custom_popup(f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, good luck with the interface", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        resolution_attack()
    elif 'rickroll_attack' in signal_dic['attack_type']:
        logger.info(f"You are rickrolled by {signal_dic['from_user']}")
        gui_server.custom_popup(f"Mouahahah", f"You are rickrolled by {signal_dic['from_user']}, enjoy !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        rickroll()
    elif 'lock_attack' in signal_dic['attack_type']:
        logger.info(f"Your session was locked by {signal_dic['from_user']}")
        gui_server.custom_popup(f"Mouahahah", f"Your session was locked by {signal_dic['from_user']}, see you soon !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        lock_workstation()
    elif 'flip_attack_1' in signal_dic['attack_type']:
        logger.info(f"Your screen was flipped by {signal_dic['from_user']}")
        gui_server.custom_popup(f"Mouahahah", f"Your screen was flipped by {signal_dic['from_user']}, try to turn your head !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
        rotate_screen_once()


class mouse_attack(threading.Thread):
    def __init__(self):
        super(mouse_attack, self).__init__()
        self.duration = 10

    def set_duration(self, duration):
        self.duration = duration

    def run(self):
        start_time = time.time()
        while time.time() - self.duration < start_time:
            rel_pos_x = random.randint(-50, 50)
            rel_pos_y = random.randint(-50, 50)
            pyautogui.moveRel(rel_pos_x, rel_pos_y)#), duration = 0.01)
            time.sleep(0.02)

def life_attack(force=10):
    game.remove_life(force)
    gui_server.refresh_ui()

def resolution_attack():
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = 800
    devmode.PelsHeight = 600
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)

def rickroll():
    webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

def lock_workstation():
    cmd='rundll32.exe user32.dll, LockWorkStation'
    subprocess.call(cmd)

def rotate_screen_once():
    dis = rotatescreen.get_primary_display()
    dis.set_landscape_flipped()