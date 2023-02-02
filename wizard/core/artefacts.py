# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging
logger = logging.getLogger(__name__)

# Wizard core modules
from wizard.core import team_client
from wizard.core import environment
from wizard.core import repository
from wizard.vars import ressources
from wizard.vars import game_vars

def buy_artefact(artefact_name):
	if artefact_name not in game_vars.artefacts_dic.keys():
		return
	user_row = repository.get_user_row_by_name(environment.get_user())
	if 'coins' not in user_row.keys():
		return
	if game_vars.artefacts_dic[artefact_name]['price'] > user_row['coins']:
		logger.warning(f'Not enough coins to buy this artefact : {artefact_name}')
		return
	repository.modify_user_coins(environment.get_user(), user_row['coins']-game_vars.artefacts_dic[artefact_name]['price'])

def drink_heal_potion():
	repository.modify_user_life(environment.get_user(), 100)
	logger.info(f"You just drank a heal potion, your life is now full !")

def send_mouse_attack(destination_user, duration=10):
	signal_dic = dict()
	signal_dic['attack_type'] = 'mouse_attack'
	signal_dic['duration'] = duration
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)
	logger.info(f"{duration}s mouse attack sent to {destination_user}")

def send_life_attack(destination_user, force=10):
	signal_dic = dict()
	signal_dic['attack_type'] = 'life_attack'
	signal_dic['force'] = force
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)
	logger.info(f"{force}% life attack sent to {destination_user}")

def send_negative_attack(destination_user, duration=100):
	signal_dic = dict()
	signal_dic['attack_type'] = 'negative_attack'
	signal_dic['duration'] = duration
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)
	logger.info(f"{duration}s negative attack sent to {destination_user}")
