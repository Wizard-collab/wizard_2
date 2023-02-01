# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import threading
import pyautogui
import random
import time
import logging
logger = logging.getLogger(__name__)
from PyQt5 import QtWidgets

# Wizard core modules
from wizard.core import game
from wizard.core import team_client
from wizard.core import environment
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_server


def execute_prank(signal_dic):
	if signal_dic['prank_type'] == 'mouse_prank':
		prank = mouse_prank()
		prank.set_duration(signal_dic['duration'])
		gui_server.custom_popup(f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, jiggly mouuuse !", ressources._potion_red_icon_)
		prank.start()
	elif signal_dic['prank_type'] == 'attack':
		gui_server.custom_popup(f"Mouahahah", f"You are attacked by {signal_dic['from_user']}, you loose {signal_dic['force']}% of life !", ressources._sword_icon_)
		attack(signal_dic['force'])
	elif signal_dic['prank_type'] == 'negative':
		gui_server.custom_popup(f"Mouahahah", f"You are poisonned by {signal_dic['from_user']}, good luck with the interface", ressources._potion_green_icon_)
		negative(signal_dic['duration'])

class mouse_prank(threading.Thread):
	def __init__(self):
		super(mouse_prank, self).__init__()
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

def attack(force=10):
	game.remove_life(force)
	gui_server.refresh_ui()

def negative(duration=2):
	app_instance = QtWidgets.QApplication.instance()
	with open('ressources/stylesheet_negative.css', 'r') as f:
        app_instance.setStyleSheet(f.read())

def send_mouse_prank(destination_user, duration=10):
	signal_dic = dict()
	signal_dic['prank_type'] = 'mouse_prank'
	signal_dic['duration'] = duration
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)

def send_attack_prank(destination_user, force=10):
	signal_dic = dict()
	signal_dic['prank_type'] = 'attack'
	signal_dic['force'] = force
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)

def send_negative_prank(destination_user, duration=100):
	signal_dic = dict()
	signal_dic['prank_type'] = 'negative'
	signal_dic['duration'] = duration
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)