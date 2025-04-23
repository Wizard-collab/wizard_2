# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtCore
import win32api
import win32con
import ctypes
import pywintypes
import pyautogui
import rotatescreen
import random
import webbrowser
import subprocess
import time
import logging

# Wizard core modules
from wizard.vars import game_vars
from wizard.core import game

# Wizard gui modules
from wizard.gui import gui_server

logger = logging.getLogger(__name__)


class pranks():
    def __init__(self):
        self.pranks_dic = dict()

    def execute_attack(self, signal_dic):
        if 'mouse_attack' in signal_dic['attack_type']:
            time_id = time.time()
            self.pranks_dic[time_id] = mouse_attack()
            self.pranks_dic[time_id].set_duration(
                game_vars.artefacts_dic[signal_dic['attack_type']]['duration'])
            logger.info(
                f"You are poisonned by {signal_dic['from_user']}, jiggly mouuuse !")
            gui_server.custom_popup(
                f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, jiggly mouuuse !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            self.pranks_dic[time_id].start()
        elif 'life_attack' in signal_dic['attack_type']:
            logger.info(
                f"You are attacked by {signal_dic['from_user']}, you loose {game_vars.artefacts_dic[signal_dic['attack_type']]['force']}% of life !")
            gui_server.custom_popup(f"Mouahahah",
                                    f"You are attacked by {signal_dic['from_user']}, you loose {game_vars.artefacts_dic[signal_dic['attack_type']]['force']}% of life !",
                                    game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            life_attack(
                game_vars.artefacts_dic[signal_dic['attack_type']]['force'])
        elif 'resolution_attack' in signal_dic['attack_type']:
            logger.info(
                f"You are poisonned by {signal_dic['from_user']}, good luck with the interface")
            gui_server.custom_popup(
                f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, good luck with the interface", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            resolution_attack()
        elif 'rickroll_attack' in signal_dic['attack_type']:
            logger.info(f"You are rickrolled by {signal_dic['from_user']}")
            gui_server.custom_popup(
                f"Mouahahah", f"You are rickrolled by {signal_dic['from_user']}, enjoy !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            rickroll()
        elif 'lock_attack' in signal_dic['attack_type']:
            logger.info(
                f"Your session was locked by {signal_dic['from_user']}")
            gui_server.custom_popup(
                f"Mouahahah", f"Your session was locked by {signal_dic['from_user']}, see you soon !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            lock_workstation()
        elif 'flip_attack_1' in signal_dic['attack_type']:
            logger.info(
                f"Your screen was flipped by {signal_dic['from_user']}")
            gui_server.custom_popup(
                f"Mouahahah", f"Your screen was flipped by {signal_dic['from_user']}, try to turn your head !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            rotate_screen_once()
        elif 'flip_attack_2' in signal_dic['attack_type']:
            logger.info(
                f"Your screen is flipped by {signal_dic['from_user']} for 10s")
            gui_server.custom_popup(
                f"Mouahahah", f"Your screen is flipped by {signal_dic['from_user']} for 10 seconds, try to turn your head !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            time_id = time.time()
            self.pranks_dic[time_id] = flip_attack_2()
            self.pranks_dic[time_id].start()
        elif 'steal_attack_1' in signal_dic['attack_type']:
            logger.info(f"{signal_dic['from_user']} just stole you 1 level !")
            gui_server.custom_popup(
                f"Mouahahah", f"{signal_dic['from_user']} just stole you 1 level !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            gui_server.refresh_ui()
        elif 'steal_attack_2' in signal_dic['attack_type']:
            logger.info(
                f"{signal_dic['from_user']} just stole you some coins !")
            gui_server.custom_popup(
                f"Mouahahah", f"{signal_dic['from_user']} just stole you some coins !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            gui_server.refresh_ui()
        elif 'mouse_speed_attack' in signal_dic['attack_type']:
            logger.info(
                f"{signal_dic['from_user']} just modified the speed of your mouse, good luck !")
            gui_server.custom_popup(
                f"Mouahahah", f"{signal_dic['from_user']} just modified the speed of your mouse, good luck !", game_vars.artefacts_dic[signal_dic['attack_type']]['icon'])
            mouse_speed_attack()


class mouse_attack(QtCore.QThread):
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
            pyautogui.moveRel(rel_pos_x, rel_pos_y)  # ), duration = 0.01)
            time.sleep(0.02)


class flip_attack_2(QtCore.QThread):
    def __init__(self):
        super(flip_attack_2, self).__init__()
        self.duration = 30

    def run(self):
        start_pos = 0
        dis = rotatescreen.get_primary_display()
        for i in range(1, 10):
            pos = abs((start_pos - i*90) % 360)
            dis.rotate_to(pos)
            time.sleep(0.8)


def mouse_speed_attack():
    ctypes.windll.user32.SystemParametersInfoA(113, 0, 1, 0)


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
    cmd = 'rundll32.exe user32.dll, LockWorkStation'
    subprocess.call(cmd)


def rotate_screen_once():
    dis = rotatescreen.get_primary_display()
    dis.set_landscape_flipped()
