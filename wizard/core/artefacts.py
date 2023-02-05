# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
import time
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
	current_artefacts = json.loads(user_row['artefacts'])
	current_artefacts.append(artefact_name)
	if not repository.modify_user_artefacts(environment.get_user(), current_artefacts):
		return
	repository.modify_user_coins(environment.get_user(), user_row['coins']-game_vars.artefacts_dic[artefact_name]['price'])
	return 1

def use_artefact(artefact_name, destination_user=None):
	if (destination_user == environment.get_user()) and game_vars.artefacts_dic[artefact_name]['usage'] == 'keep':
		keeped_artefacts_dic = json.loads(repository.get_user_row_by_name(environment.get_user(), 'keeped_artefacts'))
		if artefact_name in keeped_artefacts_dic.values():
			logger.warning(f"You can't cummulate {game_vars.artefacts_dic[artefact_name]['name']} !")
			return
		keeped_artefacts_dic[str(time.time())] = artefact_name
		repository.modify_keeped_artefacts(environment.get_user(), keeped_artefacts_dic)
	user_row = repository.get_user_row_by_name(environment.get_user())
	artefacts_list = json.loads(user_row['artefacts'])
	if artefact_name not in artefacts_list:
		logger.warning(f"You don't have this artefact : {artefact_name}")
		return
	artefact_index = artefacts_list.index(artefact_name)
	artefacts_list.pop(artefact_index)
	if not repository.modify_user_artefacts(environment.get_user(), artefacts_list):
		return
	if game_vars.artefacts_dic[artefact_name]['type'] == 'attack':
		if check_immunity(destination_user):
			return
		send_attack(destination_user, artefact_name)
	if 'heal' in artefact_name:
		heal(game_vars.artefacts_dic[artefact_name]['amount'])

def check_immunity(destination_user):
	destination_user_row = repository.get_user_row_by_name(destination_user)
	destination_user_keeped_artefacts = json.loads(destination_user_row['keeped_artefacts'])
	for time_id, keeped_artefact in destination_user_keeped_artefacts.items():
		if 'immunity' not in keeped_artefact:
			continue
		if time.time() > float(time_id) + game_vars.artefacts_dic[keeped_artefact]['duration']:
			continue
		logger.warning(f"Your attack just failed, {destination_user} has an immunity artefact !")
		return 1

def check_artefacts_expiration():
	user_row = repository.get_user_row_by_name(environment.get_user())
	user_keeped_artefacts = json.loads(user_row['keeped_artefacts'])
	time_ids = list(user_keeped_artefacts.keys())
	for time_id in time_ids:
		keeped_artefact = user_keeped_artefacts[time_id]
		if time.time() > float(time_id) + game_vars.artefacts_dic[keeped_artefact]['duration']:
			logger.info(f"{game_vars.artefacts_dic[keeped_artefact]['name']} is expired")
			del user_keeped_artefacts[time_id]
	repository.modify_keeped_artefacts(environment.get_user(), user_keeped_artefacts)

def heal(amount):
	if amount == 100:
		life = 100
	else:
		life = repository.get_user_row_by_name(environment.get_user(), 'life') + amount
		if life > 100:
			life = 100
	repository.modify_user_life(environment.get_user(), life)
	logger.info(f"You just drank a heal potion, your life is now at {life}% !")

def send_attack(destination_user, attack_name):
	signal_dic = dict()
	signal_dic['attack_type'] = attack_name
	signal_dic['from_user'] = environment.get_user()
	signal_dic['destination_user'] = destination_user
	team_client.send_prank(environment.get_team_dns(), signal_dic)
	logger.info(f"Attack sent to {destination_user}")
